# 🤖 ARGOS Trading Bot (V7 Ultimate)

Argos es un bot de trading algorítmico profesional diseñado para operar en **Binance Spot**. Combina múltiples indicadores técnicos para entradas precisas y una gestión de riesgo dinámica para proteger el capital.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

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
- Bot de Telegram (Token y Chat ID)

### 1. Clonar y Configurar

```bash
git clone https://github.com/Medalcode/Argos.git
cd Argos
pip install -r requirements.txt
```

### 2. Variables de Entorno (`.env`)

Renombra `.env.example` a `.env` y configura tus claves:

```ini
# Credenciales API
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key
TELEGRAM_TOKEN=tu_telegram_token
TELEGRAM_CHAT_ID=tu_telegram_id

# Configuración del Bot
SYMBOL=BTC/USDT

# Estrategia
STOP_LOSS_PCT=0.01          # 1% Pérdida Máxima
TAKE_PROFIT_PCT=0.015       # 1.5% Meta Inicial (Trailing lo puede extender)
TRAILING_STOP_PCT=0.005     # 0.5% Distancia de seguimiento
POSITION_SIZE_PCT=0.95      # Usar 95% del saldo disponible por trade

# Modos
SIMULATION_MODE=True        # True = Dinero Ficticio, False = Dinero Real
```

### 3. Ejecutar

```bash
python main.py
```

O en segundo plano (Linux):

```bash
nohup python -u main.py > bot.log 2>&1 &
```

---

## 🐳 Ejecución con Docker (Recomendado)

Olvídate de instalar Python o librerías. Corre el bot en un contenedor aislado.

1.  **Construir imagen:**

    ```bash
    docker build -t argos-bot .
    ```

2.  **Correr contenedor:**
    ```bash
    docker run -d --name argos --env-file .env --restart unless-stopped argos-bot
    ```

---

## 📊 Backtesting

¿Quieres saber cuánto habría ganado esta estrategia el mes pasado?

```bash
python backtest.py
```

Este script descarga datos históricos de Binance y simula la estrategia minuto a minuto, dándote un reporte detallado de rentabilidad y Win Rate.

---

## ⚠️ Disclaimer (Aviso Legal)

Este software es para fines educativos y experimentales. El trading de criptomonedas conlleva un alto riesgo de pérdida de capital.

- **Argos** no garantiza ganancias.
- El autor no se hace responsable de pérdidas financieras derivadas del uso de este bot.
- Usa **Modo Simulación** hasta que entiendas completamente cómo opera el bot.
