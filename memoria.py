import json
import os

# Nombre del archivo donde el bot guardará su estado
ESTADO_FILE = "estado_bot.json"

def cargar_estado():
    if os.path.exists(ESTADO_FILE):
        try:
            with open(ESTADO_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass # Si el archivo está corrupto, retorna estado default
            
    return {"posicion_abierta": False, "precio_compra": 0.0, "max_precio": 0.0, "pnl_acumulado": 0.0, "operaciones_hoy": 0}

def guardar_estado(estado):
    with open(ESTADO_FILE, 'w') as f:
        json.dump(estado, f)
