# 🚀 Guía de Testing en Testnet - Argos Bot

## 📅 Inicio: 7 de enero de 2026

---

## ✅ Estado Actual

- ✅ Bot ejecutándose en testnet (PID: 69378)
- ✅ Base de datos SQLite inicializada
- ✅ Sistema de monitoreo configurado
- ✅ Logs activos en `argos_bot.log`

---

## 📊 Condiciones de Mercado Actuales

**BTC/USDT**: ~$91,356  
**RSI**: 48.38 (neutral)  
**Tendencia**: ALCISTA 🐂  
**Posición**: Esperando señal de compra

---

## 🎯 Objetivos del Testing (2-4 semanas)

### Meta Principal
Acumular **50-100 trades** para validar:

1. ✅ **Lógica de Triple Filtro**
   - RSI < 35 (sobreventa)
   - Precio < BB Lower
   - Precio > EMA 20 (tendencia alcista)

2. ✅ **Trailing Stop Dinámico**
   - Seguimiento del precio (0.5% desde máximo)
   - Venta automática al detectar reversión

3. ✅ **Gestión de Riesgo**
   - Stop Loss 1%
   - Take Profit 1.5%
   - Position Size 95% del balance

4. ✅ **Manejo de Errores**
   - Reconexión automática
   - Errores de red
   - Validación de fondos

---

## 🛠️ Comandos de Monitoreo

### Monitor en Tiempo Real
```bash
# Ver dashboard completo
./monitor.sh

# Actualización automática cada 5 segundos
watch -n 5 ./monitor.sh

# Logs en tiempo real
tail -f argos_bot.log

# Logs con filtro
tail -f argos_bot.log | grep -E "COMPRA|VENTA|ERROR"
```

### Reportes
```bash
# Reporte diario
python reporte_diario.py

# Métricas completas
python metricas.py

# Estado de la base de datos
sqlite3 argos.db "SELECT * FROM trades ORDER BY timestamp_venta DESC LIMIT 10;"
```

### Control del Bot
```bash
# Ver proceso
ps aux | grep "python main.py"

# Detener bot
pkill -f "python main.py"

# Reiniciar bot
pkill -f "python main.py" && sleep 2 && nohup python main.py > bot_output.log 2>&1 &

# Ver últimos logs
tail -50 argos_bot.log
```

---

## 📋 Checklist Diario

### Mañana (9:00 AM)
- [ ] Verificar que el bot está corriendo: `./monitor.sh`
- [ ] Revisar trades de la noche: `python reporte_diario.py`
- [ ] Verificar errores en logs: `grep ERROR argos_bot.log | tail -20`

### Mediodía (14:00 PM)
- [ ] Check rápido: `./monitor.sh`
- [ ] Verificar posición actual

### Noche (22:00 PM)
- [ ] Reporte completo: `python reporte_diario.py`
- [ ] Revisar métricas si hay >5 trades: `python metricas.py`
- [ ] Backup de base de datos: `cp argos.db backups/argos_$(date +%Y%m%d).db`

---

## 📊 Checklist Semanal

### Domingo (Fin de Semana)
- [ ] Generar reporte de métricas: `python metricas.py`
- [ ] Analizar Win Rate y Profit Factor
- [ ] Revisar trades perdedores (identificar patrones)
- [ ] Ajustar parámetros si es necesario
- [ ] Backup completo: `tar -czf backup_$(date +%Y%m%d).tar.gz argos.db argos_bot.log`

---

## 🔧 Ajuste de Parámetros

Si después de 20-30 trades observas:

### Win Rate < 40%
```bash
# Considerar hacer más conservador el Triple Filtro
# Editar .env:
RSI_THRESHOLD=30  # Más estricto (era 35)
```

### Muchos Stop Loss
```bash
# Aumentar Stop Loss
STOP_LOSS_PCT=0.015  # 1.5% (era 1%)
```

### Trailing Stop sale muy pronto
```bash
# Dar más margen al trailing
TRAILING_STOP_PCT=0.008  # 0.8% (era 0.5%)
```

### Take Profit se alcanza antes del trailing
```bash
# Aumentar Take Profit para dar chance al trailing
TAKE_PROFIT_PCT=0.02  # 2% (era 1.5%)
```

---

## 🚨 Alertas a Monitorear

### Críticas (Acción Inmediata)
- ❌ Bot detenido inesperadamente
- ❌ Pérdida > 5% en un día
- ❌ Más de 3 errores de red seguidos
- ❌ Balance USDT < $50

### Advertencias (Revisar)
- ⚠️ Win Rate < 35% después de 20 trades
- ⚠️ Más de 10 trades en un día (sobreoperar)
- ⚠️ Duración promedio de trades < 30 min
- ⚠️ RSI permanentemente > 70 (mercado sobrecomprado)

---

## 📈 Métricas Objetivo

Después de 50 trades, apuntar a:

| Métrica | Mínimo Aceptable | Objetivo | Excelente |
|---------|------------------|----------|-----------|
| **Win Rate** | > 40% | > 50% | > 60% |
| **Profit Factor** | > 1.2 | > 1.8 | > 2.5 |
| **Sharpe Ratio** | > 0.5 | > 1.5 | > 2.5 |
| **Max Drawdown** | < 20% | < 15% | < 10% |
| **PnL Promedio** | > 0.5% | > 1% | > 1.5% |

---

## 🎓 Interpretación de Resultados

### Si Win Rate es bajo pero Profit Factor alto
✅ **BIEN** - Pocas operaciones pero muy rentables cuando gana.

### Si Win Rate es alto pero Profit Factor bajo
⚠️ **REVISAR** - Gana seguido pero poco, y pierde mucho cuando falla.

### Si Max Drawdown > 20%
🚨 **PELIGRO** - Reducir position size o hacer stops más conservadores.

### Si Sharpe Ratio < 1
⚠️ **MEJORAR** - El riesgo es mayor que el retorno. Ajustar estrategia.

---

## 💾 Sistema de Backups

### Backup Automático Diario (Cron)
```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 23:00)
0 23 * * * cd /home/medalcode/Antigravity/Argos && cp argos.db backups/argos_$(date +\%Y\%m\%d).db
```

### Backup Manual
```bash
# Crear directorio de backups
mkdir -p backups

# Backup completo
cp argos.db backups/argos_$(date +%Y%m%d_%H%M%S).db
cp argos_bot.log backups/log_$(date +%Y%m%d_%H%M%S).log
```

---

## 🔄 Reinicio Después de Ajustes

Cuando cambies parámetros en `.env`:

```bash
# 1. Detener bot
pkill -f "python main.py"

# 2. Verificar que se detuvo
ps aux | grep "python main.py"

# 3. Editar configuración
nano .env

# 4. Reiniciar bot
nohup python main.py > bot_output.log 2>&1 &

# 5. Verificar inicio
tail -20 argos_bot.log

# 6. Monitor
./monitor.sh
```

---

## 📞 Contacto y Soporte

### Logs de Debug
Si encuentras errores:
```bash
# Ver stack trace completo
tail -100 argos_bot.log | grep -A 20 "ERROR"

# Verificar conexión a Binance
python -c "import ccxt; exchange = ccxt.binance({'enableRateLimit': True}); exchange.set_sandbox_mode(True); print(exchange.fetch_ticker('BTC/USDT'))"
```

### Telegram
- Configurar notificaciones: Editar `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `.env`
- Habilitar en `reporte_diario.py` (descomentar línea 125)

---

## ✅ Checklist de Finalización (Después de 2-4 semanas)

Antes de pasar a producción:

- [ ] Al menos 50 trades completados
- [ ] Win Rate > 40%
- [ ] Profit Factor > 1.5
- [ ] Max Drawdown < 20%
- [ ] Sin errores críticos en 1 semana
- [ ] Trailing Stop funcionando correctamente
- [ ] Métricas estables en última semana

**Si todos los checks pasan**: ✅ LISTO PARA PRODUCCIÓN

---

## 🚀 Siguiente Fase: Producción

Una vez validado en testnet:

1. **Rotar API Keys** (usar mainnet)
2. **Configurar .env** con producción
3. **Reducir position size** (comenzar con 50% del capital)
4. **Monitoreo intensivo** primeros 3 días
5. **Aumentar gradualmente** position size

---

**Fecha de inicio**: 7 de enero de 2026  
**Fecha estimada de finalización**: 4 de febrero de 2026  
**Estado**: 🟢 EN PROGRESO

---

## 📝 Notas del Testing

### Semana 1
- *Agregar observaciones aquí*

### Semana 2
- *Agregar observaciones aquí*

### Semana 3
- *Agregar observaciones aquí*

### Semana 4
- *Agregar observaciones aquí*
