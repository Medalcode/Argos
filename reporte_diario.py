#!/usr/bin/env python3
"""
Script de Reporte Diario - Argos Bot
Genera un resumen completo del día y lo envía por Telegram
"""
import sys
import os
from datetime import datetime
from database import Database
from metricas import MetricasPerformance

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generar_reporte_diario():
    """Genera reporte diario completo"""
    
    print("=" * 70)
    print(f"  📊 REPORTE DIARIO - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 70)
    print()
    
    with Database() as db:
        # 1. Estado actual
        estado = db.cargar_estado()
        print("🤖 ESTADO DEL BOT:")
        print(f"  Posición: {'🟢 ABIERTA' if estado['posicion_abierta'] else '⚪ CERRADA'}")
        
        if estado['posicion_abierta']:
            print(f"  Precio Compra: ${estado['precio_compra']:,.2f}")
            print(f"  Cantidad: {estado['cantidad']:.6f} BTC")
            print(f"  Max Precio: ${estado['max_precio']:,.2f}")
            pnl_flotante = (estado['max_precio'] - estado['precio_compra']) * estado['cantidad']
            print(f"  PnL Flotante: ${pnl_flotante:.2f}")
        
        print(f"  PnL Acumulado: ${estado['pnl_acumulado']:.2f}")
        print(f"  Operaciones Hoy: {estado['operaciones_hoy']}")
        print()
        
        # 2. Trades del día
        trades_hoy = db.obtener_trades_hoy()
        print(f"📈 TRADES DE HOY: {len(trades_hoy)}")
        
        if trades_hoy:
            for i, trade in enumerate(trades_hoy, 1):
                emoji = "🟢" if trade['pnl_usd'] > 0 else "🔴"
                print(f"  {emoji} Trade #{i}:")
                print(f"     Compra: ${trade['precio_compra']:,.2f} → Venta: ${trade['precio_venta']:,.2f}")
                print(f"     PnL: ${trade['pnl_usd']:.2f} ({trade['pnl_pct']:.2f}%)")
                print(f"     Razón: {trade['razon_salida']}")
                print(f"     Duración: {trade['duracion_minutos']} min")
        else:
            print("  Sin trades completados hoy")
        
        print()
        
        # 3. Estadísticas globales
        stats = db.obtener_estadisticas_globales()
        print("📊 ESTADÍSTICAS GLOBALES:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Ganadoras: {stats['ganadoras']} | Perdedoras: {stats['perdedoras']}")
        print(f"  Win Rate: {stats['win_rate']:.2f}%")
        print(f"  PnL Total: ${stats['pnl_total']:.2f}")
        
        if stats['total_trades'] > 0:
            print(f"  PnL Promedio: {stats['pnl_promedio']:.2f}%")
            print(f"  Mejor Trade: ${stats['mejor_trade']:.2f}")
            print(f"  Peor Trade: ${stats['peor_trade']:.2f}")
            print(f"  Duración Promedio: {stats['duracion_promedio']:.0f} min")
        
        print()
        
        # 4. Métricas avanzadas (si hay suficientes datos)
        if stats['total_trades'] >= 5:
            print("📈 MÉTRICAS AVANZADAS:")
            metricas = MetricasPerformance(db)
            
            try:
                sharpe = metricas.calcular_sharpe_ratio(7)
                print(f"  Sharpe Ratio (7d): {sharpe}")
            except:
                pass
            
            try:
                max_dd, _, _ = metricas.calcular_maximum_drawdown(7)
                print(f"  Max Drawdown (7d): {max_dd:.2f}%")
            except:
                pass
            
            try:
                pf = metricas.calcular_profit_factor(7)
                print(f"  Profit Factor (7d): {pf}")
            except:
                pass
            
            try:
                exp = metricas.calcular_expectancy(7)
                print(f"  Expectancy: ${exp:.2f} por trade")
            except:
                pass
            
            print()
        
        # 5. Métricas del día
        metricas_hoy = db.obtener_metricas_diarias(datetime.now().strftime("%Y-%m-%d"))
        if metricas_hoy:
            print("📊 MÉTRICAS DEL DÍA:")
            print(f"  Operaciones: {metricas_hoy['operaciones_total']}")
            print(f"  Win Rate: {metricas_hoy['win_rate']:.2f}%")
            print(f"  PnL Total: ${metricas_hoy['pnl_total_usd']:.2f}")
            if metricas_hoy['operaciones_total'] > 0:
                print(f"  Profit Factor: {metricas_hoy['profit_factor']:.2f}")
            print()
    
    print("=" * 70)
    print(f"  Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # 6. Enviar por Telegram (opcional)
    try:
        from notificaciones import enviar_telegram
        
        mensaje = f"""
📊 REPORTE DIARIO - {datetime.now().strftime('%d/%m/%Y')}

🤖 Estado: {'🟢 Posición Abierta' if estado['posicion_abierta'] else '⚪ Sin Posición'}
💰 PnL Acumulado: ${estado['pnl_acumulado']:.2f}
📈 Trades Hoy: {len(trades_hoy)}

📊 Global:
• Total Trades: {stats['total_trades']}
• Win Rate: {stats['win_rate']:.2f}%
• PnL Total: ${stats['pnl_total']:.2f}
"""
        
        # Descomentar para enviar por Telegram
        # enviar_telegram(mensaje)
        # print("✅ Reporte enviado por Telegram")
        
    except Exception as e:
        print(f"⚠️  No se pudo enviar por Telegram: {e}")


if __name__ == "__main__":
    generar_reporte_diario()
