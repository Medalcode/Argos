import os
import sys

# Mock numba if it's missing (common in Termux)
try:
    import numba
except ImportError:
    from unittest.mock import MagicMock
    mock_numba = MagicMock()
    mock_numba.njit = lambda f=None, *args, **kwargs: f if f else lambda x: x
    mock_numba.jit = lambda f=None, *args, **kwargs: f if f else lambda x: x
    sys.modules["numba"] = mock_numba

import time
import requests
import datetime
import ccxt
import pandas as pd
import pandas_ta as ta
import logging
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv
from notificaciones import enviar_telegram 
from memoria import cargar_estado, guardar_estado

# 1. Configuración Inicial
load_dotenv()

# Configurar sistema de logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'argos_bot.log'

# Handler para archivo (max 5MB, mantiene 3 backups)
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Configurar logger
logger = logging.getLogger('ArgosBot')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Configurar Rich Console para dashboard
console = Console()

# Configuración del Exchange (Binance por defecto)
# Se usa 'enableRateLimit': True para respetar los límites de la API
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'} 
})

# Si estamos en modo TESTNET (Sandbox), descomentar las siguientes líneas si el exchange lo soporta
exchange.set_sandbox_mode(True) 

SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')
# Parsear porcentajes
SL = float(os.getenv('STOP_LOSS_PCT', 0.01))
TP = float(os.getenv('TAKE_PROFIT_PCT', 0.015))
TS = float(os.getenv('TRAILING_STOP_PCT', 0.005))
POS_SIZE = float(os.getenv('POSITION_SIZE_PCT', 0.95)) # 95% del saldo
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'True').lower() == 'true'

estado = cargar_estado()
ultima_vez_vivo = datetime.datetime.now()
ultimo_reporte_dia = datetime.datetime.now().day

def verificar_reporte_diario():
    global ultimo_reporte_dia
    ahora = datetime.datetime.now()
    
    # Si cambió de día y son las 8:00 AM (o después)
    if ahora.day != ultimo_reporte_dia and ahora.hour >= 8:
        ops = estado.get("operaciones_hoy", 0)
        pnl = estado.get("pnl_acumulado", 0.0)
        saldo_simulado = 1000 * (1 + pnl/100) # Estimado
        
        msg = f"""📅 **REPORTE DIARIO ARGOS**
-------------------------
🔢 Operaciones: {ops}
💰 PnL del Día: {pnl:+.2f}%
💵 Capital Est.: ${saldo_simulado:.2f}
-------------------------"""
        enviar_telegram(msg)
        logger.info(f"Reporte diario enviado: {ops} operaciones, PnL: {pnl:.2f}%")
        
        # Resetear contadores
        estado["operaciones_hoy"] = 0
        estado["pnl_acumulado"] = 0.0
        guardar_estado(estado)
        
        ultimo_reporte_dia = ahora.day

# Archivo para guardar historial
TRADES_FILE = "trades.csv"

def guardar_trade_csv(fecha, tipo, precio, resultado_pct):
    existe = os.path.isfile(TRADES_FILE)
    with open(TRADES_FILE, 'a') as f:
        # Header si es nuevo
        if not existe:
            f.write("fecha,tipo,precio,resultado_pct,ganancia_usd_estimada\n")
        
        # Asumiendo capital 1000 usd
        ganancia_usd = 1000 * resultado_pct
        f.write(f"{fecha},{tipo},{precio},{resultado_pct:.4f},{ganancia_usd:.2f}\n")
        logger.info(f"Trade guardado: {tipo} a ${precio:.2f}, PnL: {resultado_pct*100:.2f}%")

def registrar_operacion(tipo, precio_venta, pnl_pct):
    # Actualizar Stats en Memoria
    estado["operaciones_hoy"] = estado.get("operaciones_hoy", 0) + 1
    estado["pnl_acumulado"] = estado.get("pnl_acumulado", 0.0) + (pnl_pct * 100)
    
    # Guardar en CSV
    guardar_trade_csv(datetime.datetime.now(), tipo, precio_venta, pnl_pct)

    # Cerrar Posición
    estado["posicion_abierta"] = False
    estado["max_precio"] = 0.0
    guardar_estado(estado)
    
    logger.info(f"{tipo} ejecutado: Precio=${precio_venta:.2f}, PnL={pnl_pct*100:.2f}%")

    # Mensaje Telegram
    icono = "✅" if pnl_pct > 0 else "❌"
    enviar_telegram(f"{icono} **{tipo} EJECUTADO**\nVenta: {precio_venta}\nResultado: {pnl_pct*100:.2f}%")


def check_balance():
    """
    Verifica si tenemos suficiente USDT en la billetera SPOT para operar.
    Retorna True si hay > 15 USDT (mínimo de seguridad).
    """
    try:
        balance = exchange.fetch_balance()
        usdt_free = balance.get('USDT', {}).get('free', 0.0)
        
        if usdt_free < 15: # Binance suele pedir min $10, ponemos $15 por seguridad
            logger.warning(f"Saldo insuficiente: ${usdt_free:.2f} USDT")
            return False
            
        logger.debug(f"Saldo verificado: ${usdt_free:.2f} USDT")
        return True
    except Exception as e:
        logger.error(f"Error verificando saldo: {e}")
        return False # Ante la duda, no operar

def obtener_datos():
    """
    Obtiene las velas y calcula indicadores.
    """
    try:
        # Fetch OHLCV 
        # Testnet tiene datos limitados, usamos lo que nos da
        velas = exchange.fetch_ohlcv(SYMBOL, timeframe='15m', limit=500)
        df = pd.DataFrame(velas, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        
        logger.debug(f"Datos recibidos: {len(df)} velas")
        
        # Calcular RSI 14
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # Calcular Bollinger (20, 2)
        bbands = ta.bbands(df['close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        
        # Calcular EMA 20 (ajustado para testnet con datos limitados)
        # En producción con más datos, cambiar a EMA 200
        df['EMA_200'] = ta.ema(df['close'], length=20)
        
        return df
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}", exc_info=True)
        return pd.DataFrame()

# Variable para no repetir comandos viejos
ultimo_update_id = 0

def procesar_comandos(df_actual):
    global ultimo_update_id
    token = os.getenv('TELEGRAM_TOKEN')
    if not token: return

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {'offset': ultimo_update_id + 1, 'timeout': 1}
    
    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        
        if not data.get('ok'): return
        
        for result in data.get('result', []):
            update_id = result['update_id']
            ultimo_update_id = update_id # Actualizamos para no leerlo de nuevo
            
            message = result.get('message', {})
            texto = message.get('text', '').lower().strip()
            
            if not texto: continue
            
            # --- COMANDO /STATUS ---
            if texto == '/status':
                precio = df_actual['close'].iloc[-1] if not df_actual.empty else 0
                rsi = df_actual['RSI'].iloc[-1] if not df_actual.empty else 0
                pos = "Abierta ✅" if estado["posicion_abierta"] else "Esperando 💤"
                tendencia = "ALCISTA 🐂" if not df_actual.empty and precio > df_actual['EMA_200'].iloc[-1] else "BAJISTA 🐻"
                
                msg = f"""📊 **STATUS ARGOS**
Precio: {precio}
RSI: {rsi:.2f}
Tendencia: {tendencia}
Posición: {pos}
PNL Acum: {estado.get('pnl_acumulado',0):.2f}%"""
                enviar_telegram(msg)

            # --- COMANDO /SALDO ---
            elif texto == '/saldo':
                pnl = estado.get("pnl_acumulado", 0.0)
                saldo_est = 1000 * (1 + pnl/100)
                enviar_telegram(f"💵 **Saldo Estimado:** ${saldo_est:.2f}\nPnL Acumulado: {pnl:.2f}%")

            # --- COMANDO /VENDER (PÁNICO) ---
            elif texto == '/vender':
                if estado["posicion_abierta"]:
                    precio = df_actual['close'].iloc[-1]
                    precio_compra = estado["precio_compra"]
                    pnl_pct = (precio - precio_compra) / precio_compra
                    
                    registrar_operacion("VENTA MANUAL (PÁNICO)", precio, pnl_pct)
                    enviar_telegram("🚨 **VENTA FORZADA EJECUTADA**")
                else:
                    enviar_telegram("⚠️ No hay posición abierta para vender.")
                    
    except Exception as e:
        logger.error(f"Error procesando comandos: {e}", exc_info=True)

def generar_dashboard(precio, rsi, ema, tendencia, posicion_abierta, estado):
    """
    Genera una tabla visual con Rich para mostrar el estado del bot
    """
    # Crear tabla principal
    tabla = Table(title="🤖 ARGOS TRADING BOT - Dashboard", 
                  show_header=True, header_style="bold magenta", border_style="blue",
                  expand=False)
    
    tabla.add_column("Métrica", style="cyan", width=20, no_wrap=True)
    tabla.add_column("Valor", style="yellow", width=22, no_wrap=True)
    tabla.add_column("Estado", style="green", width=18, no_wrap=True)
    
    # Datos de mercado
    tabla.add_row("💰 Precio BTC/USDT", f"${precio:,.2f}", "🔴 LIVE")
    
    # RSI con color según valor
    rsi_color = "red" if rsi < 35 else "yellow" if rsi < 70 else "green"
    rsi_status = "🔥 SOBREVENTA" if rsi < 35 else "⚖️  NEUTRAL" if rsi < 70 else "❄️  SOBRECOMPRA"
    tabla.add_row("📊 RSI (14)", f"[{rsi_color}]{rsi:.2f}[/{rsi_color}]", rsi_status)
    
    # EMA y tendencia
    tendencia_emoji = "🐂" if tendencia == "ALCISTA" else "🐻"
    tendencia_color = "green" if tendencia == "ALCISTA" else "red"
    tabla.add_row("📈 EMA 20", f"${ema:.2f}", f"[{tendencia_color}]{tendencia} {tendencia_emoji}[/{tendencia_color}]")
    
    # Posición
    if posicion_abierta:
        precio_compra = estado.get("precio_compra", 0)
        pnl_pct = ((precio - precio_compra) / precio_compra) * 100 if precio_compra > 0 else 0
        pnl_color = "green" if pnl_pct > 0 else "red"
        tabla.add_row("🎯 Posición", f"✅ ${precio_compra:.2f}", f"[{pnl_color}]{pnl_pct:+.2f}%[/{pnl_color}]")
        
        # Trailing Stop info
        max_precio = estado.get("max_precio", precio_compra)
        precio_trailing = max_precio * (1 - TS)
        tabla.add_row("🛡️ Trailing Stop", f"${precio_trailing:.2f}", f"Max: ${max_precio:.2f}")
    else:
        tabla.add_row("🎯 Posición", "❌ CERRADA", "🔍 Esperando")
    
    return tabla

# 2. Loop Principal
logger.info(f"=== ARGOS BOT INICIADO PARA {SYMBOL} ===")
modo_msg = "MODO SIMULACIÓN (PAPER TRADING)" if SIMULATION_MODE else "MODO REAL (DINERO REAL)"
logger.info(modo_msg)

# Banner de inicio con Rich
console.print("\n")
console.print("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
console.print(f"[bold cyan]           🤖 ARGOS TRADING BOT v2.1 🤖[/bold cyan]")
console.print("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
console.print(f"[yellow]Par:[/yellow] [bold]{SYMBOL}[/bold]")
console.print(f"[yellow]Estrategia:[/yellow] Triple Filtro (RSI + Bollinger + EMA20) + Trailing Stop")
console.print(f"[yellow]Modo:[/yellow] [bold red]{modo_msg}[/bold red]" if not SIMULATION_MODE else f"[yellow]Modo:[/yellow] [bold blue]{modo_msg}[/bold blue]")
console.print(f"[yellow]Exchange:[/yellow] Binance Testnet")
console.print("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
console.print("\n")

enviar_telegram(f"🤖 **Argos Bot Iniciado**\\n{modo_msg}\\nPar: {SYMBOL}\\nEstrategia: RSI + Bollinger + EMA20 + Trailing")

while True:
    try:
        verificar_reporte_diario()
        
        # Heartbeat cada 12 horas (43200 segundos)
        ahora = datetime.datetime.now()
        if (ahora - ultima_vez_vivo).total_seconds() >= 43200:
            enviar_telegram(f"💓 **Heartbeat:** El bot sigue activo. Precio: {estado.get('precio_compra', 'N/A')}")
            ultima_vez_vivo = ahora

        df = obtener_datos()
        
        if df.empty:
            time.sleep(10)
            continue
            
        # Asegurarnos de tener suficientes datos para EMA
        if pd.isna(df['EMA_200'].iloc[-1]):
            logger.warning(f"Esperando datos suficientes para EMA... ({len(df)} velas disponibles)")
            time.sleep(10)
            continue
            
        # PROCESAR COMANDOS DE TELEGRAM
        procesar_comandos(df)

        precio_actual = df['close'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]
        
        # Búsqueda inteligente de la columna BBL (Lower Band)
        # A veces panda_ta la llama BBL_20_2.0, otras veces diferente
        col_bbl = [c for c in df.columns if c.startswith('BBL')][0]
        lower_band = df[col_bbl].iloc[-1]
        
        ema_200 = df['EMA_200'].iloc[-1]

        # Log de consola con dashboard visual
        tendencia = "ALCISTA" if precio_actual > ema_200 else "BAJISTA"
        
        # Logger para archivo
        status_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] P: ${precio_actual:.2f} | RSI: {rsi_actual:.2f} | {tendencia} | Pos: {'SÍ' if estado['posicion_abierta'] else 'NO'}"
        logger.info(status_msg)
        
        # Dashboard visual con Rich
        dashboard = generar_dashboard(precio_actual, rsi_actual, ema_200, tendencia, 
                                       estado['posicion_abierta'], estado)
        
        # Limpiar pantalla y mostrar dashboard
        console.clear()
        console.print(dashboard)
        console.print(f"\\n[dim]⏰ Actualizado: {datetime.datetime.now().strftime('%H:%M:%S')} | ⏳ Próxima actualización en 60s[/dim]\\n")

        if not estado["posicion_abierta"]:
            # --- LÓGICA DE ENTRADA (COMPRA) ---
            # FILTRO TRIPLE: 
            # 1. RSI < 35 (Oversold)
            # 2. Precio < Banda Bollinger Inferior (Cheap)
            # 3. Precio > EMA 200 (Trend is Up - Solo compramos correcciones en subida)
            
            condicion_rsi = rsi_actual < 35
            condicion_bb = precio_actual < lower_band
            condicion_ema = precio_actual > ema_200
            if condicion_rsi and condicion_bb and condicion_ema:
                logger.info("🚀 SEÑAL DE COMPRA CONFIRMADA (Triple Filtro)")
                print("\n🚀 SEÑAL PERFECTA CONFIRMADA\n")
                
                # --- VERIFICACIÓN DE SEGURIDAD ANTES DE DISPARAR ---
                # Validamos saldo solo si vamos a operar de verdad
                if not SIMULATION_MODE and not check_balance():
                     enviar_telegram("⚠️ **SEÑAL OMITIDA**: Saldo insuficiente en Binance (<$15 USDT).")
                cantidad_compra = 0.0
                
                if not SIMULATION_MODE:
                    try:
                        # 1. Obtener Saldo Libre
                        balance = exchange.fetch_balance()
                        usdt_free = balance.get('USDT', {}).get('free', 0.0)
                        
                        # VERIFICAR SI HAY SUFICIENTE SALDO
                        if usdt_free < 15:
                             enviar_telegram("⚠️ **SEÑAL OMITIDA**: Saldo insuficiente (< $15 USD).")
                             time.sleep(60)
                             continue
                        
                        # VERIFICAR MÍNIMO NOTIONAL DE BINANCE
                        market_info = exchange.markets.get(SYMBOL, {})
                        min_cost = market_info.get('limits', {}).get('cost', {}).get('min', 10.0)
                        if usdt_free * POS_SIZE < min_cost:
                            enviar_telegram(f"⚠️ **SEÑAL OMITIDA**: Monto calculado menor al mínimo de Binance (${min_cost:.2f} USD).")
                            time.sleep(60)
                            continue

                        # 2. Calcular cuánto gastar (Ej. 95% de 100 USDT = 95 USD)
                        gasto_usdt = usdt_free * POS_SIZE
                        
                        # 3. Calcular cantidad de BTC (95 / 90000 = 0.00105 BTC)
                        cantidad_bruta = gasto_usdt / precio_actual
                        
                        # 4. Ajustar decimales según reglas de Binance (PRECISIÓN)
                        cantidad_compra = exchange.amount_to_precision(SYMBOL, cantidad_bruta)
                        
                        logger.info(f"Ejecutando compra: {cantidad_compra} {SYMBOL.split('/')[0]} con ${gasto_usdt:.2f} USDT")
                        print(f"💰 Comprando {cantidad_compra} {SYMBOL.split('/')[0]} con ${gasto_usdt:.2f} USDT")
                        
                        # 5. Ejecutar Orden
                        order = exchange.create_market_buy_order(SYMBOL, cantidad_compra)
                        precio_real_ejecucion = order.get('average') or order.get('price') or precio_actual
                        logger.info(f"✅ Orden ejecutada exitosamente a precio: ${precio_real_ejecucion:.2f}")
                        print(f"✅ Orden ejecutada a precio: {precio_real_ejecucion}")
                        
                    except ccxt.InsufficientFunds as e:
                        logger.error(f"Fondos insuficientes: {e}")
                        enviar_telegram(f"❌ Fondos insuficientes para comprar: {e}")
                        continue
                    except ccxt.InvalidOrder as e:
                        logger.error(f"Orden inválida: {e}")
                        enviar_telegram(f"❌ Orden inválida (posible mín. notional): {e}")
                        continue
                    except ccxt.NetworkError as e:
                        logger.error(f"Error de red: {e}")
                        enviar_telegram(f"⚠️ Error de conexión con Binance: {e}")
                        continue
                    except ccxt.ExchangeError as e:
                        logger.error(f"Error del exchange: {e}")
                        enviar_telegram(f"❌ Error de Binance: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error calculando tamaño posición: {e}", exc_info=True)
                        enviar_telegram(f"❌ Error al intentar comprar: {e}")
                        continue
                else:
                    # En simulación, asumimos 0.01 BTC como referencia
                    cantidad_compra = 0.01 

                # Guardar estado
                precio_efectivo = precio_real_ejecucion if not SIMULATION_MODE and 'precio_real_ejecucion' in locals() else precio_actual
                estado.update({
                    "posicion_abierta": True, 
                    "precio_compra": precio_efectivo,
                    "cantidad": cantidad_compra,
                    "max_precio": precio_efectivo, 
                    "fecha_compra": str(datetime.datetime.now())
                })
                guardar_estado(estado)
                guardar_trade_csv(datetime.datetime.now(), "COMPRA", precio_actual, 0)
                
                enviar_telegram(f"🚀 **COMPRA EJECUTADA**\nPrecio: {precio_actual}\nCant: {cantidad_compra}\nRSI: {rsi_actual:.2f}\nEMA200: {ema_200:.2f}")
    
        else:
            # --- LÓGICA DE SALIDA (VENTA) ---
            precio_entrada = estado["precio_compra"]
            max_precio_historico = estado.get("max_precio", precio_entrada)
            
            # Actualizamos el Trailing (Precio Máximo visto)
            if precio_actual > max_precio_historico:
                max_precio_historico = precio_actual
                estado["max_precio"] = max_precio_historico
                guardar_estado(estado)
                # print(f"📈 Nuevo máximo alcanzado: {max_precio_historico}")

            # Calculamos el precio de salida dinámica (Trailing Stop)
            precio_salida_trailing = max_precio_historico * (1 - TS)

            # 1. Verificar TRAILING STOP
            if precio_actual <= precio_salida_trailing:
                pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                logger.info(f"📉 TRAILING STOP DISPARADO (PnL: {pnl_pct*100:.2f}%)")
                print(f"\n📉 TRAILING STOP DISPARADO\n")
                if not SIMULATION_MODE:
                    try:
                        cantidad_venta = estado.get("cantidad", 0)
                        order = exchange.create_market_sell_order(SYMBOL, cantidad_venta)
                        logger.info(f"✅ Venta ejecutada (Trailing Stop)")
                        print(f"✅ Venta ejecutada (Trailing Stop)")
                    except Exception as e:
                        logger.error(f"Error ejecutando venta: {e}", exc_info=True)
                        enviar_telegram(f"❌ Error al vender (Trailing Stop): {e}")
                registrar_operacion("TRAILING STOP", precio_actual, pnl_pct)
            
            # 2. Verificar TAKE PROFIT
            elif precio_actual >= precio_entrada * (1 + TP):
                logger.info(f"✅ TAKE PROFIT EJECUTADO")
                print(f"\n✅ TAKE PROFIT EJECUTADO\n")
                if not SIMULATION_MODE:
                    try:
                        cantidad_venta = estado.get("cantidad", 0)
                        order = exchange.create_market_sell_order(SYMBOL, cantidad_venta)
                        logger.info(f"✅ Venta ejecutada (Take Profit)")
                        print(f"✅ Venta ejecutada (Take Profit)")
                    except Exception as e:
                        logger.error(f"Error ejecutando venta: {e}", exc_info=True)
                        enviar_telegram(f"❌ Error al vender (Take Profit): {e}")
                pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                registrar_operacion("TAKE PROFIT", precio_actual, pnl_pct)
            
            # 3. Stop Loss de Emergencia
            elif precio_actual <= precio_entrada * (1 - SL):
                 logger.warning(f"❌ STOP LOSS DE EMERGENCIA ACTIVADO")
                 print(f"\n❌ STOP LOSS DE EMERGENCIA\n")
                 if not SIMULATION_MODE:
                     try:
                         cantidad_venta = estado.get("cantidad", 0)
                         order = exchange.create_market_sell_order(SYMBOL, cantidad_venta)
                         logger.info(f"✅ Venta ejecutada (Stop Loss)")
                         print(f"✅ Venta ejecutada (Stop Loss)")
                     except Exception as e:
                         logger.error(f"Error ejecutando venta: {e}", exc_info=True)
                         enviar_telegram(f"❌ Error al vender (Stop Loss): {e}")
                 pnl_pct = (precio_actual - precio_entrada) / precio_entrada
                 registrar_operacion("STOP LOSS (EMERGENCIA)", precio_actual, pnl_pct)
            
            # 3. (Opcional) Salida por RSI alto (si el usuario quisiera vender por RSI > 70 también)
            # elif rsi_actual > 70: ...

    except Exception as e:
        logger.error(f"Error en bucle principal: {e}", exc_info=True)
        time.sleep(30) # Esperar antes de reintentar si falla algo grave
    
    # Revisar cada 60 segundos
    time.sleep(60) 
