import pandas as pd
import pandas_ta as ta
import ccxt
import os
from dotenv import load_dotenv

# Cargar datos una sola vez para no spammear a Binance
load_dotenv()
SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')

def get_data():
    exchange = ccxt.binance()
    print("⏳ Descargando datos para optimización...")
    all_ohlcv = []
    since = exchange.milliseconds() - (4000 * 15 * 60 * 1000)
    for _ in range(4):
        ohlcv = exchange.fetch_ohlcv(SYMBOL, '15m', limit=1000, since=since)
        if not ohlcv: break
        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + 1
        
    df = pd.DataFrame(all_ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
    df['datetime'] = pd.to_datetime(df['ts'], unit='ms')
    df['RSI'] = ta.rsi(df['close'], length=14)
    return df

def test_strategy(df, sl_pct, tp_pct, rsi_buy_limit):
    saldo = 1000.0
    posicion = None
    wins = 0
    losses = 0
    
    for i in range(14, len(df)):
        price = df.iloc[i]['close']
        rsi = df.iloc[i]['RSI']
        
        if posicion is None:
            if rsi < rsi_buy_limit:
                posicion = price
        else:
            # Check Exit
            if price <= posicion * (1 - sl_pct): # Stop Loss
                saldo = saldo * (1 + ((price - posicion)/posicion))
                posicion = None
                losses += 1
            elif price >= posicion * (1 + tp_pct): # Take Profit
                saldo = saldo * (1 + ((price - posicion)/posicion))
                posicion = None
                wins += 1
                
    return saldo, wins, losses

if __name__ == "__main__":
    df = get_data()
    
    # Lista de configuraciones a probar
    configs = [
        {"name": "Actual (Conservador)", "sl": 0.02, "tp": 0.04, "rsi": 30},
        {"name": "Agresivo (Largo Plazo)", "sl": 0.05, "tp": 0.10, "rsi": 30}, # SL 5%, TP 10%
        {"name": "Scalping (Rápido)",      "sl": 0.01, "tp": 0.015, "rsi": 35}, # SL 1%, TP 1.5%, RSI < 35 (entra más fácil)
        {"name": "Francotirador (Paciencia)", "sl": 0.03, "tp": 0.06, "rsi": 25}, # RSI < 25 (solo caídas fuertes)
    ]
    
    print("\n🏆 --- TORNEO DE ESTRATEGIAS (Saldo Inicial $1000) ---")
    print(f"{'Estrategia':<25} | {'Saldo Final':<12} | {'Rentab.':<8} | {'Win Rate'}")
    print("-" * 65)
    
    best_config = None
    best_result = 0
    
    for cfg in configs:
        final_balance, w, l = test_strategy(df, cfg['sl'], cfg['tp'], cfg['rsi'])
        rentabilidad = ((final_balance - 1000) / 1000) * 100
        total = w + l
        wr = (w/total*100) if total > 0 else 0
        
        print(f"{cfg['name']:<25} | ${final_balance:,.2f}   | {rentabilidad:+.2f}%   | {wr:.1f}% ({w}/{total})")
        
        if final_balance > best_result:
            best_result = final_balance
            best_config = cfg

    print(f"\n🌟 GANADOR: {best_config['name']}")
    print(f"   Configurar: SL={best_config['sl']*100}%, TP={best_config['tp']*100}%, RSI<{best_config['rsi']}")
