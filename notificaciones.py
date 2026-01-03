import requests
import os

def enviar_telegram(mensaje):
    """
    Envía una notificación al chat de Telegram configurado en las variables de entorno.
    """
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print(f"⚠️ Telegram no configurado. Mensaje no enviado: {mensaje}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': mensaje,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Error enviando a Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción al enviar a Telegram: {e}")
