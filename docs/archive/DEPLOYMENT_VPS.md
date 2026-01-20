# 🚀 Guía de Deployment en VPS (24/7)

## 🎯 Objetivo
Ejecutar el bot Argos 24/7 en un servidor en la nube, independiente de tu computador personal.

---

## 🆓 OPCIÓN RECOMENDADA: Oracle Cloud Free Tier

### ✅ Por qué Oracle Cloud
- ✅ **GRATIS PARA SIEMPRE** (no solo trial)
- ✅ 2 VPS ARM con 1GB RAM cada uno
- ✅ 200GB almacenamiento
- ✅ Ideal para bots de trading
- ✅ Sin tarjeta de crédito requerida

---

## 📋 Paso 1: Crear Cuenta en Oracle Cloud

1. Ve a: https://www.oracle.com/cloud/free/
2. Click en "Start for free"
3. Completa el registro (email, país, teléfono)
4. Verifica tu identidad
5. **IMPORTANTE**: Selecciona región más cercana (Ashburn, São Paulo, etc.)

---

## 🖥️ Paso 2: Crear VM Instance

### En Oracle Cloud Console:

1. **Menu → Compute → Instances**
2. Click "Create Instance"
3. Configuración:
   ```
   Name: argos-trading-bot
   Image: Ubuntu 22.04 (Oracle Linux también funciona)
   Shape: VM.Standard.A1.Flex (ARM - GRATIS)
   OCPU: 1
   RAM: 6GB (ajusta según disponibilidad)
   ```
4. **Networking**:
   - Selecciona VCN por defecto
   - Asignar IP pública: ✅ SÍ
5. **SSH Keys**:
   - Genera par de keys o sube tu clave pública
   - **GUARDA LA CLAVE PRIVADA** (no se puede recuperar)
6. Click "Create"

**Espera 2-3 minutos** hasta que el estado sea "Running" 🟢

---

## 🔐 Paso 3: Conectar por SSH

### Desde tu computador:

```bash
# Permisos a la clave privada
chmod 600 ~/Downloads/ssh-key-*.key

# Conectar (reemplaza con tu IP pública)
ssh -i ~/Downloads/ssh-key-*.key ubuntu@<IP_PUBLICA>
# o si es Oracle Linux:
ssh -i ~/Downloads/ssh-key-*.key opc@<IP_PUBLICA>
```

**¿No funciona?** Verifica el firewall de Oracle Cloud:
1. Instance Details → Subnet
2. Security List → Ingress Rules
3. Agregar regla para puerto 22 (SSH)

---

## 📦 Paso 4: Deployment Automatizado

### En el servidor VPS (después de conectar por SSH):

```bash
# 1. Descargar script de deployment
wget https://raw.githubusercontent.com/Medalcode/Argos/main/deploy_vps.sh

# 2. Dar permisos de ejecución
chmod +x deploy_vps.sh

# 3. Ejecutar deployment
./deploy_vps.sh
```

El script hace automáticamente:
- ✅ Actualiza el sistema
- ✅ Instala Python 3 y dependencias
- ✅ Clona el repositorio
- ✅ Crea entorno virtual
- ✅ Instala librerías Python
- ✅ Configura servicio systemd (autostart)

---

## 🔑 Paso 5: Configurar Credenciales

### Editar archivo .env:

```bash
# En el VPS
cd ~/trading-bots/Argos
nano .env
```

**Pega tus credenciales**:
```ini
BINANCE_API_KEY=tu_api_key_real
BINANCE_SECRET_KEY=tu_secret_key_real
TELEGRAM_TOKEN=tu_token_telegram
TELEGRAM_CHAT_ID=tu_chat_id

SYMBOL=BTC/USDT
STOP_LOSS_PCT=0.01
TAKE_PROFIT_PCT=0.015
TRAILING_STOP_PCT=0.005
POSITION_SIZE_PCT=0.95
SIMULATION_MODE=False
```

**Guardar**: Ctrl+O, Enter, Ctrl+X

---

## 🚀 Paso 6: Iniciar el Bot

```bash
# Iniciar servicio
sudo systemctl start argos-bot

# Verificar estado
sudo systemctl status argos-bot

# Si está OK, verás:
# ● argos-bot.service - Argos Trading Bot
#    Active: active (running) since...

# Ver logs en vivo
tail -f ~/trading-bots/Argos/argos_bot.log

# Monitor completo
cd ~/trading-bots/Argos
./monitor.sh
```

---

## 🛠️ Comandos de Administración

### Control del Bot
```bash
# Iniciar
sudo systemctl start argos-bot

# Detener
sudo systemctl stop argos-bot

# Reiniciar
sudo systemctl restart argos-bot

# Ver estado
sudo systemctl status argos-bot

# Ver logs
tail -f ~/trading-bots/Argos/argos_bot.log

# Logs con filtros
tail -f ~/trading-bots/Argos/argos_bot.log | grep -E "COMPRA|VENTA|ERROR"
```

### Monitoreo
```bash
# Dashboard completo
cd ~/trading-bots/Argos
./monitor.sh

# Reporte diario
python reporte_diario.py

# Métricas avanzadas
python metricas.py

# Uso de recursos del servidor
htop
```

### Actualizar Bot
```bash
cd ~/trading-bots/Argos
git pull origin main
sudo systemctl restart argos-bot
```

---

## 🔒 Paso 7: Configurar Firewall

**IMPORTANTE**: Asegura el servidor

### En Oracle Cloud Console:
1. Instance → Subnet → Security List
2. Agregar Ingress Rules:
   - SSH (22): Solo tu IP
   - HTTPS (443): 0.0.0.0/0 (si vas a agregar dashboard web)

### En el VPS:
```bash
# Instalar UFW
sudo apt install ufw -y

# Permitir SSH
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

# Verificar
sudo ufw status
```

---

## 📊 Paso 8: Configurar Backups Automáticos

### Cron job para backup diario:

```bash
# Editar crontab
crontab -e

# Agregar al final:
# Backup diario a las 23:00
0 23 * * * cd /home/ubuntu/trading-bots/Argos && cp argos.db backups/argos_$(date +\%Y\%m\%d).db

# Limpiar backups antiguos (mantener últimos 30 días)
0 0 * * * find /home/ubuntu/trading-bots/Argos/backups -name "argos_*.db" -mtime +30 -delete
```

---

## 🔍 Verificación Post-Deployment

### Checklist:

```bash
# 1. Servicio activo
sudo systemctl status argos-bot
# Debe mostrar: Active: active (running)

# 2. Logs generándose
tail -20 ~/trading-bots/Argos/argos_bot.log
# Debe mostrar actualizaciones cada 60 segundos

# 3. Base de datos funcionando
cd ~/trading-bots/Argos
sqlite3 argos.db "SELECT COUNT(*) FROM trades;"
# Debe ejecutarse sin error

# 4. Monitor funcionando
./monitor.sh
# Debe mostrar dashboard completo

# 5. Conexión a Binance
grep "Conexión exitosa\|Connected" ~/trading-bots/Argos/argos_bot.log
# Debe aparecer líneas de conexión exitosa
```

---

## 🌍 Acceso Remoto desde tu Computador

### Configurar SSH fácil:

En tu computador local, edita `~/.ssh/config`:

```bash
Host argos-vps
    HostName <IP_PUBLICA_VPS>
    User ubuntu
    IdentityFile ~/Downloads/ssh-key-argos.key
    ServerAliveInterval 60
```

Ahora puedes conectar simplemente con:
```bash
ssh argos-vps
```

### Scripts remotos:

```bash
# Ver estado desde tu PC
ssh argos-vps "cd trading-bots/Argos && ./monitor.sh"

# Ver logs
ssh argos-vps "tail -20 trading-bots/Argos/argos_bot.log"

# Reporte diario
ssh argos-vps "cd trading-bots/Argos && python reporte_diario.py"
```

---

## 💰 Alternativas de VPS

### Si Oracle Cloud no funciona:

#### Google Cloud Platform ($300 gratis)
```bash
# 1. Crear cuenta: https://cloud.google.com/free
# 2. Compute Engine → VM instances
# 3. e2-micro (gratis permanente)
# 4. Ubuntu 22.04
# 5. SSH desde browser o con gcloud CLI
```

#### DigitalOcean ($5/mes)
```bash
# 1. Crear cuenta: https://www.digitalocean.com/
# 2. Create → Droplets
# 3. Basic Plan: $5/mo (1GB RAM)
# 4. Ubuntu 22.04
# 5. SSH con tu key
```

#### AWS EC2 (Free tier 12 meses)
```bash
# 1. Crear cuenta: https://aws.amazon.com/free/
# 2. EC2 → Launch Instance
# 3. t2.micro (Free tier)
# 4. Ubuntu 22.04
# 5. Download .pem key
```

---

## 🚨 Solución de Problemas

### El bot no inicia:
```bash
# Ver logs detallados
sudo journalctl -u argos-bot -n 50

# Verificar permisos
ls -la ~/trading-bots/Argos/

# Verificar .env existe
cat ~/trading-bots/Argos/.env

# Probar manualmente
cd ~/trading-bots/Argos
source venv/bin/activate
python main.py
```

### Sin conexión a Binance:
```bash
# Test de conectividad
curl https://testnet.binance.vision/api/v3/ping

# Test con Python
cd ~/trading-bots/Argos
source venv/bin/activate
python -c "import ccxt; exchange = ccxt.binance(); exchange.set_sandbox_mode(True); print(exchange.fetch_ticker('BTC/USDT'))"
```

### Servidor sin memoria:
```bash
# Ver memoria disponible
free -h

# Ver procesos pesados
htop

# Limpiar cache (si es seguro)
sudo sync && sudo sysctl -w vm.drop_caches=3
```

---

## 📱 Monitoreo desde el Móvil

### Opción 1: Telegram
Habilita notificaciones en `reporte_diario.py` (línea 125):
```python
enviar_telegram(mensaje)  # Descomentar
```

### Opción 2: Termius (App SSH)
1. Instala Termius (iOS/Android)
2. Agregar host con tus credenciales SSH
3. Ejecuta comandos desde el móvil

### Opción 3: Pingdom (Monitoreo Uptime)
1. Cuenta gratis en https://www.pingdom.com/
2. Monitorea que el servidor esté UP
3. Alertas por email/SMS

---

## ✅ Checklist Final

- [ ] VPS creado y accesible
- [ ] Bot deployado con `deploy_vps.sh`
- [ ] `.env` configurado con credenciales reales
- [ ] Servicio systemd iniciado
- [ ] Logs mostrando actividad cada 60s
- [ ] Firewall configurado
- [ ] Backups automáticos programados
- [ ] Notificaciones Telegram funcionando
- [ ] Acceso SSH desde tu computador configurado

**¡LISTO! El bot correrá 24/7 independientemente de tu computador** 🚀

---

## 📞 Soporte

Si tienes problemas:

1. Revisa logs: `tail -100 ~/trading-bots/Argos/argos_bot.log`
2. Verifica estado: `sudo systemctl status argos-bot`
3. Test manual: `cd ~/trading-bots/Argos && source venv/bin/activate && python main.py`

---

**Última actualización**: 7 de enero de 2026  
**Costo mensual**: $0 (Oracle Free Tier) o $5 (DigitalOcean)  
**Uptime esperado**: 99.9%
