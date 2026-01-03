import os
import time
import datetime
import ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv
from notificaciones import enviar_telegram 
from memoria import cargar_estado, guardar_estado

# 1. Configuración Inicial
load_dotenv()

# Configuración del Exchange (Binance por defecto)
# Se usa 'enableRateLimit': True para respetar los límites de la API
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'} 
})

# Si estamos en modo TESTNET (Sandbox), descomentar las siguientes líneas si el exchange lo soporta
# exchange.set_sandbox_mode(True) 

SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')
# Parsear porcentajes (0.02 = 2%)
SL = float(os.getenv('STOP_LOSS_PCT', 0.01))
TP = float(os.getenv('TAKE_PROFIT_PCT', 0.015))
TS = float(os.getenv('TRAILING_STOP_PCT', 0.005)) # 0.5% Trailing
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'True').lower() == 'true'

estado = cargar_estado()
ultima_vez_vivo = datetime.datetime.now()
ultimo_reporte_dia = datetime.datetime.now().day

def verificar_reporte_diario():
    global ultimo_reporte_dia
    ahora = datetime.datetime.now()
    
    # Si cambió de día y son las 8:00 AM (o después)
    if ahora.day != ultimo_reporte_dia and ahora.hour >= 8:
        ops = estado.get("operaciones_hoy", 0)
        pnl = estado.get("pnl_acumulado", 0.0)
        saldo_simulado = 1000 * (1 + pnl/100) # Estimado
        
        msg = f"""📅 **REPORTE DIARIO ARGOS**
-------------------------
🔢 Operaciones: {ops}
💰 PnL del Día: {pnl:+.2f}%
💵 Capital Est.: ${saldo_simulado:.2f}
-------------------------"""
        enviar_telegram(msg)
        
        # Resetear contadores
        estado["operaciones_hoy"] = 0
        estado["pnl_acumulado"] = 0.0
        guardar_estado(estado)
        
        ultimo_reporte_dia = ahora.day

def registrar_operacion(tipo, precio_venta, pnl_pct):
    # Actualizar Stats
    estado["operaciones_hoy"] = estado.get("operaciones_hoy", 0) + 1
    estado["pnl_acumulado"] = estado.get("pnl_acumulado", 0.0) + (pnl_pct * 100)
    
    # Cerrar Posición
    estado["posicion_abierta"] = False
    estado["max_precio"] = 0.0
    guardar_estado(estado)

    # Mensaje Telegram
    icono = "✅" if pnl_pct > 0 else "❌"
    enviar_telegram(f"{icono} **{tipo} EJECUTADO**\nVenta: {precio_venta}\nResultado: {pnl_pct*100:.2f}%")


def obtener_datos():
    """
    Obtiene las velas y calcula indicadores.
    """
    try:
        # Fetch OHLCV (Open, High, Low, Close, Volume)
        velas = exchange.fetch_ohlcv(SYMBOL, timeframe='15m', limit=100)
        df = pd.DataFrame(velas, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        
        # Calcular RSI usando pandas_ta
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # Calcular Bandas de Bollinger (Periodo 20, Desviación 2)
        # Esto genera columnas: BBL_20_2.0 (Lower), BBM... (Mid), BBU... (Upper)
        bbands = ta.bbands(df['close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        
        return df
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return pd.DataFrame()

# 2. Loop Principal
print(f"--- 🤖 ARGOS BOT INICIADO PARA {SYMBOL} ---")
modo_msg = "🔹 MODO SIMULACIÓN (PAPER TRADING)" if SIMULATION_MODE else "🔸 MODO REAL (DINERO REAL)"
print(modo_msg)
enviar_telegram(f"🤖 **Argos Bot Iniciado**\n{modo_msg}\nPar: {SYMBOL}\nEstrategia: RSI + Bollinger + Trailing ({TS*100}%)")

while True:
    try:
        verificar_reporte_diario()
        
        # Heartbeat cada 12 horas (43200 segundos)
        ahora = datetime.datetime.now()
        if (ahora - ultima_vez_vivo).total_seconds() >= 43200:
            enviar_telegram(f"💓 **Heartbeat:** El bot sigue activo. Precio: {estado.get('precio_compra', 'N/A')}")
            ultima_vez_vivo = ahora

        df = obtener_datos()
        
        if df.empty:
            time.sleep(10)
            continue

        precio_actual = df['close'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]
        
        # Obtenemos la Banda Inferior (Lower Band)
        # pandas_ta nombra la col: BBL_length_std
        lower_band = df['BBL_20_2.0'].iloc[-1]

        # Log de consola (para debug ver que sigue vivo)
        status_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] P: {precio_actual:.2f} | RSI: {rsi_actual:.2f} | BBL: {lower_band:.2f} | Pos: {estado['posicion_abierta']}"
        print(status_msg)

        if not estado["posicion_abierta"]:
            # --- LÓGICA DE ENTRADA (COMPRA) ---
            # FILTRO DOBLE: RSI < 35 Y Precio < Banda Inferior
            if rsi_actual < 35 and precio_actual < lower_band:
                print(f"🚀 SEÑAL CONFIRMADA: RSI {rsi_actual:.2f} y Precio < Bollinger")
                
                if not SIMULATION_MODE:
                    # order = exchange.create_market_buy_order(SYMBOL, cantidad)
                    pass # Descomentar para producción real
                
                # Simulamos la compra guardando el estado
                estado.update({
                    "posicion_abierta": True, 
                    "precio_compra": precio_actual,
                    "max_precio": precio_actual, # Inicializamos el max_precio
                    "fecha_compra": str(datetime.datetime.now())
                })
                guardar_estado(estado)
                
                enviar_telegram(f"🚀 **COMPRA EJECUTADA ({'SIMULADA' if SIMULATION_MODE else 'REAL'})**\nPrecio: {precio_actual}\nRSI: {rsi_actual:.2f}\nBanda Bool: {lower_band:.2f}")
        
        else:
            # --- LÓGICA DE SALIDA (VENTA) ---
            precio_entrada = estado["precio_compra"]
            max_precio_historico = estado.get("max_precio", precio_entrada)
            
            # Actualizamos el Trailing (Precio Máximo visto)
            if precio_actual > max_precio_historico:
                max_precio_historico = precio_actual
                estado["max_precio"] = max_precio_historico
                guardar_estado(estado)
                # print(f"📈 Nuevo máximo alcanzado: {max_precio_historico}")

            # Calculamos el precio de salida dinámica (Trailing Stop)
            precio_salida_trailing = max_precio_historico * (1 - TS)

            # 1. Verificar TRAILING STOP
            if precio_actual <= precio_salida_trailing:
                pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                print(f"📉 TRAILING STOP DISPARADO")
                if not SIMULATION_MODE: pass 
                registrar_operacion("TRAILING STOP", precio_actual, pnl_pct)
            
            # 2. Verificar TAKE PROFIT
            elif precio_actual >= precio_entrada * (1 + TP):
                print(f"✅ TAKE PROFIT EJECUTADO")
                if not SIMULATION_MODE: pass 
                pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                registrar_operacion("TAKE PROFIT", precio_actual, pnl_pct)
            
            # 3. Stop Loss de Emergencia
            elif precio_actual <= precio_entrada * (1 - SL):
                 print(f"❌ STOP LOSS DE EMERGENCIA")
                 if not SIMULATION_MODE: pass
                 pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                 registrar_operacion("STOP LOSS (EMERGENCIA)", precio_actual, pnl_pct)
            
            # 3. (Opcional) Salida por RSI alto (si el usuario quisiera vender por RSI > 70 también)
            # elif rsi_actual > 70: ...

    except Exception as e:
        print(f"❌ Error en bucle principal: {e}")
        time.sleep(30) # Esperar antes de reintentar si falla algo grave
    
    # Revisar cada 60 segundos
    time.sleep(60) 
