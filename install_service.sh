#!/bin/bash
# Script para instalar Argos como servicio systemd
# Esto permitirá que el bot corra 24/7 en tu computador

echo "🤖 Instalando Argos Bot como servicio del sistema..."
echo ""

# Obtener ruta actual
ARGOS_DIR=$(pwd)
USER=$(whoami)

# Crear archivo de servicio
sudo tee /etc/systemd/system/argos.service > /dev/null << EOF
[Unit]
Description=Argos Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$ARGOS_DIR
Environment="PATH=$ARGOS_DIR/venv/bin:/usr/bin:/bin"
ExecStart=$ARGOS_DIR/venv/bin/python $ARGOS_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$ARGOS_DIR/argos_bot.log
StandardError=append:$ARGOS_DIR/argos_bot.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Archivo de servicio creado"
echo ""

# Recargar systemd
echo "📋 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar servicio (se inicia al boot)
echo "🔧 Habilitando servicio..."
sudo systemctl enable argos.service

# Detener bot si está corriendo manualmente
echo "🛑 Deteniendo bot manual..."
pkill -f "python main.py" 2>/dev/null || true
sleep 2

# Iniciar servicio
echo "🚀 Iniciando servicio..."
sudo systemctl start argos.service

sleep 3

# Verificar estado
echo ""
echo "📊 Estado del servicio:"
sudo systemctl status argos.service --no-pager

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ✅ ARGOS BOT INSTALADO COMO SERVICIO               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 El bot ahora:"
echo "  ✅ Se inicia automáticamente al encender el PC"
echo "  ✅ Se reinicia automáticamente si falla"
echo "  ✅ Corre en segundo plano siempre"
echo ""
echo "🛠️ Comandos útiles:"
echo "  Ver estado:     sudo systemctl status argos"
echo "  Ver logs:       tail -f $ARGOS_DIR/argos_bot.log"
echo "  Detener:        sudo systemctl stop argos"
echo "  Iniciar:        sudo systemctl start argos"
echo "  Reiniciar:      sudo systemctl restart argos"
echo "  Deshabilitar:   sudo systemctl disable argos"
echo ""
