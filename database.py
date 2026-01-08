"""
Módulo de Base de Datos SQLite para Argos Trading Bot
Gestiona persistencia de datos: trades, señales, precios y métricas
"""
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os


# Configuración
DB_FILE = os.getenv("DB_FILE", "argos.db")
logger = logging.getLogger(__name__)


class Database:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.conn = None
        self.conectar()
        self.crear_tablas()
    
    def conectar(self):
        """Conectar a la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Devolver rows como diccionarios
            logger.info(f"✅ Conectado a base de datos: {self.db_file}")
        except sqlite3.Error as e:
            logger.error(f"❌ Error al conectar a base de datos: {e}")
            raise
    
    def crear_tablas(self):
        """Crear todas las tablas necesarias"""
        cursor = self.conn.cursor()
        
        # Tabla de trades (operaciones completadas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_compra TEXT NOT NULL,
                timestamp_venta TEXT NOT NULL,
                precio_compra REAL NOT NULL,
                precio_venta REAL NOT NULL,
                cantidad REAL NOT NULL,
                pnl_usd REAL NOT NULL,
                pnl_pct REAL NOT NULL,
                razon_salida TEXT NOT NULL,
                max_precio REAL,
                trailing_pct REAL,
                rsi_compra REAL,
                duracion_minutos INTEGER,
                UNIQUE(timestamp_compra, timestamp_venta)
            )
        """)
        
        # Tabla de señales (todos los checks de entrada/salida)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS senales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                tipo TEXT NOT NULL,
                precio REAL NOT NULL,
                rsi REAL,
                bb_lower REAL,
                bb_middle REAL,
                bb_upper REAL,
                ema REAL,
                posicion_abierta INTEGER NOT NULL,
                balance_usdt REAL,
                razon TEXT,
                UNIQUE(timestamp, tipo)
            )
        """)
        
        # Tabla de precios (histórico cada 60s)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                precio REAL NOT NULL,
                volumen REAL,
                UNIQUE(timestamp)
            )
        """)
        
        # Tabla de métricas diarias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metricas_diarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL UNIQUE,
                operaciones_total INTEGER DEFAULT 0,
                operaciones_ganadoras INTEGER DEFAULT 0,
                operaciones_perdedoras INTEGER DEFAULT 0,
                pnl_total_usd REAL DEFAULT 0.0,
                pnl_total_pct REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0,
                ganancia_promedio REAL DEFAULT 0.0,
                perdida_promedio REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                max_ganancia REAL DEFAULT 0.0,
                max_perdida REAL DEFAULT 0.0
            )
        """)
        
        # Tabla de estado (reemplaza el JSON)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estado (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                posicion_abierta INTEGER NOT NULL DEFAULT 0,
                precio_compra REAL DEFAULT 0,
                cantidad REAL DEFAULT 0,
                max_precio REAL DEFAULT 0,
                pnl_acumulado REAL DEFAULT 0.0,
                operaciones_hoy INTEGER DEFAULT 0,
                ultimo_update TEXT NOT NULL
            )
        """)
        
        # Insertar estado inicial si no existe
        cursor.execute("""
            INSERT OR IGNORE INTO estado (id, posicion_abierta, ultimo_update)
            VALUES (1, 0, ?)
        """, (datetime.now().isoformat(),))
        
        # Crear índices para mejorar performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp_venta)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_senales_timestamp ON senales(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_precios_timestamp ON precios(timestamp)")
        
        self.conn.commit()
        logger.info("✅ Tablas creadas/verificadas correctamente")
    
    # ===== TRADES =====
    
    def guardar_trade(self, trade: Dict) -> int:
        """Guardar un trade completado"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trades (
                timestamp_compra, timestamp_venta, precio_compra, precio_venta,
                cantidad, pnl_usd, pnl_pct, razon_salida, max_precio,
                trailing_pct, rsi_compra, duracion_minutos
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade['timestamp_compra'],
            trade['timestamp_venta'],
            trade['precio_compra'],
            trade['precio_venta'],
            trade['cantidad'],
            trade['pnl_usd'],
            trade['pnl_pct'],
            trade['razon_salida'],
            trade.get('max_precio'),
            trade.get('trailing_pct'),
            trade.get('rsi_compra'),
            trade.get('duracion_minutos')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def obtener_trades(self, limit: int = 100) -> List[Dict]:
        """Obtener últimos trades"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM trades
            ORDER BY timestamp_venta DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def obtener_trades_hoy(self) -> List[Dict]:
        """Obtener trades del día actual"""
        cursor = self.conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT * FROM trades
            WHERE date(timestamp_venta) = ?
            ORDER BY timestamp_venta DESC
        """, (hoy,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== SEÑALES =====
    
    def guardar_senal(self, senal: Dict) -> int:
        """Guardar una señal de entrada/salida"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO senales (
                timestamp, tipo, precio, rsi, bb_lower, bb_middle, bb_upper,
                ema, posicion_abierta, balance_usdt, razon
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            senal['timestamp'],
            senal['tipo'],
            senal['precio'],
            senal.get('rsi'),
            senal.get('bb_lower'),
            senal.get('bb_middle'),
            senal.get('bb_upper'),
            senal.get('ema'),
            senal['posicion_abierta'],
            senal.get('balance_usdt'),
            senal.get('razon')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def obtener_senales(self, limit: int = 100) -> List[Dict]:
        """Obtener últimas señales"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM senales
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== PRECIOS =====
    
    def guardar_precio(self, timestamp: str, precio: float, volumen: float = None):
        """Guardar precio histórico"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO precios (timestamp, precio, volumen)
            VALUES (?, ?, ?)
        """, (timestamp, precio, volumen))
        self.conn.commit()
    
    def obtener_precios_recientes(self, horas: int = 24) -> List[Dict]:
        """Obtener precios de las últimas N horas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM precios
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """, (horas,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== ESTADO =====
    
    def cargar_estado(self) -> Dict:
        """Cargar estado actual del bot"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM estado WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return self._estado_default()
    
    def guardar_estado(self, estado: Dict):
        """Guardar estado del bot"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE estado SET
                posicion_abierta = ?,
                precio_compra = ?,
                cantidad = ?,
                max_precio = ?,
                pnl_acumulado = ?,
                operaciones_hoy = ?,
                ultimo_update = ?
            WHERE id = 1
        """, (
            estado['posicion_abierta'],
            estado.get('precio_compra', 0),
            estado.get('cantidad', 0),
            estado.get('max_precio', 0),
            estado.get('pnl_acumulado', 0.0),
            estado.get('operaciones_hoy', 0),
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def _estado_default(self) -> Dict:
        """Estado por defecto"""
        return {
            "posicion_abierta": False,
            "precio_compra": 0,
            "cantidad": 0,
            "max_precio": 0,
            "pnl_acumulado": 0.0,
            "operaciones_hoy": 0
        }
    
    # ===== MÉTRICAS =====
    
    def actualizar_metricas_diarias(self, fecha: str = None):
        """Calcular y guardar métricas del día"""
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        
        # Obtener trades del día
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as ganadoras,
                SUM(CASE WHEN pnl_usd <= 0 THEN 1 ELSE 0 END) as perdedoras,
                SUM(pnl_usd) as pnl_total_usd,
                AVG(pnl_pct) as pnl_total_pct,
                AVG(CASE WHEN pnl_usd > 0 THEN pnl_usd ELSE NULL END) as ganancia_prom,
                AVG(CASE WHEN pnl_usd <= 0 THEN pnl_usd ELSE NULL END) as perdida_prom,
                MAX(pnl_usd) as max_ganancia,
                MIN(pnl_usd) as max_perdida
            FROM trades
            WHERE date(timestamp_venta) = ?
        """, (fecha,))
        
        row = cursor.fetchone()
        
        if row['total'] > 0:
            win_rate = (row['ganadoras'] / row['total']) * 100 if row['total'] > 0 else 0
            
            # Profit Factor = Ganancias Totales / Pérdidas Totales
            ganancias_totales = cursor.execute("""
                SELECT SUM(pnl_usd) FROM trades
                WHERE date(timestamp_venta) = ? AND pnl_usd > 0
            """, (fecha,)).fetchone()[0] or 0
            
            perdidas_totales = abs(cursor.execute("""
                SELECT SUM(pnl_usd) FROM trades
                WHERE date(timestamp_venta) = ? AND pnl_usd <= 0
            """, (fecha,)).fetchone()[0] or 0)
            
            profit_factor = ganancias_totales / perdidas_totales if perdidas_totales > 0 else 0
            
            # Guardar métricas
            cursor.execute("""
                INSERT OR REPLACE INTO metricas_diarias (
                    fecha, operaciones_total, operaciones_ganadoras, operaciones_perdedoras,
                    pnl_total_usd, pnl_total_pct, win_rate, ganancia_promedio,
                    perdida_promedio, profit_factor, max_ganancia, max_perdida
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha,
                row['total'],
                row['ganadoras'],
                row['perdedoras'],
                row['pnl_total_usd'],
                row['pnl_total_pct'],
                win_rate,
                row['ganancia_prom'],
                row['perdida_prom'],
                profit_factor,
                row['max_ganancia'],
                row['max_perdida']
            ))
            self.conn.commit()
    
    def obtener_metricas_diarias(self, fecha: str = None) -> Optional[Dict]:
        """Obtener métricas de un día específico"""
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM metricas_diarias WHERE fecha = ?", (fecha,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def obtener_estadisticas_globales(self) -> Dict:
        """Obtener estadísticas globales de todos los trades"""
        cursor = self.conn.cursor()
        
        stats = cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as ganadoras,
                SUM(CASE WHEN pnl_usd <= 0 THEN 1 ELSE 0 END) as perdedoras,
                SUM(pnl_usd) as pnl_total,
                AVG(pnl_pct) as pnl_promedio,
                MAX(pnl_usd) as mejor_trade,
                MIN(pnl_usd) as peor_trade,
                AVG(duracion_minutos) as duracion_promedio
            FROM trades
        """).fetchone()
        
        if stats and stats['total_trades'] > 0:
            return {
                'total_trades': stats['total_trades'],
                'ganadoras': stats['ganadoras'],
                'perdedoras': stats['perdedoras'],
                'win_rate': (stats['ganadoras'] / stats['total_trades']) * 100,
                'pnl_total': stats['pnl_total'],
                'pnl_promedio': stats['pnl_promedio'],
                'mejor_trade': stats['mejor_trade'],
                'peor_trade': stats['peor_trade'],
                'duracion_promedio': stats['duracion_promedio']
            }
        
        return {
            'total_trades': 0,
            'ganadoras': 0,
            'perdedoras': 0,
            'win_rate': 0.0,
            'pnl_total': 0.0,
            'pnl_promedio': 0.0,
            'mejor_trade': 0.0,
            'peor_trade': 0.0,
            'duracion_promedio': 0.0
        }
    
    def cerrar(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Conexión a base de datos cerrada")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cerrar()


# ===== FUNCIONES DE COMPATIBILIDAD CON memoria.py =====

_db_instance = None

def get_db() -> Database:
    """Obtener instancia singleton de la base de datos"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def cargar_estado() -> Dict:
    """Función de compatibilidad con memoria.py"""
    return get_db().cargar_estado()


def guardar_estado(estado: Dict):
    """Función de compatibilidad con memoria.py"""
    get_db().guardar_estado(estado)


if __name__ == "__main__":
    # Test básico
    logging.basicConfig(level=logging.INFO)
    
    with Database("test_argos.db") as db:
        # Test estado
        estado = db.cargar_estado()
        print("Estado inicial:", estado)
        
        estado['posicion_abierta'] = True
        estado['precio_compra'] = 90000
        db.guardar_estado(estado)
        
        estado_cargado = db.cargar_estado()
        print("Estado guardado:", estado_cargado)
        
        # Test trade
        trade = {
            'timestamp_compra': datetime.now().isoformat(),
            'timestamp_venta': datetime.now().isoformat(),
            'precio_compra': 90000,
            'precio_venta': 91000,
            'cantidad': 0.01,
            'pnl_usd': 10.0,
            'pnl_pct': 1.11,
            'razon_salida': 'Take Profit',
            'max_precio': 91500,
            'duracion_minutos': 45
        }
        db.guardar_trade(trade)
        
        trades = db.obtener_trades(limit=10)
        print(f"\nTrades guardados: {len(trades)}")
        
        # Test estadísticas
        stats = db.obtener_estadisticas_globales()
        print("\nEstadísticas globales:", stats)
    
    # Limpiar test
    if os.path.exists("test_argos.db"):
        os.remove("test_argos.db")
    
    print("\n✅ Tests de database.py completados")
