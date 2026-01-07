import os
import time
import requests
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
# Parsear porcentajes
SL = float(os.getenv('STOP_LOSS_PCT', 0.01))
TP = float(os.getenv('TAKE_PROFIT_PCT', 0.015))
TS = float(os.getenv('TRAILING_STOP_PCT', 0.005))
POS_SIZE = float(os.getenv('POSITION_SIZE_PCT', 0.95)) # 95% del saldo
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

# Archivo para guardar historial
TRADES_FILE = "trades.csv"

def guardar_trade_csv(fecha, tipo, precio, resultado_pct):
    existe = os.path.isfile(TRADES_FILE)
    with open(TRADES_FILE, 'a') as f:
        # Header si es nuevo
        if not existe:
            f.write("fecha,tipo,precio,resultado_pct,ganancia_usd_estimada\n")
        
        # Asumiendo capital 1000 usd
        ganancia_usd = 1000 * resultado_pct
        f.write(f"{fecha},{tipo},{precio},{resultado_pct:.4f},{ganancia_usd:.2f}\n")

def registrar_operacion(tipo, precio_venta, pnl_pct):
    # Actualizar Stats en Memoria
    estado["operaciones_hoy"] = estado.get("operaciones_hoy", 0) + 1
    estado["pnl_acumulado"] = estado.get("pnl_acumulado", 0.0) + (pnl_pct * 100)
    
    # Guardar en CSV
    guardar_trade_csv(datetime.datetime.now(), tipo, precio_venta, pnl_pct)

    # Cerrar Posición
    estado["posicion_abierta"] = False
    estado["max_precio"] = 0.0
    guardar_estado(estado)

    # Mensaje Telegram
    icono = "✅" if pnl_pct > 0 else "❌"
    enviar_telegram(f"{icono} **{tipo} EJECUTADO**\nVenta: {precio_venta}\nResultado: {pnl_pct*100:.2f}%")


def check_balance():
    """
    Verifica si tenemos suficiente USDT en la billetera SPOT para operar.
    Retorna True si hay > 15 USDT (mínimo de seguridad).
    """
    try:
        balance = exchange.fetch_balance()
        usdt_free = balance.get('USDT', {}).get('free', 0.0)
        
        if usdt_free < 15: # Binance suele pedir min $10, ponemos $15 por seguridad
            print(f"⚠️ Saldo insuficiente: ${usdt_free:.2f} USDT")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error verificando saldo: {e}")
        return False # Ante la duda, no operar

def obtener_datos():
    """
    Obtiene las velas y calcula indicadores.
    """
    try:
        # Fetch OHLCV (Necesitamos más historia para la EMA 200)
        # 15m * 300 velas = 75 horas (Suficiente para EMA 200)
        velas = exchange.fetch_ohlcv(SYMBOL, timeframe='15m', limit=300)
        df = pd.DataFrame(velas, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        
        # Calcular RSI 14
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # Calcular Bollinger (20, 2)
        bbands = ta.bbands(df['close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        
        # Calcular EMA 200 (Tendencia de largo plazo)
        df['EMA_200'] = ta.ema(df['close'], length=200)
        
        return df
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return pd.DataFrame()

# Variable para no repetir comandos viejos
ultimo_update_id = 0

def procesar_comandos(df_actual):
    global ultimo_update_id
    token = os.getenv('TELEGRAM_TOKEN')
    if not token: return

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {'offset': ultimo_update_id + 1, 'timeout': 1}
    
    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        
        if not data.get('ok'): return
        
        for result in data.get('result', []):
            update_id = result['update_id']
            ultimo_update_id = update_id # Actualizamos para no leerlo de nuevo
            
            message = result.get('message', {})
            texto = message.get('text', '').lower().strip()
            
            if not texto: continue
            
            # --- COMANDO /STATUS ---
            if texto == '/status':
                precio = df_actual['close'].iloc[-1] if not df_actual.empty else 0
                rsi = df_actual['RSI'].iloc[-1] if not df_actual.empty else 0
                pos = "Abierta ✅" if estado["posicion_abierta"] else "Esperando 💤"
                tendencia = "ALCISTA 🐂" if not df_actual.empty and precio > df_actual['EMA_200'].iloc[-1] else "BAJISTA 🐻"
                
                msg = f"""📊 **STATUS ARGOS**
Precio: {precio}
RSI: {rsi:.2f}
Tendencia: {tendencia}
Posición: {pos}
PNL Acum: {estado.get('pnl_acumulado',0):.2f}%"""
                enviar_telegram(msg)

            # --- COMANDO /SALDO ---
            elif texto == '/saldo':
                pnl = estado.get("pnl_acumulado", 0.0)
                saldo_est = 1000 * (1 + pnl/100)
                enviar_telegram(f"💵 **Saldo Estimado:** ${saldo_est:.2f}\nPnL Acumulado: {pnl:.2f}%")

            # --- COMANDO /VENDER (PÁNICO) ---
            elif texto == '/vender':
                if estado["posicion_abierta"]:
                    precio = df_actual['close'].iloc[-1]
                    precio_compra = estado["precio_compra"]
                    pnl_pct = (precio - precio_compra) / precio_compra
                    
                    registrar_operacion("VENTA MANUAL (PÁNICO)", precio, pnl_pct)
                    enviar_telegram("🚨 **VENTA FORZADA EJECUTADA**")
                else:
                    enviar_telegram("⚠️ No hay posición abierta para vender.")
                    
    except Exception as e:
        print(f"Error procesando comandos: {e}")

# 2. Loop Principal
print(f"--- 🤖 ARGOS BOT INICIADO PARA {SYMBOL} ---")
modo_msg = "🔹 MODO SIMULACIÓN (PAPER TRADING)" if SIMULATION_MODE else "🔸 MODO REAL (DINERO REAL)"
print(modo_msg)
enviar_telegram(f"🤖 **Argos Bot Iniciado**\n{modo_msg}\nPar: {SYMBOL}\nEstrategia: RSI + Bollinger + EMA200 + Trailing")

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
            
        # Asegurarnos de tener suficientes datos para EMA 200
        if pd.isna(df['EMA_200'].iloc[-1]):
            print("⏳ Calculando EMA 200 (recopilando datos)...")
            time.sleep(10)
            continue
            
        # PROCESAR COMANDOS DE TELEGRAM
        procesar_comandos(df)

        precio_actual = df['close'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]
        
        # Búsqueda inteligente de la columna BBL (Lower Band)
        # A veces panda_ta la llama BBL_20_2.0, otras veces diferente
        col_bbl = [c for c in df.columns if c.startswith('BBL')][0]
        lower_band = df[col_bbl].iloc[-1]
        
        ema_200 = df['EMA_200'].iloc[-1]

        # Log de consola
        tendencia = "ALCISTA 🐂" if precio_actual > ema_200 else "BAJISTA 🐻"
        status_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] P: {precio_actual:.2f} | RSI: {rsi_actual:.2f} | Tendencia: {tendencia} | Pos: {estado['posicion_abierta']}"
        print(status_msg)

        if not estado["posicion_abierta"]:
            # --- LÓGICA DE ENTRADA (COMPRA) ---
            # FILTRO TRIPLE: 
            # 1. RSI < 35 (Oversold)
            # 2. Precio < Banda Bollinger Inferior (Cheap)
            # 3. Precio > EMA 200 (Trend is Up - Solo compramos correcciones en subida)
            
            condicion_rsi = rsi_actual < 35
            condicion_bb = precio_actual < lower_band
            condicion_ema = precio_actual > ema_200
            if condicion_rsi and condicion_bb and condicion_ema:
                print(f"🚀 SEÑAL PERFECTA CONFIRMADA")
                
                # --- VERIFICACIÓN DE SEGURIDAD ANTES DE DISPARAR ---
                # Validamos saldo solo si vamos a operar de verdad
                if not SIMULATION_MODE and not check_balance():
                     enviar_telegram("⚠️ **SEÑAL OMITIDA**: Saldo insuficiente en Binance (<$15 USDT).")
                cantidad_compra = 0.0
                
                if not SIMULATION_MODE:
                    try:
                        # 1. Obtener Saldo Libre
                        balance = exchange.fetch_balance()
                        usdt_free = balance.get('USDT', {}).get('free', 0.0)
                        
                        # VERIFICAR SI HAY SUFICIENTE SALDO
                        if usdt_free < 15:
                             enviar_telegram("⚠️ **SEÑAL OMITIDA**: Saldo insuficiente (< $15 USD).")
                             time.sleep(60)
                             continue

                        # 2. Calcular cuánto gastar (Ej. 95% de 100 USDT = 95 USD)
                        gasto_usdt = usdt_free * POS_SIZE
                        
                        # 3. Calcular cantidad de BTC (95 / 90000 = 0.00105 BTC)
                        cantidad_bruta = gasto_usdt / precio_actual
                        
                        # 4. Ajustar decimales según reglas de Binance (PRECISIÓN)
                        cantidad_compra = exchange.amount_to_precision(SYMBOL, cantidad_bruta)
                        
                        print(f"💰 Comprando {cantidad_compra} {SYMBOL.split('/')[0]} con ${gasto_usdt:.2f} USDT")
                        
                        # 5. Ejecutar Orden
                        # order = exchange.create_market_buy_order(SYMBOL, cantidad_compra)
                        # precio_real_ejecucion = order['price'] # Usamos el precio real del exchange
                        
                    except Exception as e:
                        print(f"❌ Error calculando tamaño posición: {e}")
                        enviar_telegram(f"❌ Error al intentar comprar: {e}")
                        continue
                else:
                    # En simulación, asumimos 0.01 BTC como referencia
                    cantidad_compra = 0.01 

                # Guardar estado
                estado.update({
                    "posicion_abierta": True, 
                    "precio_compra": precio_actual, # Si fuera real usariamos precio_real_ejecucion
                    "cantidad": cantidad_compra,
                    "max_precio": precio_actual, 
                    "fecha_compra": str(datetime.datetime.now())
                })
                guardar_estado(estado)
                guardar_trade_csv(datetime.datetime.now(), "COMPRA", precio_actual, 0)
                
                enviar_telegram(f"🚀 **COMPRA EJECUTADA**\nPrecio: {precio_actual}\nCant: {cantidad_compra}\nRSI: {rsi_actual:.2f}\nEMA200: {ema_200:.2f}")
    
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
