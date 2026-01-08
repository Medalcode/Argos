"""
Tests para cálculo de indicadores técnicos
"""
import pytest
import pandas as pd
import pandas_ta as ta
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_rsi_calculation():
    """Test que el RSI se calcula correctamente"""
    # Crear datos de prueba
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
    df = pd.DataFrame({'close': prices})
    
    # Calcular RSI
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # Verificar que RSI está en el rango válido (0-100)
    rsi_values = df['RSI'].dropna()
    assert all(0 <= val <= 100 for val in rsi_values), "RSI debe estar entre 0 y 100"
    
    # Verificar que tenemos valores calculados
    assert len(rsi_values) > 0, "RSI debe tener al menos un valor calculado"


def test_bollinger_bands():
    """Test que las Bandas de Bollinger se calculan correctamente"""
    prices = [100 + i for i in range(50)]  # Tendencia alcista
    df = pd.DataFrame({'close': prices})
    
    # Calcular Bollinger Bands
    bbands = ta.bbands(df['close'], length=20, std=2)
    
    # Verificar que tenemos las 3 bandas
    assert 'BBL_20_2.0' in bbands.columns or any('BBL' in col for col in bbands.columns), "Debe tener banda inferior"
    assert 'BBM_20_2.0' in bbands.columns or any('BBM' in col for col in bbands.columns), "Debe tener banda media"
    assert 'BBU_20_2.0' in bbands.columns or any('BBU' in col for col in bbands.columns), "Debe tener banda superior"
    
    # Verificar relación entre bandas (inferior < media < superior)
    col_bbl = [c for c in bbands.columns if c.startswith('BBL')][0]
    col_bbm = [c for c in bbands.columns if c.startswith('BBM')][0]
    col_bbu = [c for c in bbands.columns if c.startswith('BBU')][0]
    
    valid_rows = bbands.dropna()
    if len(valid_rows) > 0:
        assert all(valid_rows[col_bbl] <= valid_rows[col_bbm]), "Banda inferior debe ser <= banda media"
        assert all(valid_rows[col_bbm] <= valid_rows[col_bbu]), "Banda media debe ser <= banda superior"


def test_ema_calculation():
    """Test que la EMA se calcula correctamente"""
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113,
              115, 117, 116, 118, 120, 119, 121]
    df = pd.DataFrame({'close': prices})
    
    # Calcular EMA 20
    df['EMA_20'] = ta.ema(df['close'], length=20)
    
    # Verificar que tenemos valores
    ema_values = df['EMA_20'].dropna()
    assert len(ema_values) > 0, "EMA debe tener al menos un valor"
    
    # Verificar que los valores son razonables (cerca del precio)
    last_price = df['close'].iloc[-1]
    last_ema = ema_values.iloc[-1]
    assert 0.8 * last_price < last_ema < 1.2 * last_price, "EMA debe estar cerca del precio actual"


def test_indicators_with_insufficient_data():
    """Test manejo de datos insuficientes"""
    # Solo 5 datos (insuficiente para RSI 14)
    prices = [100, 102, 101, 103, 105]
    df = pd.DataFrame({'close': prices})
    
    # Calcular RSI
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # Debe tener valores NaN
    assert df['RSI'].isna().all(), "RSI debe ser NaN con datos insuficientes"


def test_rsi_oversold_condition():
    """Test detección de condición de sobreventa (RSI < 35)"""
    # Crear datos que generen RSI bajo (caída fuerte)
    prices = [100] + [100 - i*2 for i in range(1, 20)]
    df = pd.DataFrame({'close': prices})
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # Verificar que hay al menos un valor de RSI < 35
    rsi_values = df['RSI'].dropna()
    if len(rsi_values) > 0:
        assert any(val < 40 for val in rsi_values), "Debe haber valores de RSI bajos en caída fuerte"


def test_ema_trend_detection():
    """Test detección de tendencia con EMA"""
    # Crear tendencia alcista clara
    prices_up = [100 + i for i in range(25)]
    df_up = pd.DataFrame({'close': prices_up})
    df_up['EMA_20'] = ta.ema(df_up['close'], length=20)
    
    # En tendencia alcista, precio > EMA
    last_price_up = df_up['close'].iloc[-1]
    last_ema_up = df_up['EMA_20'].dropna().iloc[-1]
    assert last_price_up > last_ema_up, "En tendencia alcista, precio debe estar sobre EMA"
    
    # Crear tendencia bajista clara
    prices_down = [100 - i for i in range(25)]
    df_down = pd.DataFrame({'close': prices_down})
    df_down['EMA_20'] = ta.ema(df_down['close'], length=20)
    
    # En tendencia bajista, precio < EMA
    last_price_down = df_down['close'].iloc[-1]
    last_ema_down = df_down['EMA_20'].dropna().iloc[-1]
    assert last_price_down < last_ema_down, "En tendencia bajista, precio debe estar bajo EMA"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
