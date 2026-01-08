import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')
TIMEFRAME = '15m'
# Queremos bajar suficientes datos. Binance permite 1000 por request.
# Vamos a intentar bajar 4000 velas (~1000 horas = 41 días)
CANDLES_LIMIT = 1000 
TOTAL_CHUNKS = 4 # 4 * 1000 = 4000 velas

SL = float(os.getenv('STOP_LOSS_PCT', 0.01))
TP = float(os.getenv('TAKE_PROFIT_PCT', 0.015))
TS = float(os.getenv('TRAILING_STOP_PCT', 0.005))  # Trailing Stop

# Parámetros de la estrategia (Triple Filtro)
RSI_THRESHOLD = 35  # RSI < 35 para comprar
EMA_LENGTH = 20     # EMA 20 (ajustado para datos limitados)

exchange = ccxt.binance()

def fetch_historical_data():
    print(f"⏳ Descargando datos históricos para {SYMBOL} ({TIMEFRAME})...")
    
    all_ohlcv = []
    # Fecha de inicio: Unas 4000 velas atrás aprox
    # 15 min * 4000 = 60000 min = 1000 horas = 41 días
    # timestamp en ms
    since = exchange.milliseconds() - (4000 * 15 * 60 * 1000)
    
    for i in range(TOTAL_CHUNKS):
        print(f"   📡 Bajando bloque {i+1}/{TOTAL_CHUNKS}...")
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=CANDLES_LIMIT, since=since)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            # Actualizamos 'since' para la siguiente petición (último tiempo + 1 vela)
            since = ohlcv[-1][0] + 1
            time.sleep(1) # Respetar rate limit
            
        except Exception as e:
            print(f"❌ Error descargando: {e}")
            break
            
    df = pd.DataFrame(all_ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
    df['datetime'] = pd.to_datetime(df['ts'], unit='ms')
    
    # Calcular Indicadores igual que en el bot
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # Bandas de Bollinger (20, 2)
    bbands = ta.bbands(df['close'], length=20, std=2)
    df = pd.concat([df, bbands], axis=1)
    
    # EMA para tendencia
    df['EMA'] = ta.ema(df['close'], length=EMA_LENGTH)
    
    return df

def run_backtest(df):
    print(f"\n🧪 Iniciando Backtest sobre {len(df)} velas...")
    print(f"   Desde: {df['datetime'].iloc[0]}")
    print(f"   Hasta: {df['datetime'].iloc[-1]}")
    
    saldo_inicial = 1000.0 # USDT
    saldo = saldo_inicial
    posicion = None # None o dict con precio_compra
    
    operaciones = []
    win_count = 0
    loss_count = 0
    
    for i in range(EMA_LENGTH + 20, len(df)):  # Necesitamos datos suficientes para EMA y BB
        row = df.iloc[i]
        precio = row['close']
        rsi = row['RSI']
        ts = row['datetime']
        
        # Buscar columna BBL (Lower Band)
        col_bbl = [c for c in df.columns if c.startswith('BBL')]
        if not col_bbl:
            continue
        lower_band = row[col_bbl[0]]
        ema = row['EMA']
        
        if posicion is None:
            # --- LÓGICA DE COMPRA (TRIPLE FILTRO) ---
            # 1. RSI < 35 (Sobreventa)
            # 2. Precio < Banda Bollinger Inferior (Cheap)
            # 3. Precio > EMA (Tendencia Alcista)
            if pd.notna(rsi) and pd.notna(lower_band) and pd.notna(ema):
                if rsi < RSI_THRESHOLD and precio < lower_band and precio > ema:
                    # Compramos
                    posicion = {
                        'precio': precio,
                        'fecha': ts,
                        'max_precio': precio  # Para Trailing Stop
                    }
        
        else:
            # --- LÓGICA DE VENTA ---
            precio_entrada = posicion['precio']
            max_precio = posicion['max_precio']
            
            # Actualizar máximo precio (Trailing Stop)
            if precio > max_precio:
                max_precio = precio
                posicion['max_precio'] = max_precio
            
            # Calcular precio de salida del Trailing Stop
            precio_trailing = max_precio * (1 - TS)
            
            # 1. Trailing Stop (prioridad)
            if precio <= precio_trailing:
                pnl = (precio - precio_entrada) / precio_entrada
                resultado = saldo * pnl
                saldo += resultado
                
                operaciones.append({'tipo': 'TRAILING STOP', 'pnl_pct': pnl, 'fecha': ts})
                if pnl > 0:
                    win_count += 1
                else:
                    loss_count += 1
                posicion = None
                
            # 2. Take Profit
            elif precio >= precio_entrada * (1 + TP):
                pnl = (precio - precio_entrada) / precio_entrada
                resultado = saldo * pnl
                saldo += resultado
                
                operaciones.append({'tipo': 'TP', 'pnl_pct': pnl, 'fecha': ts})
                win_count += 1
                posicion = None

    # Resultados Finales
    print("\n📊 --- RESULTADOS DEL BACKTEST ---")
    print(f"💰 Saldo Inicial: ${saldo_inicial:.2f}")
    print(f"💰 Saldo Final:   ${saldo:.2f}")
    total_ops = win_count + loss_count
    rentabilidad = ((saldo - saldo_inicial) / saldo_inicial) * 100
    
    color = "🟢" if rentabilidad > 0 else "🔴"
    print(f"{color} Rentabilidad: {rentabilidad:.2f}%")
    print(f"🔄 Operaciones Totales: {total_ops}")
    if total_ops > 0:
        print(f"✅ Ganadas: {win_count} ({(win_count/total_ops)*100:.1f}%)")
        print(f"❌ Perdidas: {loss_count} ({(loss_count/total_ops)*100:.1f}%)")

if __name__ == "__main__":
    df = fetch_historical_data()
    if not df.empty:
        run_backtest(df)
