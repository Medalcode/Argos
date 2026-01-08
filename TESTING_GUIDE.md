# 🧪 Guía de Testing en Binance Testnet

## ⚠️ IMPORTANTE: Testing Obligatorio Antes de Producción

Antes de activar el bot con dinero real, **DEBES** realizar pruebas exhaustivas en el entorno de testnet de Binance. Esto te permitirá validar todas las funcionalidades sin riesgo financiero.

---

## 📋 Paso 1: Configurar Credenciales de Testnet

### 1.1 Crear Cuenta en Binance Testnet

1. Visita: https://testnet.binance.vision/
2. Click en "Sign Up" y crea una cuenta (NO necesitas verificación)
3. Una vez logueado, genera API Keys desde el panel

### 1.2 Obtener USDT Virtual

1. En el panel de testnet, busca la opción **"Test Funds"**
2. Solicita **1000 USDT** de prueba (se acreditan instantáneamente)
3. Verifica que tienes saldo en tu wallet de Spot

### 1.3 Configurar Variables de Entorno

Crea un archivo `.env.testnet` con las credenciales de testnet:

```bash
# API Keys de TESTNET (NO usar las de producción)
BINANCE_API_KEY=tu_testnet_api_key_aqui
BINANCE_SECRET_KEY=tu_testnet_secret_key_aqui

# Telegram (puedes usar las mismas que en producción)
TELEGRAM_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# Parámetros de Trading
SYMBOL=BTC/USDT
STOP_LOSS_PCT=0.01
TAKE_PROFIT_PCT=0.015
TRAILING_STOP_PCT=0.005
POSITION_SIZE_PCT=0.95

# ⚠️ CRÍTICO: Desactivar modo simulación
SIMULATION_MODE=False
```

---

## 🔧 Paso 2: Modificar Código para Testnet

### 2.1 Habilitar Modo Testnet en main.py

Edita el archivo `main.py` en la **línea 27** y descomenta:

```python
# Si estamos en modo TESTNET (Sandbox), descomentar las siguientes líneas
exchange.set_sandbox_mode(True)  # ← DESCOMENTAR ESTA LÍNEA
```

### 2.2 Verificar URL del Testnet

CCXT automáticamente cambia a las URLs de testnet cuando activas `set_sandbox_mode(True)`:
- Producción: `https://api.binance.com`
- Testnet: `https://testnet.binance.vision`

---

## 🧪 Paso 3: Ejecutar Pruebas

### 3.1 Test 1: Verificación de Conexión

```bash
python3 -c "
import ccxt
import os
from dotenv import load_dotenv

load_dotenv('.env.testnet')

exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET_KEY'),
    'enableRateLimit': True
})
exchange.set_sandbox_mode(True)

balance = exchange.fetch_balance()
print(f'✅ Conexión exitosa')
print(f'USDT disponible: {balance[\"USDT\"][\"free\"]}')
"
```

**Resultado esperado:** Debería mostrar tu saldo de USDT de testnet (~1000 USDT).

---

### 3.2 Test 2: Ejecución del Bot Completo

```bash
# Usar archivo de configuración de testnet
cp .env.testnet .env

# Ejecutar el bot
python3 main.py
```

**Monitorear:**
1. ✅ El bot se conecta correctamente
2. ✅ Descarga datos del mercado (300 velas)
3. ✅ Calcula indicadores (RSI, Bollinger, EMA)
4. ✅ Evalúa condiciones de compra
5. ✅ **Cuando se cumpla señal, ejecuta compra REAL en testnet**
6. ✅ Guarda estado correctamente
7. ✅ Envía notificación a Telegram
8. ✅ Monitorea Trailing Stop
9. ✅ Ejecuta venta cuando se dispare TS/TP/SL

---

### 3.3 Test 3: Comandos de Telegram

Durante la ejecución del bot, prueba los comandos:

```
/status     → Debería mostrar estado actual de la posición
/comprar    → Debe ejecutar compra forzada (si no hay posición)
/vender     → Debe ejecutar venta forzada (si hay posición abierta)
```

---

### 3.4 Test 4: Validación de Órdenes en Binance

1. Accede al panel de testnet: https://testnet.binance.vision/
2. Ve a **Spot → Trade History**
3. Verifica que aparecen las órdenes ejecutadas por el bot
4. Compara precios y cantidades con los logs del bot

---

## ✅ Checklist de Validación

Antes de pasar a producción, asegúrate de que **TODAS** estas pruebas sean exitosas:

- [ ] ✅ Conexión a testnet funcional
- [ ] ✅ Saldo de USDT se obtiene correctamente
- [ ] ✅ Descarga de datos de mercado sin errores
- [ ] ✅ Cálculo de indicadores correcto
- [ ] ✅ Compra se ejecuta cuando se cumple señal (RSI+BB+EMA)
- [ ] ✅ Orden aparece en historial de Binance testnet
- [ ] ✅ Estado se guarda en `estado_bot.json`
- [ ] ✅ Notificación de compra llega a Telegram
- [ ] ✅ Trailing Stop se actualiza correctamente
- [ ] ✅ Venta se ejecuta al dispararse TS/TP/SL
- [ ] ✅ PnL se calcula correctamente
- [ ] ✅ Operación se registra en `trades.csv`
- [ ] ✅ Comando `/status` funciona
- [ ] ✅ Comando `/vender` funciona (venta forzada)
- [ ] ✅ Manejo de errores no rompe el bot
- [ ] ✅ Reconexión automática en caso de error de red

---

## 🚨 Errores Comunes y Soluciones

### Error: "Invalid API Key"
- **Causa:** Estás usando API Keys de producción en testnet
- **Solución:** Genera nuevas keys desde https://testnet.binance.vision/

### Error: "MIN_NOTIONAL"
- **Causa:** El monto de la orden es muy bajo (<$10 USD)
- **Solución:** Aumenta `POSITION_SIZE_PCT` o solicita más USDT de prueba

### Error: "Insufficient Funds"
- **Causa:** No tienes USDT en testnet
- **Solución:** Solicita fondos desde el panel de testnet

### Error: "Timestamp for this request is outside of the recvWindow"
- **Causa:** Reloj del sistema desincronizado
- **Solución:** Sincroniza el reloj del sistema
  ```bash
  sudo ntpdate -s time.nist.gov
  ```

---

## 🎯 Paso 4: Migración a Producción

Una vez que **TODAS** las pruebas sean exitosas:

### 4.1 Desactivar Modo Testnet

Edita `main.py` línea 27 y **comenta** la línea:

```python
# exchange.set_sandbox_mode(True)  # ← COMENTAR de nuevo
```

### 4.2 Configurar Producción

Crea `.env` con tus credenciales de **producción** de Binance:

```bash
# ⚠️ ESTAS SON TUS KEYS REALES - PROTÉGELAS
BINANCE_API_KEY=tu_produccion_api_key
BINANCE_SECRET_KEY=tu_produccion_secret_key

# Mantén SIMULATION_MODE=False para operar de verdad
SIMULATION_MODE=False
```

### 4.3 Iniciar con Capital Limitado

**RECOMENDACIÓN CRÍTICA:**
- Empieza con **$100-200 USD** máximo
- Monitorea durante 1-2 semanas
- Si todo funciona, incrementa gradualmente

### 4.4 Monitoreo Continuo

- Revisa Telegram cada 4-6 horas
- Verifica `trades.csv` diariamente
- Valida órdenes en Binance
- Haz backups de `estado_bot.json`

---

## 📊 Métricas de Éxito en Testnet

Antes de pasar a producción, deberías haber completado:

- ✅ **Mínimo 5 operaciones completas** (compra + venta)
- ✅ **Al menos 1 Trailing Stop exitoso**
- ✅ **Al menos 1 Take Profit exitoso**
- ✅ **Sin errores críticos en 24 horas de ejecución**
- ✅ **Todos los comandos de Telegram funcionando**

---

## ⚠️ DISCLAIMER FINAL

> **El trading de criptomonedas conlleva riesgo de pérdida financiera.**  
> Este bot es una herramienta automatizada, pero NO garantiza ganancias.  
> Nunca inviertas más de lo que puedas permitirte perder.  
> El autor no se hace responsable de pérdidas financieras.

---

## 🆘 Soporte

Si encuentras problemas durante el testing:
1. Revisa los logs en consola
2. Verifica el archivo `estado_bot.json`
3. Consulta el historial en `trades.csv`
4. Abre un issue en el repositorio con logs completos

---

**Última actualización:** 7 de enero de 2026  
**Versión de la guía:** 1.0
