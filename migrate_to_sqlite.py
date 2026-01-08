"""
Script de migración de datos CSV a SQLite
Migra histórico de operaciones.csv a la nueva base de datos
"""
import os
import csv
import logging
from datetime import datetime
from database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrar_csv_a_sqlite():
    """Migrar datos de operaciones.csv a SQLite"""
    
    csv_file = "operaciones.csv"
    
    if not os.path.exists(csv_file):
        logger.warning(f"⚠️  No se encontró {csv_file}, no hay datos para migrar")
        return
    
    logger.info(f"📂 Iniciando migración desde {csv_file}")
    
    with Database() as db:
        # Leer CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trades_migrados = 0
            
            for row in reader:
                try:
                    # Parsear datos del CSV
                    trade = {
                        'timestamp_compra': row.get('timestamp_compra', row.get('timestamp', '')),
                        'timestamp_venta': row.get('timestamp_venta', row.get('timestamp', '')),
                        'precio_compra': float(row.get('precio_compra', 0)),
                        'precio_venta': float(row.get('precio_venta', 0)),
                        'cantidad': float(row.get('cantidad', 0)),
                        'pnl_usd': float(row.get('pnl_usd', row.get('pnl', 0))),
                        'pnl_pct': float(row.get('pnl_pct', 0)),
                        'razon_salida': row.get('razon_salida', row.get('razon', 'Manual')),
                        'max_precio': float(row.get('max_precio', 0)) if row.get('max_precio') else None,
                        'trailing_pct': float(row.get('trailing_pct', 0)) if row.get('trailing_pct') else None,
                        'rsi_compra': float(row.get('rsi_compra', 0)) if row.get('rsi_compra') else None,
                        'duracion_minutos': int(row.get('duracion_minutos', 0)) if row.get('duracion_minutos') else None
                    }
                    
                    # Guardar en SQLite
                    db.guardar_trade(trade)
                    trades_migrados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error al migrar fila: {row} - {e}")
                    continue
        
        logger.info(f"✅ Migración completada: {trades_migrados} trades migrados")
        
        # Calcular métricas
        logger.info("📊 Calculando métricas diarias...")
        
        # Obtener fechas únicas de los trades
        cursor = db.conn.cursor()
        cursor.execute("SELECT DISTINCT date(timestamp_venta) as fecha FROM trades ORDER BY fecha")
        fechas = [row['fecha'] for row in cursor.fetchall()]
        
        for fecha in fechas:
            db.actualizar_metricas_diarias(fecha)
            logger.info(f"  ✓ Métricas calculadas para {fecha}")
        
        # Mostrar estadísticas globales
        stats = db.obtener_estadisticas_globales()
        logger.info("\n📈 Estadísticas globales:")
        logger.info(f"  Total trades: {stats['total_trades']}")
        logger.info(f"  Ganadoras: {stats['ganadoras']}")
        logger.info(f"  Perdedoras: {stats['perdedoras']}")
        logger.info(f"  Win Rate: {stats['win_rate']:.2f}%")
        logger.info(f"  PnL Total: ${stats['pnl_total']:.2f}")
        logger.info(f"  PnL Promedio: {stats['pnl_promedio']:.2f}%")
        logger.info(f"  Mejor trade: ${stats['mejor_trade']:.2f}")
        logger.info(f"  Peor trade: ${stats['peor_trade']:.2f}")
        logger.info(f"  Duración promedio: {stats['duracion_promedio']:.0f} min")
    
    # Renombrar CSV para backup
    backup_file = f"{csv_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.rename(csv_file, backup_file)
    logger.info(f"💾 Backup creado: {backup_file}")


if __name__ == "__main__":
    print("=" * 60)
    print("  MIGRACIÓN DE DATOS CSV A SQLITE")
    print("=" * 60)
    print()
    
    migrar_csv_a_sqlite()
    
    print()
    print("=" * 60)
    print("  ✅ MIGRACIÓN COMPLETADA")
    print("=" * 60)
