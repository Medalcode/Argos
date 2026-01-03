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
SL = float(os.getenv('STOP_LOSS_PCT', 0.02))
TP = float(os.getenv('TAKE_PROFIT_PCT', 0.04))

estado = cargar_estado()
ultima_vez_vivo = datetime.datetime.now()

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
        return df
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return pd.DataFrame()

# 2. Loop Principal
print(f"--- 🤖 ARGOS BOT INICIADO PARA {SYMBOL} ---")
enviar_telegram(f"🤖 **Argos Bot Iniciado**\nPar: {SYMBOL}\nEstrategia: RSI + StopLoss ({SL*100}%) / TakeProfit ({TP*100}%)")

while True:
    try:
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

        # Log de consola (para debug ver que sigue vivo)
        status_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] P: {precio_actual:.2f} | RSI: {rsi_actual:.2f} | Pos: {estado['posicion_abierta']}"
        print(status_msg)

        if not estado["posicion_abierta"]:
            # --- LÓGICA DE ENTRADA (COMPRA) ---
            if rsi_actual < 30:
                print(f"🚀 SEÑAL DE COMPRA DETECTADA (RSI {rsi_actual:.2f})")
                
                # NOTA: Aquí iría la orden real: 
                # order = exchange.create_market_buy_order(SYMBOL, cantidad)
                
                # Simulamos la compra guardando el estado
                estado.update({
                    "posicion_abierta": True, 
                    "precio_compra": precio_actual,
                    "fecha_compra": str(datetime.datetime.now())
                })
                guardar_estado(estado)
                
                enviar_telegram(f"🚀 **COMPRA EJECUTADA**\nPrecio: {precio_actual}\nRSI: {rsi_actual:.2f}")
        
        else:
            # --- LÓGICA DE SALIDA (VENTA) ---
            precio_entrada = estado["precio_compra"]
            
            # 1. Verificar STOP LOSS
            if precio_actual <= precio_entrada * (1 - SL):
                print(f"❌ STOP LOSS EJECUTADO")
                
                # order = exchange.create_market_sell_order(SYMBOL, cantidad)
                
                enviar_telegram(f"❌ **STOP LOSS ACTIVADO**\nVenta a: {precio_actual}\nPérdida: -{SL*100}%")
                
                estado["posicion_abierta"] = False
                guardar_estado(estado)
            
            # 2. Verificar TAKE PROFIT
            elif precio_actual >= precio_entrada * (1 + TP):
                print(f"✅ TAKE PROFIT EJECUTADO")
                
                # order = exchange.create_market_sell_order(SYMBOL, cantidad)
                
                enviar_telegram(f"✅ **TAKE PROFIT ALCANZADO**\nVenta a: {precio_actual}\nGanancia: +{TP*100}%")
                
                estado["posicion_abierta"] = False
                guardar_estado(estado)
            
            # 3. (Opcional) Salida por RSI alto (si el usuario quisiera vender por RSI > 70 también)
            # elif rsi_actual > 70: ...

    except Exception as e:
        print(f"❌ Error en bucle principal: {e}")
        time.sleep(30) # Esperar antes de reintentar si falla algo grave
    
    # Revisar cada 60 segundos
    time.sleep(60) 
