"""
Módulo de Métricas Avanzadas de Performance para Argos Trading Bot
Calcula Sharpe Ratio, Maximum Drawdown, Win Rate por periodo, Profit Factor, etc.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import Database
import math

logger = logging.getLogger(__name__)


class MetricasPerformance:
    """Calculador de métricas avanzadas de trading"""
    
    def __init__(self, db: Database = None):
        self.db = db if db else Database()
    
    # ===== SHARPE RATIO =====
    
    def calcular_sharpe_ratio(self, periodo_dias: int = 30, rf_rate: float = 0.0) -> float:
        """
        Calcular Sharpe Ratio: (Retorno promedio - Tasa libre de riesgo) / Desviación estándar
        
        Args:
            periodo_dias: Días a considerar para el cálculo
            rf_rate: Tasa libre de riesgo anual (default 0%)
        
        Returns:
            Sharpe Ratio (>1 es bueno, >2 es excelente)
        """
        # Obtener trades del periodo
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT pnl_pct FROM trades
            WHERE date(timestamp_venta) >= ?
            ORDER BY timestamp_venta
        """, (fecha_inicio,))
        
        retornos = [row['pnl_pct'] / 100 for row in cursor.fetchall()]  # Convertir % a decimal
        
        if len(retornos) < 2:
            logger.warning("⚠️  Insuficientes datos para calcular Sharpe Ratio")
            return 0.0
        
        # Calcular promedio y desviación estándar
        retorno_promedio = sum(retornos) / len(retornos)
        varianza = sum((r - retorno_promedio) ** 2 for r in retornos) / (len(retornos) - 1)
        desviacion_std = math.sqrt(varianza)
        
        if desviacion_std == 0:
            return 0.0
        
        # Sharpe Ratio = (Retorno - Rf) / Desviación
        sharpe = (retorno_promedio - rf_rate) / desviacion_std
        
        # Anualizar (asumiendo ~252 días de trading al año)
        sharpe_anualizado = sharpe * math.sqrt(252 / periodo_dias)
        
        return round(sharpe_anualizado, 2)
    
    # ===== MAXIMUM DRAWDOWN =====
    
    def calcular_maximum_drawdown(self, periodo_dias: int = 30) -> Tuple[float, str, str]:
        """
        Calcular Maximum Drawdown: Mayor caída desde un pico
        
        Returns:
            (drawdown_pct, fecha_pico, fecha_valle)
        """
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT timestamp_venta, pnl_usd FROM trades
            WHERE date(timestamp_venta) >= ?
            ORDER BY timestamp_venta
        """, (fecha_inicio,))
        
        trades = cursor.fetchall()
        
        if len(trades) < 2:
            return 0.0, "", ""
        
        # Calcular equity curve (capital acumulado)
        capital_inicial = 10000  # Asumimos 10K inicial
        equity_curve = []
        capital_actual = capital_inicial
        
        for trade in trades:
            capital_actual += trade['pnl_usd']
            equity_curve.append({
                'fecha': trade['timestamp_venta'],
                'capital': capital_actual
            })
        
        # Encontrar máximo drawdown
        max_dd = 0.0
        fecha_pico = ""
        fecha_valle = ""
        pico = equity_curve[0]['capital']
        fecha_pico_actual = equity_curve[0]['fecha']
        
        for punto in equity_curve:
            if punto['capital'] > pico:
                pico = punto['capital']
                fecha_pico_actual = punto['fecha']
            
            dd = ((pico - punto['capital']) / pico) * 100
            
            if dd > max_dd:
                max_dd = dd
                fecha_pico = fecha_pico_actual
                fecha_valle = punto['fecha']
        
        return round(max_dd, 2), fecha_pico, fecha_valle
    
    # ===== WIN RATE POR PERIODO =====
    
    def calcular_win_rate_por_periodo(self, periodo: str = "diario") -> List[Dict]:
        """
        Calcular Win Rate por periodo (diario, semanal, mensual)
        
        Args:
            periodo: "diario", "semanal" o "mensual"
        
        Returns:
            Lista de dicts con {periodo, win_rate, total, ganadoras, perdedoras}
        """
        cursor = self.db.conn.cursor()
        
        if periodo == "diario":
            group_by = "date(timestamp_venta)"
            format_str = "%Y-%m-%d"
        elif periodo == "semanal":
            group_by = "strftime('%Y-W%W', timestamp_venta)"
            format_str = "Semana %W de %Y"
        elif periodo == "mensual":
            group_by = "strftime('%Y-%m', timestamp_venta)"
            format_str = "%Y-%m"
        else:
            raise ValueError("Periodo debe ser 'diario', 'semanal' o 'mensual'")
        
        cursor.execute(f"""
            SELECT 
                {group_by} as periodo,
                COUNT(*) as total,
                SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as ganadoras,
                SUM(CASE WHEN pnl_usd <= 0 THEN 1 ELSE 0 END) as perdedoras
            FROM trades
            GROUP BY {group_by}
            ORDER BY periodo DESC
            LIMIT 30
        """)
        
        resultados = []
        for row in cursor.fetchall():
            win_rate = (row['ganadoras'] / row['total']) * 100 if row['total'] > 0 else 0
            resultados.append({
                'periodo': row['periodo'],
                'win_rate': round(win_rate, 2),
                'total': row['total'],
                'ganadoras': row['ganadoras'],
                'perdedoras': row['perdedoras']
            })
        
        return resultados
    
    # ===== PROFIT FACTOR =====
    
    def calcular_profit_factor(self, periodo_dias: int = 30) -> float:
        """
        Calcular Profit Factor: Ganancias Totales / Pérdidas Totales
        >1 = rentable, >2 = muy bueno, >3 = excelente
        
        Returns:
            Profit Factor (0 si no hay pérdidas)
        """
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        
        # Ganancias totales
        ganancias = cursor.execute("""
            SELECT SUM(pnl_usd) as total FROM trades
            WHERE date(timestamp_venta) >= ? AND pnl_usd > 0
        """, (fecha_inicio,)).fetchone()['total'] or 0
        
        # Pérdidas totales (valor absoluto)
        perdidas = abs(cursor.execute("""
            SELECT SUM(pnl_usd) as total FROM trades
            WHERE date(timestamp_venta) >= ? AND pnl_usd <= 0
        """, (fecha_inicio,)).fetchone()['total'] or 0)
        
        if perdidas == 0:
            return 0.0 if ganancias == 0 else float('inf')
        
        return round(ganancias / perdidas, 2)
    
    # ===== EXPECTANCY =====
    
    def calcular_expectancy(self, periodo_dias: int = 30) -> float:
        """
        Calcular Expectancy: (Win% * Avg Win) - (Loss% * Avg Loss)
        Valor esperado por trade
        
        Returns:
            Expectancy en USD
        """
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as ganadoras,
                AVG(CASE WHEN pnl_usd > 0 THEN pnl_usd ELSE NULL END) as avg_win,
                AVG(CASE WHEN pnl_usd <= 0 THEN pnl_usd ELSE NULL END) as avg_loss
            FROM trades
            WHERE date(timestamp_venta) >= ?
        """, (fecha_inicio,))
        
        row = cursor.fetchone()
        
        if row['total'] == 0:
            return 0.0
        
        win_pct = row['ganadoras'] / row['total']
        loss_pct = 1 - win_pct
        avg_win = row['avg_win'] or 0
        avg_loss = row['avg_loss'] or 0
        
        expectancy = (win_pct * avg_win) - (loss_pct * abs(avg_loss))
        
        return round(expectancy, 2)
    
    # ===== RECOVERY FACTOR =====
    
    def calcular_recovery_factor(self, periodo_dias: int = 30) -> float:
        """
        Calcular Recovery Factor: Net Profit / Max Drawdown
        >10 es excelente
        
        Returns:
            Recovery Factor
        """
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        # Calcular net profit
        cursor = self.db.conn.cursor()
        net_profit = cursor.execute("""
            SELECT SUM(pnl_usd) as total FROM trades
            WHERE date(timestamp_venta) >= ?
        """, (fecha_inicio,)).fetchone()['total'] or 0
        
        # Calcular max drawdown
        max_dd, _, _ = self.calcular_maximum_drawdown(periodo_dias)
        
        if max_dd == 0:
            return 0.0
        
        # Recovery Factor = Net Profit / Max DD (en términos absolutos)
        # Asumimos capital inicial de 10K para calcular DD en USD
        max_dd_usd = (max_dd / 100) * 10000
        
        if max_dd_usd == 0:
            return float('inf') if net_profit > 0 else 0.0
        
        return round(net_profit / max_dd_usd, 2)
    
    # ===== AVERAGE MAE/MFE =====
    
    def calcular_mae_mfe_promedio(self, periodo_dias: int = 30) -> Tuple[float, float]:
        """
        Calcular MAE (Maximum Adverse Excursion) y MFE (Maximum Favorable Excursion) promedio
        
        MAE: Máxima pérdida flotante durante el trade
        MFE: Máxima ganancia flotante durante el trade
        
        Returns:
            (mae_promedio, mfe_promedio) en USD
        """
        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                precio_compra,
                precio_venta,
                max_precio,
                cantidad
            FROM trades
            WHERE date(timestamp_venta) >= ? AND max_precio IS NOT NULL
        """, (fecha_inicio,))
        
        trades = cursor.fetchall()
        
        if not trades:
            return 0.0, 0.0
        
        mae_total = 0.0
        mfe_total = 0.0
        
        for trade in trades:
            # MAE: Máxima pérdida = precio_compra - (mínimo teórico, asumimos 1% peor)
            # En este caso simplificado, usamos precio_compra vs precio_venta
            mae = abs(min(0, (trade['precio_venta'] - trade['precio_compra']) * trade['cantidad']))
            mae_total += mae
            
            # MFE: Máxima ganancia = max_precio - precio_compra
            mfe = (trade['max_precio'] - trade['precio_compra']) * trade['cantidad']
            mfe_total += mfe
        
        n = len(trades)
        return round(mae_total / n, 2), round(mfe_total / n, 2)
    
    # ===== REPORTE COMPLETO =====
    
    def generar_reporte_completo(self, periodo_dias: int = 30) -> Dict:
        """
        Generar reporte completo de todas las métricas
        
        Returns:
            Dict con todas las métricas calculadas
        """
        logger.info(f"📊 Generando reporte de métricas ({periodo_dias} días)...")
        
        sharpe = self.calcular_sharpe_ratio(periodo_dias)
        max_dd, fecha_pico_dd, fecha_valle_dd = self.calcular_maximum_drawdown(periodo_dias)
        profit_factor = self.calcular_profit_factor(periodo_dias)
        expectancy = self.calcular_expectancy(periodo_dias)
        recovery_factor = self.calcular_recovery_factor(periodo_dias)
        mae, mfe = self.calcular_mae_mfe_promedio(periodo_dias)
        
        # Win rate diario
        win_rates = self.calcular_win_rate_por_periodo("diario")
        win_rate_promedio = sum(wr['win_rate'] for wr in win_rates) / len(win_rates) if win_rates else 0
        
        # Estadísticas globales
        stats = self.db.obtener_estadisticas_globales()
        
        reporte = {
            'periodo_dias': periodo_dias,
            'fecha_generacion': datetime.now().isoformat(),
            
            # Métricas principales
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd,
            'max_drawdown_fechas': {'pico': fecha_pico_dd, 'valle': fecha_valle_dd},
            'profit_factor': profit_factor,
            'expectancy_usd': expectancy,
            'recovery_factor': recovery_factor,
            'mae_promedio': mae,
            'mfe_promedio': mfe,
            
            # Estadísticas generales
            'total_trades': stats['total_trades'],
            'win_rate_promedio': round(win_rate_promedio, 2),
            'pnl_total': stats['pnl_total'],
            'pnl_promedio_pct': stats['pnl_promedio'],
            'mejor_trade': stats['mejor_trade'],
            'peor_trade': stats['peor_trade'],
            'duracion_promedio_min': stats['duracion_promedio'],
            
            # Interpretaciones
            'interpretacion': {
                'sharpe': self._interpretar_sharpe(sharpe),
                'profit_factor': self._interpretar_profit_factor(profit_factor),
                'max_dd': self._interpretar_drawdown(max_dd),
                'recovery': self._interpretar_recovery(recovery_factor)
            }
        }
        
        return reporte
    
    # ===== INTERPRETACIONES =====
    
    def _interpretar_sharpe(self, sharpe: float) -> str:
        if sharpe < 0:
            return "Malo (retorno negativo ajustado por riesgo)"
        elif sharpe < 1:
            return "Pobre (riesgo alto vs retorno)"
        elif sharpe < 2:
            return "Bueno (retorno aceptable por el riesgo)"
        elif sharpe < 3:
            return "Muy bueno (excelente retorno ajustado)"
        else:
            return "Excelente (retorno excepcional vs riesgo)"
    
    def _interpretar_profit_factor(self, pf: float) -> str:
        if pf == 0:
            return "Sin datos suficientes"
        elif pf < 1:
            return "Malo (pérdidas > ganancias)"
        elif pf < 1.5:
            return "Aceptable (ligeramente rentable)"
        elif pf < 2:
            return "Bueno (ganancias duplican pérdidas)"
        elif pf < 3:
            return "Muy bueno (ganancias triplican pérdidas)"
        else:
            return "Excelente (altamente rentable)"
    
    def _interpretar_drawdown(self, dd: float) -> str:
        if dd < 5:
            return "Excelente (bajo riesgo)"
        elif dd < 10:
            return "Bueno (riesgo moderado)"
        elif dd < 20:
            return "Aceptable (riesgo medio-alto)"
        elif dd < 30:
            return "Alto (riesgo significativo)"
        else:
            return "Muy alto (riesgo extremo)"
    
    def _interpretar_recovery(self, rf: float) -> str:
        if rf < 2:
            return "Bajo (recuperación lenta)"
        elif rf < 5:
            return "Aceptable (recuperación moderada)"
        elif rf < 10:
            return "Bueno (buena recuperación)"
        else:
            return "Excelente (recuperación rápida)"


def imprimir_reporte_consola(reporte: Dict):
    """Imprimir reporte de métricas en consola con formato"""
    print("\n" + "=" * 70)
    print(f"  📊 REPORTE DE MÉTRICAS DE PERFORMANCE ({reporte['periodo_dias']} días)")
    print("=" * 70)
    
    print("\n🎯 MÉTRICAS PRINCIPALES:")
    print(f"  • Sharpe Ratio: {reporte['sharpe_ratio']} - {reporte['interpretacion']['sharpe']}")
    print(f"  • Maximum Drawdown: {reporte['max_drawdown_pct']}% - {reporte['interpretacion']['max_dd']}")
    print(f"  • Profit Factor: {reporte['profit_factor']} - {reporte['interpretacion']['profit_factor']}")
    print(f"  • Expectancy: ${reporte['expectancy_usd']:.2f} por trade")
    print(f"  • Recovery Factor: {reporte['recovery_factor']} - {reporte['interpretacion']['recovery']}")
    
    print("\n📈 ESTADÍSTICAS GENERALES:")
    print(f"  • Total Trades: {reporte['total_trades']}")
    print(f"  • Win Rate Promedio: {reporte['win_rate_promedio']:.2f}%")
    print(f"  • PnL Total: ${reporte['pnl_total']:.2f}")
    print(f"  • PnL Promedio: {reporte['pnl_promedio_pct']:.2f}%")
    print(f"  • Mejor Trade: ${reporte['mejor_trade']:.2f}")
    print(f"  • Peor Trade: ${reporte['peor_trade']:.2f}")
    print(f"  • Duración Promedio: {reporte['duracion_promedio_min']:.0f} minutos")
    
    print("\n💹 MAE/MFE:")
    print(f"  • MAE Promedio: ${reporte['mae_promedio']:.2f}")
    print(f"  • MFE Promedio: ${reporte['mfe_promedio']:.2f}")
    
    if reporte['max_drawdown_fechas']['pico']:
        print(f"\n📉 Drawdown Máximo:")
        print(f"  • Pico: {reporte['max_drawdown_fechas']['pico']}")
        print(f"  • Valle: {reporte['max_drawdown_fechas']['valle']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Test con base de datos de prueba
    logging.basicConfig(level=logging.INFO)
    
    # Crear base de datos de prueba con datos de ejemplo
    from database import Database
    import os
    
    test_db = "test_metricas.db"
    
    with Database(test_db) as db:
        # Insertar trades de ejemplo
        for i in range(10):
            trade = {
                'timestamp_compra': (datetime.now() - timedelta(days=10-i, hours=2)).isoformat(),
                'timestamp_venta': (datetime.now() - timedelta(days=10-i)).isoformat(),
                'precio_compra': 90000 + i * 100,
                'precio_venta': 91000 + i * 100,
                'cantidad': 0.01,
                'pnl_usd': 10.0 + i,
                'pnl_pct': 1.11,
                'razon_salida': 'Take Profit',
                'max_precio': 91500 + i * 100,
                'duracion_minutos': 120
            }
            db.guardar_trade(trade)
        
        # Calcular métricas
        metricas = MetricasPerformance(db)
        reporte = metricas.generar_reporte_completo(periodo_dias=30)
        
        # Imprimir reporte
        imprimir_reporte_consola(reporte)
    
    # Limpiar
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("\n✅ Tests de metricas.py completados")
