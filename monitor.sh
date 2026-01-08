#!/bin/bash
# Script de monitoreo del bot Argos
# Uso: ./monitor.sh

cd /home/medalcode/Antigravity/Argos

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🤖 MONITOR DEL BOT ARGOS - TESTNET                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Estado del proceso
echo "📊 ESTADO DEL PROCESO:"
if ps aux | grep -v grep | grep "python main.py" > /dev/null; then
    PID=$(ps aux | grep -v grep | grep "python main.py" | awk '{print $2}')
    UPTIME=$(ps -p $PID -o etime= | tr -d ' ')
    CPU=$(ps -p $PID -o %cpu= | tr -d ' ')
    MEM=$(ps -p $PID -o %mem= | tr -d ' ')
    echo "  ✅ Bot ACTIVO"
    echo "  📍 PID: $PID"
    echo "  ⏱️  Uptime: $UPTIME"
    echo "  💻 CPU: ${CPU}%"
    echo "  🧠 RAM: ${MEM}%"
else
    echo "  ❌ Bot NO está corriendo"
    echo ""
    echo "Para iniciar: python main.py"
    exit 1
fi

echo ""

# 2. Últimas líneas del log
echo "📝 ÚLTIMAS OPERACIONES (5 líneas):"
tail -5 argos_bot.log | sed 's/^/  /'
echo ""

# 3. Estado de la base de datos
echo "💾 ESTADO DE LA BASE DE DATOS:"
python3 << EOF
from database import Database
import sys

try:
    with Database() as db:
        estado = db.cargar_estado()
        stats = db.obtener_estadisticas_globales()
        
        print(f"  Posición: {'🟢 ABIERTA' if estado['posicion_abierta'] else '⚪ CERRADA'}")
        
        if estado['posicion_abierta']:
            print(f"  Precio Compra: \${estado['precio_compra']:,.2f}")
            print(f"  Cantidad: {estado['cantidad']:.6f} BTC")
            print(f"  Max Precio: \${estado['max_precio']:,.2f}")
        
        print(f"  PnL Acumulado Hoy: \${estado['pnl_acumulado']:.2f}")
        print(f"  Operaciones Hoy: {estado['operaciones_hoy']}")
        print(f"")
        print(f"  📈 ESTADÍSTICAS GLOBALES:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Win Rate: {stats['win_rate']:.2f}%")
        print(f"  PnL Total: \${stats['pnl_total']:.2f}")
        
        if stats['total_trades'] > 0:
            print(f"  Mejor Trade: \${stats['mejor_trade']:.2f}")
            print(f"  Peor Trade: \${stats['peor_trade']:.2f}")
            print(f"  Duración Prom: {stats['duracion_promedio']:.0f} min")

except Exception as e:
    print(f"  ❌ Error al leer DB: {e}")
    sys.exit(1)
EOF

echo ""

# 4. Tamaño de archivos
echo "📂 ARCHIVOS:"
echo "  Log: $(ls -lh argos_bot.log 2>/dev/null | awk '{print $5}')"
echo "  DB: $(ls -lh argos.db 2>/dev/null | awk '{print $5}' || echo 'No existe')"
echo ""

# 5. Comandos útiles
echo "🛠️  COMANDOS ÚTILES:"
echo "  Ver logs en vivo:    tail -f argos_bot.log"
echo "  Ver dashboard:       clear && watch -n 5 ./monitor.sh"
echo "  Métricas completas:  python metricas.py"
echo "  Detener bot:         pkill -f 'python main.py'"
echo "  Reiniciar bot:       pkill -f 'python main.py' && python main.py &"
echo ""
echo "Última actualización: $(date '+%Y-%m-%d %H:%M:%S')"
