#!/usr/bin/env bash
set -e
# Instalador orientado a Termux / Android (no usa systemd)
echo "Instalador Termux para Argos"

SCRIPT_DIR=$(pwd)
echo "Directorio actual: $SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 no encontrado. Instala 'python' en Termux: pkg install python"
  exit 1
fi

if [ ! -f requirements.txt ]; then
  echo "requirements.txt no encontrado en $SCRIPT_DIR. Abortando."
  exit 1
fi

echo "Creando virtualenv en venv (si no existe)"
python3 -m venv venv || { echo 'Fallo creando virtualenv'; exit 2; }
source venv/bin/activate
pip install --upgrade pip
echo "Instalando dependencias..."
pip install -r requirements.txt || { echo 'pip install falló'; exit 3; }

echo "Creando script de arranque: run_argos.sh"
cat > run_argos.sh <<'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
source venv/bin/activate
nohup python3 main.py >> argos_bot.log 2>&1 &
echo $! > argos.pid
EOF

chmod +x run_argos.sh

echo "Instalación completa. Para ejecutar: ./run_argos.sh"
echo "Para ejecutar al inicio en Termux instala 'termux:boot' y coloca un enlace a run_argos.sh en ~/.termux/boot/"
echo "Comandos útiles:"
echo "  ./run_argos.sh      -> iniciar en background"
echo "  tail -f argos_bot.log"
echo "  kill \$(cat argos.pid)"

exit 0
