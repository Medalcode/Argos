import pandas as pd
import pandas_ta as ta
import ccxt
import time
import os
from dotenv import load_dotenv
import itertools
import multiprocessing
from datetime import datetime

# Cargar configuración
load_dotenv()
SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')

# --- CONFIGURACIÓN DE LA BÚSQUEDA ---
# Rangos de parámetros a probar
RSI_RANGE = range(20, 45, 5)        # 20, 25, 30, 35, 40
SL_RANGE = [0.01, 0.02, 0.03, 0.05, 0.07]  # 1% a 7%
TP_RANGE = [0.02, 0.04, 0.06, 0.10, 0.15]  # 2% a 15%
TRAILING_RANGE = [0.005, 0.01, 0.02] # 0.5% a 2%

RISK_FREE_RATE = 0.0  # Para Sharpe Ratio

def get_data():
    """Descarga datos históricos de Binance para optimización"""
    exchange = ccxt.binance()
    print(f"⏳ Descargando datos históricos para {SYMBOL}...")
    
    all_ohlcv = []
    # 4000 velas * 15m = ~41 días
    since = exchange.milliseconds() - (4000 * 15 * 60 * 1000)
    
    for _ in range(4):
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, '15m', limit=1000, since=since)
            if not ohlcv: break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Error descargando datos: {e}")
            break
            
    df = pd.DataFrame(all_ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
    df['datetime'] = pd.to_datetime(df['ts'], unit='ms')
    
    # Calcular indicadores base
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA_20'] = ta.ema(df['close'], length=20)
    
    # Bandas de Bollinger (usamos bb_lower)
    bb = ta.bbands(df['close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1)
    # Renombrar columna BBL para consistencia
    bbl_col = [c for c in df.columns if c.startswith('BBL')][0]
    df['BB_LOWER'] = df[bbl_col]
    
    # Limpiar NaN iniciales
    df.dropna(inplace=True)
    return df

def backtest_strategy(args):
    """
    Ejecuta el backtest para una combinación específica de parámetros.
    Esta función debe ser estática/aislada para multiprocessing.
    """
    df, params = args
    rsi_limit, sl, tp, trailing = params
    
    saldo_inicial = 1000.0
    saldo = saldo_inicial
    posicion = None # {precio, max_price}
    
    wins = 0
    losses = 0
    trades = 0
    returns = [] # Lista de retornos % para Sharpe
    
    # Convertir DataFrame a lista de dicts es mucho más rápido para iterar
    records = df.to_dict('records')
    
    for row in records:
        price = row['close']
        
        if posicion is None:
            # --- Lógica de Compra ---
            # Triple Filtro: RSI + Bollinger + EMA
            if (row['RSI'] < rsi_limit and 
                price < row['BB_LOWER'] and 
                price > row['EMA_20']):
                
                posicion = {
                    'precio': price,
                    'max_price': price
                }
        else:
            # --- Lógica de Venta ---
            precio_entrada = posicion['precio']
            
            # Actualizar Trailing Stop
            if price > posicion['max_price']:
                posicion['max_price'] = price
            
            stop_price = posicion['max_price'] * (1 - trailing)
            
            # 1. Verificar Stop Loss / Trailing Stop
            # Stop Loss fijo (SL) es un "stop de emergencia" basado en precio de entrada
            sl_price = precio_entrada * (1 - sl)
            
            exit_price = None
            reason = None
            
            if price <= stop_price:
                exit_price = stop_price if price > stop_price else price # Simulamos ejecucion
                reason = "Trailing"
            elif price <= sl_price:
                exit_price = sl_price if price > sl_price else price
                reason = "SL"
            elif price >= precio_entrada * (1 + tp):
                exit_price = precio_entrada * (1 + tp) # Limit order assumption
                reason = "TP"
                
            if exit_price:
                pnl = (exit_price - precio_entrada) / precio_entrada
                pnl_usd = saldo * pnl
                saldo += pnl_usd
                
                returns.append(pnl)
                trades += 1
                if pnl > 0: wins += 1
                else: losses += 1
                
                posicion = None

    # Métricas Finales
    total_return = (saldo - saldo_inicial) / saldo_inicial
    win_rate = (wins / trades * 100) if trades > 0 else 0
    
    # Sharpe Ratio Simplificado (basado en trades, no en tiempo)
    sharpe = 0
    if len(returns) > 1:
        s_returns = pd.Series(returns)
        std = s_returns.std()
        if std > 0:
            sharpe = (s_returns.mean() / std) * (len(returns)**0.5)

    return {
        'RSI': rsi_limit,
        'SL': sl,
        'TP': tp,
        'Trailing': trailing,
        'Saldo Final': saldo,
        'Retorno %': total_return * 100,
        'Trades': trades,
        'Win Rate': win_rate,
        'Sharpe': sharpe
    }

def run_optimization():
    # 1. Obtener Datos
    df = get_data()
    print(f"✅ Datos cargados: {len(df)} velas.")
    
    # 2. Generar Combinaciones
    combinations = list(itertools.product(RSI_RANGE, SL_RANGE, TP_RANGE, TRAILING_RANGE))
    print(f"🚀 Iniciando optimización de {len(combinations)} estrategias...")
    print(f"cpu_count: {multiprocessing.cpu_count()}")
    
    # 3. Multiprocessing
    start_time = time.time()
    
    # Preparamos argumentos (df debe pasarse a cada proceso)
    # Nota: En sistemas reales con Big Data esto se hace diferente (shared memory),
    # pero para 4000 velas copiar el DF es despreciable.
    args = [(df, params) for params in combinations]
    
    with multiprocessing.Pool() as pool:
        results = pool.map(backtest_strategy, args)
        
    elapsed_time = time.time() - start_time
    
    # 4. Análisis de Resultados
    results_df = pd.DataFrame(results)
    
    # Ordenar por Sharpe Ratio (mejor balance riesgo/beneficio)
    best_results = results_df.sort_values(by='Sharpe', ascending=False).head(10)
    
    print(f"\n🏁 Optimización completada en {elapsed_time:.2f} segundos.")
    print("\n🏆 TOP 10 ESTRATEGIAS (Ordenadas por Sharpe Ratio):")
    print("-" * 100)
    print(best_results.to_markdown(index=False, floatfmt=".2f"))
    
    # Guardar todo
    filename = f"optimization_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    results_df.to_csv(filename, index=False)
    print(f"\n💾 Todos los resultados guardados en: {filename}")
    
    # Recomendación Final
    winner = best_results.iloc[0]
    print("\n🌟 RECOMENDACIÓN FINAL 🌟")
    print(f"Configura tu .env con:")
    print(f"RSI_THRESHOLD={int(winner['RSI'])}")
    print(f"STOP_LOSS_PCT={winner['SL']:.3f}  # {winner['SL']*100}%")
    print(f"TAKE_PROFIT_PCT={winner['TP']:.3f}  # {winner['TP']*100}%")
    print(f"TRAILING_STOP_PCT={winner['Trailing']:.3f}  # {winner['Trailing']*100}%")

if __name__ == "__main__":
    # Fix para multiprocessing en Windows/macOS (safe spawn)
    multiprocessing.freeze_support()
    run_optimization()
