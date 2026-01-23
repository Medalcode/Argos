import subprocess
import time
import os
import json
from notificaciones import enviar_telegram
import sqlite3

# Configuración dinámica de procesos
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "procesos_config.json")
def cargar_procesos():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)
DB_PATH = os.getenv("ARGOS_DB_PATH", "argos.db")
COOLDOWN = 30  # segundos entre reinicios para evitar bucles


def log_evento(evento, detalle=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                evento TEXT,
                detalle TEXT
            )
        """)
        c.execute("INSERT INTO eventos (evento, detalle) VALUES (?, ?)", (evento, detalle))
        conn.commit()
        conn.close()
    except Exception as e:
        from notificaciones import enviar_alerta_error
        enviar_alerta_error(f"Error al registrar evento: {e}")


def lanzar_proceso(comando):
    return subprocess.Popen(comando)



def main():
    procesos = {}
    cooldowns = {}
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    while True:
        PROCESOS = cargar_procesos()
        for proc in PROCESOS:
            nombre = proc["nombre"]
            comando = proc["comando"]
            p = procesos.get(nombre)
            if nombre not in cooldowns:
                cooldowns[nombre] = 0
            signal_file = os.path.join(BASE_DIR, f"dashboard/restart_{nombre}.sig")
            # Si existe archivo de señal, reiniciar forzadamente
            if os.path.exists(signal_file):
                if p:
                    try:
                        p.terminate()
                        p.wait(timeout=5)
                    except Exception:
                        p.kill()
                procesos[nombre] = lanzar_proceso(comando)
                msg = f"♻️ Proceso {nombre} reiniciado por dashboard."
                enviar_telegram(msg, tipo="success")
                log_evento("reinicio_dashboard", f"{nombre} reiniciado por dashboard")
                cooldowns[nombre] = time.time() + COOLDOWN
                os.remove(signal_file)
                continue
            # Si proceso murió, reiniciar normalmente
            if not p or p.poll() is not None:
                ahora = time.time()
                if ahora < cooldowns[nombre]:
                    continue  # Cooldown activo
                procesos[nombre] = lanzar_proceso(comando)
                msg = f"🔄 Proceso {nombre} reiniciado."
                enviar_telegram(msg, tipo="info")
                log_evento("reinicio", f"{nombre} reiniciado")
                cooldowns[nombre] = ahora + COOLDOWN
        time.sleep(5)

if __name__ == "__main__":
    main()
