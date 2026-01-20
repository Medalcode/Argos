from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import pandas as pd
import json
import os

app = FastAPI(title="Argos Dashboard")

# Configurar directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(BASE_DIR, "..", "data", "argos.db") # En Docker será /app/data/argos.db

# Montar estáticos y plantillas
if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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
