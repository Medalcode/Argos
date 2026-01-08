"""
Configuración de pytest y fixtures
"""
import pytest
from unittest.mock import Mock
import pandas as pd


@pytest.fixture
def mock_exchange():
    """Mock de exchange CCXT para tests"""
    exchange = Mock()
    
    # Simular balance
    exchange.fetch_balance.return_value = {
        'free': {'USDT': 1000.0, 'BTC': 0.01},
        'used': {'USDT': 0.0, 'BTC': 0.0},
        'total': {'USDT': 1000.0, 'BTC': 0.01}
    }
    
    # Simular precio ticker
    exchange.fetch_ticker.return_value = {
        'last': 90000.0,
        'bid': 89995.0,
        'ask': 90005.0
    }
    
    # Simular orden
    exchange.create_market_buy_order.return_value = {
        'id': 'test_order_123',
        'status': 'filled',
        'amount': 0.01,
        'price': 90000.0
    }
    
    exchange.create_market_sell_order.return_value = {
        'id': 'test_order_456',
        'status': 'filled',
        'amount': 0.01,
        'price': 91000.0
    }
    
    # Simular OHLCV
    ohlcv_data = []
    for i in range(50):
        ohlcv_data.append([
            1600000000000 + i * 60000,  # timestamp
            90000 + i * 100,  # open
            90500 + i * 100,  # high
            89500 + i * 100,  # low
            90200 + i * 100,  # close
            100.0  # volume
        ])
    exchange.fetch_ohlcv.return_value = ohlcv_data
    
    return exchange


@pytest.fixture
def sample_dataframe():
    """DataFrame de muestra con datos de precios"""
    prices = [90000 + i * 100 for i in range(50)]
    df = pd.DataFrame({
        'close': prices,
        'high': [p + 500 for p in prices],
        'low': [p - 500 for p in prices],
        'volume': [100.0] * 50
    })
    return df


@pytest.fixture
def mock_estado_inicial():
    """Estado inicial de prueba"""
    return {
        "posicion_abierta": False,
        "precio_compra": 0,
        "cantidad": 0,
        "max_precio": 0,
        "pnl_acumulado": 0.0,
        "operaciones_hoy": 0
    }


@pytest.fixture
def mock_estado_con_posicion():
    """Estado con posición abierta"""
    return {
        "posicion_abierta": True,
        "precio_compra": 90000,
        "cantidad": 0.01,
        "max_precio": 91000,
        "pnl_acumulado": 5.5,
        "operaciones_hoy": 2
    }
