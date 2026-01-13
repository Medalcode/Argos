#!/bin/bash
# Script de Deployment Automatizado para VPS
# Uso: ./deploy_vps.sh

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🚀 DEPLOYMENT DE ARGOS BOT EN VPS                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Actualizar sistema
echo -e "${YELLOW}[1/8] Actualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
echo -e "${YELLOW}[2/8] Instalando dependencias...${NC}"
sudo apt install -y python3 python3-pip python3-venv git htop

# 3. Crear directorio
echo -e "${YELLOW}[3/8] Creando directorio del proyecto...${NC}"
mkdir -p ~/trading-bots
cd ~/trading-bots

# 4. Clonar repositorio
echo -e "${YELLOW}[4/8] Clonando repositorio...${NC}"
if [ -d "Argos" ]; then
    echo "Directorio ya existe, actualizando..."
    cd Argos
    git pull origin main
else
    git clone https://github.com/Medalcode/Argos.git
    cd Argos
fi

# 5. Crear entorno virtual
echo -e "${YELLOW}[5/8] Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependencias Python
echo -e "${YELLOW}[6/8] Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 7. Configurar .env
echo -e "${YELLOW}[7/8] Configurando archivo .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}IMPORTANTE: No existe archivo .env${NC}"
    echo "Copiando .env.example a .env"
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}⚠️  DEBES EDITAR .env CON TUS CREDENCIALES:${NC}"
    echo "   nano .env"
    echo ""
    echo "Presiona ENTER para continuar cuando hayas editado .env..."
    read
fi

# 8. Crear servicio systemd
echo -e "${YELLOW}[8/8] Creando servicio systemd...${NC}"

SCRIPT_DIR=$(pwd)
USER=$(whoami)

sudo tee /etc/systemd/system/argos-bot.service > /dev/null <<EOF
[Unit]
Description=Argos Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/argos_bot.log
StandardError=append:$SCRIPT_DIR/argos_bot.log

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable argos-bot.service

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ DEPLOYMENT COMPLETADO                              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📋 COMANDOS PARA CONTROLAR EL BOT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Iniciar:     sudo systemctl start argos-bot"
echo "  Detener:     sudo systemctl stop argos-bot"
echo "  Reiniciar:   sudo systemctl restart argos-bot"
echo "  Estado:      sudo systemctl status argos-bot"
echo "  Ver logs:    tail -f $SCRIPT_DIR/argos_bot.log"
echo "  Monitor:     cd $SCRIPT_DIR && ./monitor.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Edita .env con tus credenciales: nano .env"
echo "   2. Inicia el bot: sudo systemctl start argos-bot"
echo "   3. Verifica estado: sudo systemctl status argos-bot"
echo ""
