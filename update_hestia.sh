#!/data/data/com.termux/files/usr/bin/bash
# Script para actualizar Argos/Hestia en Termux
set -e

# Actualizar paquetes del sistema
pkg update -y && pkg upgrade -y

# Actualizar pip y dependencias Python
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install --upgrade -r requirements.txt
fi

# Actualizar repositorio (si es git)
if [ -d .git ]; then
    git pull
fi

# Reiniciar bots principales
pkill -f "python main.py" || true
pkill -f "python memoria.py" || true
sleep 2
nohup python main.py &
nohup python memoria.py &

# Mensaje final
echo "✅ Actualización completa y bots reiniciados."
