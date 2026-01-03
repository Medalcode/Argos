# 👁️ ARGOS - Bitcoin Trading Bot

Argos es un bot de trading algorítmico automatizado diseñado para operar en el mercado de criptomonedas (específicamente Bitcoin/USDT) utilizando estrategias de análisis técnico robustas y gestión de riesgos automatizada.

El sistema opera 24/7, monitoreando el mercado en tiempo real y ejecutando operaciones basadas en el indicador RSI (Relative Strength Index), protegiendo el capital con Stop Loss y asegurando ganancias con Take Profit.

## 🚀 Características Principales

- **Estrategia RSI Automática**: Compra en zonas de sobreventa (RSI < 30) para capturar "dips".
- **Gestión de Riesgo Integrada**:
  - 🛡️ **Stop Loss (2%)**: Cierra posiciones automáticamente si el mercado se vuelve en contra.
  - 💰 **Take Profit (4%)**: Asegura ganancias automáticamente cuando se alcanza el objetivo.
- **Notificaciones en Tiempo Real**: Envía alertas a Telegram sobre cada compra, venta y estado del bot.
- **Persistencia de Estado**: Sistema de memoria (`JSON`) capaz de recordar operaciones abiertas incluso si el servidor se reinicia.
- **Heartbeat Monitor**: Verificación de vida cada 12 horas para asegurar que el sistema sigue operativo.

## 📋 Requisitos Previos

- Python 3.10 o superior.
- Cuenta en Binance (API Key & Secret).
- Cuenta de Telegram (Bot Token & Chat ID).

## 🛠️ Instalación

1.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/tu-usuario/argos.git
    cd argos
    ```

2.  **Crear un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuración

1.  Crea un archivo `.env` en la raíz del proyecto (puedes copiar el ejemplo):

    ```bash
    cp .env.example .env
    ```

2.  Edita el archivo `.env` con tus credenciales:

    ```env
    # Credenciales de Binance
    BINANCE_API_KEY=tu_api_key_aqui
    BINANCE_SECRET_KEY=tu_secret_key_aqui

    # Configuración de Telegram
    TELEGRAM_TOKEN=tu_token_de_botfather
    TELEGRAM_CHAT_ID=tu_id_de_usuario

    # Parámetros de la Estrategia
    SYMBOL=BTC/USDT
    STOP_LOSS_PCT=0.02  # 2%
    TAKE_PROFIT_PCT=0.04 # 4%
    ```

## ▶️ Uso

Para iniciar el bot en segundo plano verificado (recomendado para servidores):

```bash
# Activa el entorno (si no lo está)
source venv/bin/activate

# Ejecuta el bot
python main.py
```

Deberías recibir inmediatamente un mensaje en Telegram confirmando el inicio:

> 🤖 **Argos Bot Iniciado**
> Par: BTC/USDT ...

## ⚠️ Aviso de Responsabilidad

Este software es para fines educativos y experimentales. El trading de criptomonedas conlleva un alto riesgo de pérdida financiera.

- Usa siempre una gestión de riesgo adecuada.
- Nunca inviertas dinero que no puedas permitirte perder.
- El autor no se hace responsable de las pérdidas generadas por el uso de este software.

---

_Desarrollado con ❤️ por MedalCode_
