# 🤖 ARGOS Trading Bot v2.3.0

Bot de trading algorítmico profesional para **Binance Spot** con estrategia Triple Filtro, Trailing Stop dinámico, y métricas avanzadas de performance.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Tests](https://img.shields.io/badge/Tests-28%20passed-success.svg)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ⭐ Novedades v2.3.0

- ✅ **28 Tests Unitarios** con pytest (100% éxito)
- ✅ **Base de Datos SQLite** (5 tablas, reemplaza CSV)
- ✅ **8 Métricas Avanzadas** (Sharpe, Max DD, Profit Factor, etc.)
- ✅ **Documentación Completa** (TESTING.md, DATABASE.md, METRICAS.md)

## 🚀 Características Principales

### 🧠 Estrategia Inteligente (Triple Filtro)

Argos no dispara a lo loco. Solo opera cuando se alinean 3 condiciones:

1.  **RSI (Relative Strength Index):** Detecta condiciones de sobreventa (`< 35`).
2.  **Bandas de Bollinger:** Confirma que el precio está estadísticamente "barato" (perforando la banda inferior).
3.  **EMA 200 (Media Móvil Exponencial):** Filtro de tendencia. Solo compra si el precio está por encima de la EMA 200 (Tendencia Alcista). _"The trend is your friend"_.

### 🛡️ Gestión de Riesgo (Risk Management)

- **Trailing Stop:** No se conforma con ganar poco. Persigue el precio hacia arriba (0.5% de distancia) y vende solo cuando detecta un cambio de tendencia, maximizando ganancias en "pumps".
- **Tamaño de Posición Dinámico:** Calcula automáticamente cuánto comprar basado en un % de tu saldo (`POSITION_SIZE_PCT`).
- **Filtro de Saldo:** Verifica fondos antes de operar para evitar errores de API.

### 📡 Control y Notificaciones

- **Interactive Telegram:** Controla el bot desde tu móvil.
  - `/status`: Ver precio, indicadores y posición actual.
  - `/saldo`: Estimación de capital y PnL acumulado.
  - `/vender`: **Botón de Pánico** para vender todo inmediatamente.
- **Reportes Diarios:** Resumen automático cada mañana a las 08:00 AM.
- **Modo Simulación:** Paper Trading integrado para probar estrategias sin dinero real.

---

## 🛠️ Instalación y Uso

### Prerrequisitos

- Python 3.9+
- Cuenta en Binance (Verificada)
### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/Medalcode/Argos.git
cd Argos

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración (`.env`)

Copia `.env.example` a `.env` y configura:

```ini
# Binance API (TESTNET recomendado para empezar)
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key

# Telegram
TELEGRAM_TOKEN=tu_telegram_token
TELEGRAM_CHAT_ID=tu_telegram_id

# Trading
SYMBOL=BTC/USDT
STOP_LOSS_PCT=0.01          # 1% pérdida máxima
TAKE_PROFIT_PCT=0.015       # 1.5% meta inicial
TRAILING_STOP_PCT=0.005     # 0.5% trailing
POSITION_SIZE_PCT=0.95      # 95% del saldo

# Modo
SIMULATION_MODE=False       # True = paper trading
```

### 3. Testing en Testnet (Recomendado)

Sigue la guía completa en [TESTING_GUIDE.md](TESTING_GUIDE.md):

```bash
# 1. Obtener API keys de Binance Testnet
# https://testnet.binance.vision/

# 2. Configurar .env con testnet keys

# 3. Ejecutar bot
python main.py
```

### 4. Ejecutar Tests

```bash
# Tests unitarios
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=. --cov-report=html
```

### 5. Backtest Histórico

```bash
python backtest.py
```

### 6. Métricas de Performance

```bash
python metricas.py
```

---

## 🧪 Testing

El bot incluye una suite completa de tests:

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_trading_logic.py -v
pytest tests/test_indicators.py -v

# Con cobertura HTML
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # Ver reporte
```

**Resultado**: 28 tests, 100% éxito, cobertura 100% en módulos críticos.

Ver [TESTING.md](TESTING.md) para más detalles.

---

## 🗄️ Base de Datos

Sistema SQLite con 5 tablas:

- `trades`: Operaciones completadas
- `senales`: Histórico de señales
- `precios`: Histórico de precios
- `metricas_diarias`: Agregación por día
- `estado`: Estado actual del bot

```python
from database import Database

with Database() as db:
    # Obtener estadísticas
    stats = db.obtener_estadisticas_globales()
    print(f"Win Rate: {stats['win_rate']}%")
```

Ver [DATABASE.md](DATABASE.md) para API completa.

---

## 📊 Métricas de Performance

8 métricas profesionales:

- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Maximum Drawdown**: Mayor caída desde pico
- **Profit Factor**: Ganancias / Pérdidas
- **Expectancy**: Valor esperado por trade
- **Recovery Factor**: Capacidad de recuperación
- **Win Rate por periodo**: Diario/Semanal/Mensual
- **MAE/MFE**: Adverse/Favorable Excursion

```python
from metricas import MetricasPerformance, imprimir_reporte_consola

metricas = MetricasPerformance()
reporte = metricas.generar_reporte_completo(30)
imprimir_reporte_consola(reporte)
```

Ver [METRICAS.md](METRICAS.md) para interpretaciones y benchmarks.

---

## ⚠️ Disclaimer (Aviso Legal)

Este software es para fines educativos y experimentales. El trading de criptomonedas conlleva un alto riesgo de pérdida de capital.

- **Argos** no garantiza ganancias.
- El autor no se hace responsable de pérdidas financieras derivadas del uso de este bot.
- Usa **Modo Simulación** hasta que entiendas completamente cómo opera el bot.
