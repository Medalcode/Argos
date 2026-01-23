@app.get("/api/procesos")
async def get_procesos(auth: bool = Depends(check_auth)):
    try:
        config_path = os.path.join(BASE_DIR, "..", "procesos_config.json")
        with open(config_path, "r") as f:
            procesos = json.load(f)
        return procesos
    except Exception as e:
        return []

@app.post("/api/procesos/update")
async def update_procesos(procesos: list, auth: bool = Depends(check_auth)):
    try:
        config_path = os.path.join(BASE_DIR, "..", "procesos_config.json")
        with open(config_path, "w") as f:
            json.dump(procesos, f, indent=2)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
from fastapi import Query
@app.get("/api/eventos/filter")
async def filter_eventos(
    tipo: str = Query(None),
    desde: str = Query(None),
    hasta: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: bool = Depends(check_auth)):
    try:
        conn = get_db_connection()
        query = "SELECT * FROM eventos WHERE 1=1"
        params = []
        if tipo:
            query += " AND evento = ?"
            params.append(tipo)
        if desde:
            query += " AND timestamp >= ?"
            params.append(desde)
        if hasta:
            query += " AND timestamp <= ?"
            params.append(hasta)
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([page_size, (page-1)*page_size])
        eventos = pd.read_sql_query(query, conn, params=params).to_dict('records')
        conn.close()
        return eventos
    except Exception as e:
        return []
from fastapi.responses import StreamingResponse
import io
@app.get("/api/eventos/export")
async def export_eventos(auth: bool = Depends(check_auth)):
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM eventos ORDER BY timestamp DESC", conn)
        conn.close()
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=eventos.csv"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
import psutil
@app.get("/api/health")
async def api_health(auth: bool = Depends(check_auth)):
    # Procesos monitoreados
    try:
        with open(os.path.join(BASE_DIR, "..", "procesos_config.json"), "r") as f:
            monitored = [p["nombre"] for p in json.load(f)]
    except Exception:
        monitored = ["main.py", "memoria.py"]
    status_list = []
    for proc_name in monitored:
        found = False
        for p in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc_name in ' '.join(p.info.get('cmdline', [])):
                    found = True
                    break
            except Exception:
                continue
        status_list.append({"name": proc_name, "running": found})
    return status_list
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3
import pandas as pd
import json
import os
import subprocess
from fastapi import status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI(title="Argos Dashboard")
security = HTTPBasic()
USERNAME = os.getenv("ARGOS_DASH_USER", "admin")
PASSWORD = os.getenv("ARGOS_DASH_PASS", "argos123")

def get_db_connection():
    # En desarrollo local puede que la DB no esté en ../data
    db_path = DB_PATH
    if not os.path.exists(db_path):
        # Fallback para desarrollo local fuera de Docker
        local_db = os.path.join(BASE_DIR, "..", "argos.db")
        if os.path.exists(local_db):
            db_path = local_db
            
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Acceso denegado", headers={"WWW-Authenticate": "Basic"})
    return True

# --- Watchdog control ---
WATCHDOG_PATH = os.path.join(BASE_DIR, "..", "watchdog.py")
def restart_process(process_name):
    # Simple signal: create a file that watchdog.py will check and act upon
    signal_file = os.path.join(BASE_DIR, f"restart_{process_name}.sig")
    with open(signal_file, "w") as f:
        f.write("restart")
    return True

@app.post("/api/restart/{process_name}")
async def api_restart_process(process_name: str, auth: bool = Depends(check_auth)):
    try:
        ok = restart_process(process_name)
        if ok:
            return {"status": "ok", "message": f"Reinicio solicitado para {process_name}"}
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"status": "error", "message": "No se pudo reiniciar"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": "error", "message": str(e)})

@app.get("/api/eventos")
async def api_eventos():
    try:
        conn = get_db_connection()
        eventos = pd.read_sql_query("SELECT * FROM eventos ORDER BY timestamp DESC LIMIT 100", conn).to_dict('records')
        conn.close()
        return eventos
    except Exception as e:
        return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, auth: bool = Depends(check_auth)):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/history")
async def get_history():
    """Devuelve las velas OHLCV para el gráfico"""
    try:
        conn = get_db_connection()
        # Leemos la tabla 'precios' que guarda el histórico de monitoreo
        # Limitamos a 1000 velas para no saturar
        df = pd.read_sql_query("SELECT timestamp, precio as close FROM precios ORDER BY timestamp DESC LIMIT 2000", conn)
        conn.close()
        
        # Como argos guarda ticks, esto es una aproximación visual. 
        # Idealmente Argos debería guardar velas OHLCV reales en la DB.
        # Por ahora enviamos los ticks como línea simple o velas simuladas.
        
        # Para visualización correcta, necesitamos transformar timestamp ISO a unix timestamp (segundos)
        df['time'] = pd.to_datetime(df['timestamp']).astype('int64') // 10**9
        df = df.sort_values('time')
        
        # Formato Lightweight Charts (LineSeries)
        data = df[['time', 'close']].to_dict('records')
        return {"data": data}
    except Exception as e:
        return {"error": str(e), "data": []}

@app.get("/api/trades")
async def get_trades():
    """Devuelve los trades ejecutados"""
    try:
        conn = get_db_connection()
        trades = pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp_venta DESC LIMIT 50", conn).to_dict('records')
        conn.close()
        return trades
    except Exception as e:
        return []

@app.get("/api/stats")
async def get_stats():
    """Devuelve estadísticas rápidas"""
    try:
        conn = get_db_connection()
        # Obtener último estado
        estado = pd.read_sql_query("SELECT * FROM estado LIMIT 1", conn).iloc[0].to_dict()
        conn.close()
        return estado
    except:
        return {"posicion_abierta": False, "pnl_acumulado": 0.0}
