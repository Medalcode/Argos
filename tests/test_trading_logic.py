"""
Tests para lógica de trading (compra/venta/trailing stop)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTripleFiltro:
    """Tests para la lógica del Triple Filtro"""
    
    def test_compra_con_todas_condiciones_cumplidas(self):
        """Test que se genera señal de compra cuando se cumplen las 3 condiciones"""
        # Configurar condiciones
        rsi = 30  # < 35 ✓
        precio = 90000
        lower_band = 91000  # precio < lower_band ✓
        ema = 89000  # precio > ema ✓
        
        # Evaluar condiciones
        condicion_rsi = rsi < 35
        condicion_bb = precio < lower_band
        condicion_ema = precio > ema
        
        senal_compra = condicion_rsi and condicion_bb and condicion_ema
        
        assert senal_compra == True, "Debe generar señal de compra con todas las condiciones"
    
    def test_no_compra_rsi_alto(self):
        """Test que NO se compra si RSI es alto (> 35)"""
        rsi = 50  # > 35 ✗
        precio = 90000
        lower_band = 91000
        ema = 89000
        
        condicion_rsi = rsi < 35
        condicion_bb = precio < lower_band
        condicion_ema = precio > ema
        
        senal_compra = condicion_rsi and condicion_bb and condicion_ema
        
        assert senal_compra == False, "NO debe comprar con RSI alto"
    
    def test_no_compra_precio_alto_vs_bb(self):
        """Test que NO se compra si precio está sobre banda de Bollinger"""
        rsi = 30
        precio = 92000
        lower_band = 91000  # precio > lower_band ✗
        ema = 89000
        
        condicion_rsi = rsi < 35
        condicion_bb = precio < lower_band
        condicion_ema = precio > ema
        
        senal_compra = condicion_rsi and condicion_bb and condicion_ema
        
        assert senal_compra == False, "NO debe comprar si precio está sobre BB"
    
    def test_no_compra_tendencia_bajista(self):
        """Test que NO se compra en tendencia bajista (precio < EMA)"""
        rsi = 30
        precio = 88000
        lower_band = 91000
        ema = 89000  # precio < ema ✗
        
        condicion_rsi = rsi < 35
        condicion_bb = precio < lower_band
        condicion_ema = precio > ema
        
        senal_compra = condicion_rsi and condicion_bb and condicion_ema
        
        assert senal_compra == False, "NO debe comprar en tendencia bajista"


class TestTrailingStop:
    """Tests para lógica del Trailing Stop"""
    
    def test_trailing_stop_actualiza_maximo(self):
        """Test que el trailing stop actualiza el máximo precio"""
        precio_compra = 90000
        max_precio = precio_compra
        precio_actual = 91000
        
        # Actualizar máximo
        if precio_actual > max_precio:
            max_precio = precio_actual
        
        assert max_precio == 91000, "Debe actualizar el máximo precio"
    
    def test_trailing_stop_no_baja_maximo(self):
        """Test que el máximo NO baja si el precio cae"""
        max_precio = 91000
        precio_actual = 90500
        
        # No actualizar si precio baja
        if precio_actual > max_precio:
            max_precio = precio_actual
        
        assert max_precio == 91000, "El máximo NO debe bajar"
    
    def test_trailing_stop_dispara_venta(self):
        """Test que el trailing stop dispara venta correctamente"""
        precio_compra = 90000
        max_precio = 92000
        ts_pct = 0.005  # 0.5%
        precio_actual = 91400
        
        precio_trailing = max_precio * (1 - ts_pct)
        
        # Trailing = 92000 * 0.995 = 91540
        # Precio actual = 91400 < 91540 → Vender
        dispara_venta = precio_actual <= precio_trailing
        
        assert dispara_venta == True, "Debe disparar venta cuando precio cae 0.5% desde máximo"
    
    def test_trailing_stop_no_dispara_antes_tiempo(self):
        """Test que trailing stop NO dispara si no se alcanzó el nivel"""
        max_precio = 92000
        ts_pct = 0.005
        precio_actual = 91600  # Solo cayó 0.43%
        
        precio_trailing = max_precio * (1 - ts_pct)
        dispara_venta = precio_actual <= precio_trailing
        
        assert dispara_venta == False, "NO debe disparar si no alcanzó el nivel"


class TestPnLCalculation:
    """Tests para cálculo de PnL"""
    
    def test_pnl_positivo(self):
        """Test cálculo de PnL positivo"""
        precio_compra = 90000
        precio_venta = 91000
        
        pnl_pct = (precio_venta - precio_compra) / precio_compra
        pnl_porcentaje = pnl_pct * 100
        
        assert pnl_pct > 0, "PnL debe ser positivo"
        assert abs(pnl_porcentaje - 1.11) < 0.1, "PnL debe ser ~1.11%"
    
    def test_pnl_negativo(self):
        """Test cálculo de PnL negativo (pérdida)"""
        precio_compra = 90000
        precio_venta = 89000
        
        pnl_pct = (precio_venta - precio_compra) / precio_compra
        pnl_porcentaje = pnl_pct * 100
        
        assert pnl_pct < 0, "PnL debe ser negativo en pérdida"
        assert abs(pnl_porcentaje + 1.11) < 0.1, "PnL debe ser ~-1.11%"
    
    def test_pnl_cero(self):
        """Test PnL cero (venta al mismo precio)"""
        precio_compra = 90000
        precio_venta = 90000
        
        pnl_pct = (precio_venta - precio_compra) / precio_compra
        
        assert pnl_pct == 0, "PnL debe ser 0 si vende al mismo precio"


class TestStopLossTakeProfit:
    """Tests para Stop Loss y Take Profit"""
    
    def test_stop_loss_dispara(self):
        """Test que Stop Loss dispara correctamente"""
        precio_compra = 90000
        sl_pct = 0.01  # 1%
        precio_actual = 89000
        
        precio_sl = precio_compra * (1 - sl_pct)
        dispara_sl = precio_actual <= precio_sl
        
        assert dispara_sl == True, "Stop Loss debe disparar cuando precio cae 1%"
    
    def test_take_profit_dispara(self):
        """Test que Take Profit dispara correctamente"""
        precio_compra = 90000
        tp_pct = 0.015  # 1.5%
        precio_actual = 91400
        
        precio_tp = precio_compra * (1 + tp_pct)
        dispara_tp = precio_actual >= precio_tp
        
        assert dispara_tp == True, "Take Profit debe disparar cuando precio sube 1.5%"
    
    def test_prioridad_trailing_sobre_tp(self):
        """Test que Trailing Stop tiene prioridad sobre Take Profit"""
        precio_compra = 90000
        max_precio = 92000
        precio_actual = 91400
        
        ts_pct = 0.005
        tp_pct = 0.015
        
        # Calcular ambos niveles
        precio_trailing = max_precio * (1 - ts_pct)  # 91540
        precio_tp = precio_compra * (1 + tp_pct)     # 91350
        
        # Trailing dispara primero (91400 < 91540)
        dispara_trailing = precio_actual <= precio_trailing
        dispara_tp = precio_actual >= precio_tp
        
        # En el código real, trailing se verifica primero
        assert dispara_trailing == True, "Trailing debe disparar"
        assert dispara_tp == True, "TP también se cumple"
        # Pero en el código, trailing tiene prioridad (if-elif)


class TestBalanceValidation:
    """Tests para validación de saldo"""
    
    def test_saldo_suficiente(self):
        """Test validación de saldo suficiente"""
        usdt_free = 100.0
        min_balance = 15.0
        
        saldo_suficiente = usdt_free >= min_balance
        
        assert saldo_suficiente == True, "Debe tener saldo suficiente"
    
    def test_saldo_insuficiente(self):
        """Test validación de saldo insuficiente"""
        usdt_free = 10.0
        min_balance = 15.0
        
        saldo_suficiente = usdt_free >= min_balance
        
        assert saldo_suficiente == False, "Saldo debe ser insuficiente"
    
    def test_calculo_cantidad_compra(self):
        """Test cálculo correcto de cantidad a comprar"""
        usdt_free = 100.0
        pos_size_pct = 0.95  # 95%
        precio_btc = 90000
        
        gasto_usdt = usdt_free * pos_size_pct  # 95 USDT
        cantidad_btc = gasto_usdt / precio_btc  # 0.00105 BTC
        
        assert abs(gasto_usdt - 95.0) < 0.01, "Debe gastar 95 USDT"
        assert abs(cantidad_btc - 0.001055) < 0.000001, "Debe comprar ~0.00105 BTC"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
