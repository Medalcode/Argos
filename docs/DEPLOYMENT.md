# 🚀 Argos Deployment Guide

Guía definitiva para desplegar Argos Trading Bot en un servidor (VPS) o localmente.

## 🐳 Despliegue con Docker (Recomendado)

La forma más fácil y robusta de ejecutar Argos.

### Prerrequisitos

- Docker y Docker Compose instalados.

### Pasos

1. **Configura tus credenciales**:
   Copia `.env.example` a `.env` y rellena tus datos.
2. **Ejecuta el bot**:

   ```bash
   docker-compose up -d
   ```

3. **Monitorea**:
   - Logs: `docker-compose logs -f`
   - Dashboard: `http://localhost:8000`

---

## ☁️ Despliegue en VPS (Tradicional)

Si prefieres u no usar Docker o tienes un VPS muy limitado.

### Script Automático

Hemos incluido un script para Ubuntu/Debian:

```bash
wget https://raw.githubusercontent.com/Medalcode/Argos/main/deploy_vps.sh
chmod +x deploy_vps.sh
./deploy_vps.sh
```

### Instalación Manual

1. **Clonar Repo**: `git clone https://github.com/Medalcode/Argos.git`
2. **Setup Python**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Ejecutar**: `nohup python main.py &`

---

## 🔑 Gestión de Credenciales

### 1. Binance API

1. Ve a [Gestión de API](https://www.binance.com/en/my/settings/api-management).
2. Crear API (System Generated).
3. **Permisos**:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ **Enable Withdrawals** (NUNCA ACTIVAR)

### 2. Telegram Bot

1. Habla con [@BotFather](https://t.me/BotFather).
2. Comando `/newbot`.
3. Copia el **Token**.
4. Habla con [@userinfobot](https://t.me/userinfobot) para obtener tu `ID`.

### 3. Seguridad

- Nunca subas el archivo `.env` a GitHub.
- Usa una IP Whitelist en Binance si tienes IP estática en tu VPS.
