# 🔒 Guía de Seguridad - Argos Trading Bot

## ⚠️ ALERTA: API Keys Expuestas

Si tus API keys de Binance fueron subidas a GitHub en algún momento, **debes rotarlas inmediatamente**.

---

## 🚨 Acción Inmediata Requerida

### 1. Rotar API Keys de Binance

**Testnet**:
1. Ve a https://testnet.binance.vision/
2. Elimina las API keys actuales
3. Genera nuevas API keys
4. Actualiza tu archivo `.env` local

**Mainnet** (si llegaste a usarlas):
1. Ve a https://www.binance.com/en/my/settings/api-management
2. **ELIMINA INMEDIATAMENTE** las API keys actuales
3. Genera nuevas API keys con permisos mínimos:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ Enable Withdrawals (NUNCA habilitar)
   - ❌ Enable Internal Transfer
4. Configura IP Whitelist (restringir a tu IP)
5. Actualiza tu archivo `.env` local

### 2. Rotar Token de Telegram

1. Habla con @BotFather en Telegram
2. Usa `/revoke` para revocar el token actual
3. Usa `/newbot` o `/settoken` para generar uno nuevo
4. Actualiza `TELEGRAM_TOKEN` en `.env`

---

## ✅ Verificación de Seguridad

### Archivos protegidos

Verifica que estos archivos NO estén en git:

```bash
# Debe devolver "vacío" (no encontrar nada)
git ls-files | grep -E "\.env$|\.env\."

# Si devuelve algún archivo, elimínalo del historial (ver sección siguiente)
```

### Contenido de .gitignore

El archivo `.gitignore` debe incluir:

```
# Credenciales
.env
.env.*
*.env

# Bases de datos
*.db
*.sqlite

# Logs
*.log
```

---

## 🔥 Limpiar Historial de Git (Si es necesario)

Si subiste `.env` o credenciales al repositorio, debes limpiar el historial:

### Opción 1: BFG Repo-Cleaner (Recomendado)

```bash
# Instalar BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Clonar repo completo
git clone --mirror https://github.com/Medalcode/Argos.git

# Eliminar .env del historial
java -jar bfg-1.14.0.jar --delete-files .env Argos.git

# Limpiar refs
cd Argos.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Forzar push
git push --force
```

### Opción 2: git filter-branch

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env .env.testnet" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

### Opción 3: Empezar de Cero (Más seguro)

Si el repositorio tiene pocas contribuciones:

```bash
# 1. Hacer backup local
cp -r /home/medalcode/Antigravity/Argos /home/medalcode/Argos_backup

# 2. Eliminar repo remoto en GitHub
# (desde la web: Settings → Delete this repository)

# 3. Crear nuevo repositorio vacío
# (desde la web: New repository)

# 4. Reinicializar git local
cd /home/medalcode/Antigravity/Argos
rm -rf .git
git init
git add .
git commit -m "Initial commit - cleaned version"

# 5. Conectar con nuevo remoto
git remote add origin https://github.com/Medalcode/Argos-New.git
git branch -M main
git push -u origin main
```

---

## 🛡️ Mejores Prácticas de Seguridad

### 1. Nunca Commitear Credenciales

```bash
# Antes de cada commit, verifica
git status
git diff

# Asegúrate que .env no aparezca
```

### 2. Usar Variables de Entorno del Sistema

En lugar de `.env`, usa variables de sistema:

```bash
# En Linux/Mac (~/.bashrc o ~/.zshrc)
export BINANCE_API_KEY="tu_api_key"
export BINANCE_SECRET_KEY="tu_secret_key"

# En el código, úsalas directamente
import os
api_key = os.getenv('BINANCE_API_KEY')
```

### 3. Usar Secrets en Producción

Para deployment en servidores:

**GitHub Actions**:
```yaml
env:
  BINANCE_API_KEY: ${{ secrets.BINANCE_API_KEY }}
```

**Docker**:
```bash
docker run -e BINANCE_API_KEY="..." argos-bot
```

**systemd service**:
```ini
[Service]
Environment="BINANCE_API_KEY=..."
```

### 4. Rotar Keys Periódicamente

- **Testnet**: Cada 3-6 meses
- **Mainnet**: Cada 1-3 meses
- **Después de cualquier exposición**: INMEDIATAMENTE

### 5. Permisos Mínimos en API Keys

Para trading bot:
- ✅ Enable Reading
- ✅ Enable Spot Trading
- ❌ Enable Withdrawals (NUNCA)
- ❌ Enable Futures
- ❌ Enable Margin

### 6. IP Whitelist

Restringe las API keys a IPs conocidas:

```bash
# Obtener tu IP pública
curl ifconfig.me

# En Binance: API Management → Edit → Restrict access to trusted IPs only
# Agregar tu IP
```

### 7. Monitoreo de Actividad

- Revisa el historial de API en Binance regularmente
- Configura alertas de seguridad en Binance
- Monitorea transacciones sospechosas

---

## 🔍 Checklist de Seguridad

Antes de hacer push:

- [ ] `.env` está en `.gitignore`
- [ ] `.env` no aparece en `git status`
- [ ] Ningún archivo con credenciales en staging
- [ ] API keys rotadas (si hubo exposición)
- [ ] Telegram token actualizado
- [ ] Permisos mínimos en API keys
- [ ] IP Whitelist configurada (opcional pero recomendado)

---

## 📞 Contacto en Caso de Emergencia

Si sospechas que tus fondos están en riesgo:

1. **Desactiva API keys INMEDIATAMENTE** (Binance → API Management)
2. Cambia tu contraseña de Binance
3. Habilita 2FA si no lo tienes
4. Revisa historial de transacciones
5. Contacta a Binance Support si detectas actividad sospechosa

---

## 🛠️ Comandos Útiles

```bash
# Verificar que .env no está trackeado
git ls-files | grep .env

# Ver archivos ignorados
git status --ignored

# Ver historial de un archivo específico
git log --all --full-history -- .env

# Buscar texto en historial de git (ej: buscar una API key)
git log -S "texto_a_buscar" --all

# Ver qué archivos están en staging
git diff --cached --name-only
```

---

## 📚 Referencias

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html)

---

**Última actualización**: 7 de enero de 2026  
**Estado**: ✅ `.env` protegido - ⚠️ Rotar keys por precaución
