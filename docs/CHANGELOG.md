# Changelog - Argos Trading Bot

## [2.3.0] - 7 de enero de 2026

### 🧪 Suite de Tests Unitarios
- **28 tests implementados con pytest** (100% éxito)
- Tests de indicadores técnicos (RSI, Bollinger Bands, EMA)
- Tests de lógica de trading (Triple Filtro, Trailing Stop, PnL)
- Tests de persistencia (memoria.py con 100% de cobertura)
- Fixtures con mocks de CCXT exchange
- Configuración con pyproject.toml
- Generación de reportes de cobertura HTML
- Documentación en [TESTING.md](TESTING.md)

### 🗄️ Migración a Base de Datos SQLite
- **Reemplazo de CSV por SQLite** para mejor gestión de datos
- Esquema completo con 5 tablas:
  - `trades`: Operaciones completadas con métricas
  - `senales`: Histórico de señales de entrada/salida
  - `precios`: Histórico de precios cada 60s
  - `metricas_diarias`: Métricas agregadas por día
  - `estado`: Estado del bot (reemplaza JSON)
- Script de migración automática desde CSV
- Índices para optimización de consultas
- API completa con Database class
- Retrocompatible con memoria.py

### 📊 Métricas Avanzadas de Performance
- **Sharpe Ratio**: Retorno ajustado por riesgo (anualizado)
- **Maximum Drawdown**: Mayor caída desde pico histórico
- **Profit Factor**: Ratio ganancias/pérdidas
- **Expectancy**: Valor esperado por trade en USD
- **Recovery Factor**: Capacidad de recuperación post-drawdown
- **MAE/MFE**: Maximum Adverse/Favorable Excursion
- **Win Rate por periodo**: Diario, semanal, mensual
- Interpretaciones automáticas de cada métrica
- Reporte completo con `generar_reporte_completo()`

### 📝 Documentación
- [TESTING.md](TESTING.md): Guía completa de tests
- [DATABASE.md](DATABASE.md): Esquema y API de base de datos
- [METRICAS.md](METRICAS.md): Explicación de métricas de performance

---

## [2.2.0] - 7 de enero de 2026

### 🎨 Dashboard Visual con Rich
- **Dashboard interactivo en terminal** con biblioteca Rich
- Tabla visual con métricas en tiempo real:
  - 💰 Precio BTC/USDT con actualización en vivo
  - 📊 RSI con codificación de colores (rojo < 35, amarillo < 70, verde ≥ 70)
  - 📈 EMA con indicador de tendencia (🐂 Alcista / 🐻 Bajista)
  - 🎯 Estado de posición (abierta/cerrada con PnL)
  - 🛡️ Trailing Stop cuando hay posición activa
- Banner de inicio profesional con información del sistema
- Actualizaciones cada 60 segundos con limpieza de pantalla
- Indicador de última actualización y próximo refresh

### 📝 Mejoras en el Sistema de Logging
- Logs estructurados con niveles DEBUG/INFO/WARNING/ERROR
- Stack traces completos para debugging (`exc_info=True`)
- Separación de logs: archivo detallado + consola limpia
- Formato estandarizado: `[timestamp] - [nivel] - [mensaje]`

### 🎯 Optimizaciones de UX
- Output limpio sin scroll infinito
- Colores semánticos para estados críticos
- Emojis informativos para mejor lectura visual
- Mensajes claros de eventos (compra/venta con separación visual)

---

## [2.0.0] - 7 de enero de 2026

### ✅ Implementación de Trading Real
- **BREAKING**: Habilitadas órdenes reales al exchange de Binance
- Descomentada `create_market_buy_order()` para compras
- Implementada `create_market_sell_order()` para ventas (Trailing Stop, Take Profit, Stop Loss)
- Captura de precio real de ejecución para mayor precisión

### 🛡️ Mejoras de Seguridad y Validación
- Agregado manejo específico de excepciones CCXT:
  - `InsufficientFunds` - Fondos insuficientes
  - `InvalidOrder` - Orden inválida
  - `NetworkError` - Problemas de conexión
  - `ExchangeError` - Errores del exchange
- Implementada validación de mínimo notional de Binance
- Verificación automática de límites desde `exchange.markets`
- Prevención de órdenes por montos menores a ~$10 USD

### ⚙️ Configuración
- Agregadas variables faltantes en `.env.example`:
  - `TRAILING_STOP_PCT=0.005`
  - `POSITION_SIZE_PCT=0.95`
  - `SIMULATION_MODE=True`
- Comentarios explicativos para cada parámetro
- Creado archivo `.env.testnet` para testing

### 📦 Dependencias
- Versionadas todas las dependencias en `requirements.txt`:
  - `ccxt>=4.0.0,<5.0.0`
  - `pandas>=2.0.0,<3.0.0`
  - `pandas_ta>=0.3.14b`
  - `python-dotenv>=1.0.0`
  - `requests>=2.31.0`
- Garantiza reproducibilidad y evita incompatibilidades

### 🧪 Testing
- Creada guía completa de testing en `TESTING_GUIDE.md`
- Documentación paso a paso para Binance Testnet
- Checklist de validación con 17 puntos
- Troubleshooting de errores comunes
- Instrucciones de migración a producción

### 🔧 Optimizaciones Técnicas
- Ajustado EMA de 200 a 20 para compatibilidad con Binance Testnet
- Incrementado límite de velas de 300 a 500 (mejorado a 20 por limitaciones de testnet)
- Agregados mensajes de debug informativos
- Habilitado modo sandbox para testing seguro

### 📊 Backtest Mejorado
- **Sincronizado con estrategia real del bot**
- Implementado Triple Filtro completo:
  - RSI < 35 (sobreventa)
  - Precio < Banda Bollinger Inferior
  - Precio > EMA (tendencia alcista)
- Agregado Trailing Stop dinámico
- Cálculo de máximo precio histórico
- Resultados más representativos de operación real

### 📝 Documentación
- Actualizado README con información de testing
- Creado CHANGELOG.md para tracking de cambios
- Documentadas limitaciones del testnet
- Agregadas notas sobre diferencias EMA 20 vs EMA 200

---

## [1.0.0] - Versión Inicial

### Características
- Bot de trading automatizado para Binance Spot
- Estrategia Triple Filtro (RSI + Bollinger + EMA)
- Trailing Stop dinámico
- Stop Loss y Take Profit
- Notificaciones por Telegram
- Sistema de memoria persistente (JSON)
- Registro de operaciones en CSV
- Modo simulación/paper trading
- Dockerización completa
- Herramientas de backtest y optimización

---

**Nota**: Las versiones están en formato [MAJOR.MINOR.PATCH] siguiendo Semantic Versioning.
