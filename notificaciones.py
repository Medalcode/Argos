import requests
import os


def enviar_telegram(mensaje, tipo="info"):
    """
    Envía una notificación al chat de Telegram configurado en las variables de entorno.
    tipo: "info", "error", "warning", "success"
    """
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print(f"⚠️ Telegram no configurado. Mensaje no enviado: {mensaje}")
        return

    # Emoji según tipo
    prefix = {
        "info": "ℹ️",
        "error": "❌",
        "warning": "⚠️",
        "success": "✅"
    }.get(tipo, "ℹ️")
    texto = f"{prefix} {mensaje}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': texto,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error enviando a Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción al enviar a Telegram: {e}")

def enviar_alerta_error(mensaje):
    enviar_telegram(mensaje, tipo="error")
