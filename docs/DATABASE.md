# Base de Datos SQLite - Argos Trading Bot

## 📋 Descripción

Sistema de base de datos SQLite para gestionar persistencia de datos del bot, reemplazando los archivos CSV con una solución robusta y escalable.

---

## 🗄️ Esquema de Base de Datos

### Tabla: `trades`
Almacena operaciones completadas (compra + venta).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | ID autoincremental |
| `timestamp_compra` | TEXT | Fecha/hora de compra (ISO 8601) |
| `timestamp_venta` | TEXT | Fecha/hora de venta (ISO 8601) |
| `precio_compra` | REAL | Precio de compra en USDT |
| `precio_venta` | REAL | Precio de venta en USDT |
| `cantidad` | REAL | Cantidad de BTC |
| `pnl_usd` | REAL | PnL en USD |
| `pnl_pct` | REAL | PnL en porcentaje |
| `razon_salida` | TEXT | Razón de salida (TP/SL/Trailing) |
| `max_precio` | REAL | Precio máximo alcanzado |
| `trailing_pct` | REAL | % de trailing stop usado |
| `rsi_compra` | REAL | RSI al momento de compra |
| `duracion_minutos` | INTEGER | Duración del trade |

**Índice**: `idx_trades_timestamp` en `timestamp_venta`

---

### Tabla: `senales`
Registra todas las evaluaciones de entrada/salida (para análisis posterior).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | ID autoincremental |
| `timestamp` | TEXT | Fecha/hora de la señal |
| `tipo` | TEXT | COMPRA o VENTA |
| `precio` | REAL | Precio al momento de la señal |
| `rsi` | REAL | RSI calculado |
| `bb_lower` | REAL | Banda Bollinger inferior |
| `bb_middle` | REAL | Banda Bollinger media |
| `bb_upper` | REAL | Banda Bollinger superior |
| `ema` | REAL | EMA calculada |
| `posicion_abierta` | INTEGER | 1 si hay posición, 0 si no |
| `balance_usdt` | REAL | Balance disponible |
| `razon` | TEXT | Razón de la señal |

**Índice**: `idx_senales_timestamp` en `timestamp`

---

### Tabla: `precios`
Histórico de precios BTC/USDT cada 60 segundos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | ID autoincremental |
| `timestamp` | TEXT | Fecha/hora del precio |
| `precio` | REAL | Precio en USDT |
| `volumen` | REAL | Volumen de trading |

**Índice**: `idx_precios_timestamp` en `timestamp`

---

### Tabla: `metricas_diarias`
Métricas agregadas por día.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | ID autoincremental |
| `fecha` | TEXT | Fecha (YYYY-MM-DD) UNIQUE |
| `operaciones_total` | INTEGER | Total de trades |
| `operaciones_ganadoras` | INTEGER | Trades con PnL > 0 |
| `operaciones_perdedoras` | INTEGER | Trades con PnL ≤ 0 |
| `pnl_total_usd` | REAL | PnL total en USD |
| `pnl_total_pct` | REAL | PnL total en % |
| `win_rate` | REAL | Win rate del día |
| `ganancia_promedio` | REAL | Ganancia promedio |
| `perdida_promedio` | REAL | Pérdida promedio |
| `profit_factor` | REAL | Ganancias / Pérdidas |
| `max_ganancia` | REAL | Mejor trade del día |
| `max_perdida` | REAL | Peor trade del día |

---

### Tabla: `estado`
Estado actual del bot (reemplaza estado.json).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Siempre 1 (singleton) |
| `posicion_abierta` | INTEGER | 1 si hay posición, 0 si no |
| `precio_compra` | REAL | Precio de compra actual |
| `cantidad` | REAL | Cantidad de BTC en posición |
| `max_precio` | REAL | Máximo precio para trailing |
| `pnl_acumulado` | REAL | PnL acumulado del día |
| `operaciones_hoy` | INTEGER | Operaciones realizadas hoy |
| `ultimo_update` | TEXT | Última actualización |

---

## 📦 API - Clase `Database`

### Inicialización
```python
from database import Database

# Uso directo
db = Database()  # Crea/conecta a argos.db

# Context manager (recomendado)
with Database() as db:
    # ... operaciones ...
    pass  # Se cierra automáticamente
```

### Métodos: Trades

```python
# Guardar trade completado
trade = {
    'timestamp_compra': '2026-01-07T10:00:00',
    'timestamp_venta': '2026-01-07T12:30:00',
    'precio_compra': 90000,
    'precio_venta': 91000,
    'cantidad': 0.01,
    'pnl_usd': 10.0,
    'pnl_pct': 1.11,
    'razon_salida': 'Take Profit',
    'max_precio': 91500,
    'duracion_minutos': 150
}
trade_id = db.guardar_trade(trade)

# Obtener últimos trades
trades = db.obtener_trades(limit=100)

# Obtener trades del día actual
trades_hoy = db.obtener_trades_hoy()
```

### Métodos: Señales

```python
# Guardar señal
senal = {
    'timestamp': '2026-01-07T10:00:00',
    'tipo': 'COMPRA',
    'precio': 90000,
    'rsi': 32.5,
    'bb_lower': 89500,
    'ema': 89000,
    'posicion_abierta': False,
    'balance_usdt': 1000.0,
    'razon': 'Triple Filtro cumplido'
}
senal_id = db.guardar_senal(senal)

# Obtener últimas señales
senales = db.obtener_senales(limit=100)
```

### Métodos: Precios

```python
# Guardar precio histórico
db.guardar_precio('2026-01-07T10:00:00', 90000, volumen=125.5)

# Obtener precios recientes
precios = db.obtener_precios_recientes(horas=24)
```

### Métodos: Estado

```python
# Cargar estado actual
estado = db.cargar_estado()
print(estado['posicion_abierta'])

# Guardar estado
estado['posicion_abierta'] = True
estado['precio_compra'] = 90000
estado['cantidad'] = 0.01
db.guardar_estado(estado)
```

### Métodos: Métricas

```python
# Actualizar métricas del día actual
db.actualizar_metricas_diarias()

# Actualizar métricas de fecha específica
db.actualizar_metricas_diarias('2026-01-07')

# Obtener métricas de un día
metricas = db.obtener_metricas_diarias('2026-01-07')

# Obtener estadísticas globales
stats = db.obtener_estadisticas_globales()
print(f"Win Rate Global: {stats['win_rate']:.2f}%")
```

---

## 🔄 Migración desde CSV

Si tienes datos en `operaciones.csv`, puedes migrarlos automáticamente:

```bash
python migrate_to_sqlite.py
```

El script:
1. Lee todos los trades del CSV
2. Los inserta en SQLite
3. Calcula métricas diarias
4. Crea backup del CSV original
5. Muestra estadísticas globales

---

## 🔗 Retrocompatibilidad con `memoria.py`

Para mantener compatibilidad con código existente, `database.py` exporta funciones compatibles:

```python
from database import cargar_estado, guardar_estado

# Funciona igual que memoria.py
estado = cargar_estado()
estado['posicion_abierta'] = True
guardar_estado(estado)
```

Internamente usa SQLite en lugar de JSON.

---

## 🛠️ Herramientas de Administración

### Ver contenido de la base de datos

```bash
# Abrir con sqlite3
sqlite3 argos.db

# Comandos útiles
.tables                          # Ver tablas
.schema trades                   # Ver esquema de trades
SELECT COUNT(*) FROM trades;     # Contar trades
SELECT * FROM trades LIMIT 10;   # Ver últimos 10 trades
.exit                            # Salir
```

### Backup de la base de datos

```bash
# Backup simple
cp argos.db argos_backup_$(date +%Y%m%d).db

# Backup con dump SQL
sqlite3 argos.db .dump > argos_backup.sql
```

### Restaurar desde backup

```bash
# Desde archivo .db
cp argos_backup_20260107.db argos.db

# Desde dump SQL
sqlite3 argos.db < argos_backup.sql
```

---

## 📊 Consultas Útiles

### Top 10 mejores trades
```sql
SELECT timestamp_venta, pnl_usd, pnl_pct, razon_salida
FROM trades
ORDER BY pnl_usd DESC
LIMIT 10;
```

### Win rate por día
```sql
SELECT 
    date(timestamp_venta) as fecha,
    COUNT(*) as total,
    SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
FROM trades
GROUP BY date(timestamp_venta)
ORDER BY fecha DESC;
```

### PnL acumulado por día
```sql
SELECT 
    date(timestamp_venta) as fecha,
    SUM(pnl_usd) OVER (ORDER BY timestamp_venta) as pnl_acumulado
FROM trades
ORDER BY fecha;
```

---

## 🎯 Ventajas sobre CSV

| Característica | CSV | SQLite |
|----------------|-----|--------|
| **Consultas complejas** | ❌ | ✅ |
| **Índices para velocidad** | ❌ | ✅ |
| **Transacciones ACID** | ❌ | ✅ |
| **Integridad de datos** | ❌ | ✅ |
| **Relaciones entre tablas** | ❌ | ✅ |
| **Concurrencia** | ❌ | ✅ |
| **Tamaño eficiente** | ❌ | ✅ |
| **Backup fácil** | ✅ | ✅ |

---

## ⚙️ Configuración

Cambiar ubicación de la base de datos:

```bash
# En .env
DB_FILE=custom_argos.db
```

O en código:

```python
from database import Database

db = Database("custom_argos.db")
```

---

**Documentación generada**: 7 de enero de 2026  
**Versión del Bot**: 2.3.0  
**Motor**: SQLite 3
