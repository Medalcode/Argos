# BITÁCORA DE DESPLIEGUE EN TELÉFONO

Fecha: 2026-01-23

Resumen: durante el intento de desplegar las últimas mejoras directamente en un teléfono Android conectado por ADB, realicé una serie de acciones para dejar la app ejecutable en el dispositivo. A continuación se documentan los pendientes, motivos y decisiones tomadas.

1) Estado del despliegue
- Proyecto extraído en: `/data/local/tmp/extracted_argos`
- Interprete portable instalado en: `/data/local/tmp/python_root/usr/bin/python3.12`
- Se agregó modo degradado en `main.py` para ejecutar sin dependencias pesadas.

2) Pendientes / No instalable en el teléfono (motivo)
- `cryptography`: Requiere Rust/maturin o ruedas precompiladas para CPython 3.12 aarch64. pip build falla en el dispositivo (no hay toolchain). -> No se pudo instalar.
- `numpy`, `pandas`, `numba`, `llvmlite`: requieren compilación o ruedas binarias que no están disponibles por defecto. Sin build toolchain en Android, pip intenta compilar y falla. -> No se pudieron instalar.
- `pydantic-core` / `fastapi` (si estaba en requirements): requiere Rust/maturin; no instalable sin toolchain. -> descartado para instalación en teléfono.

3) Soluciones aplicadas
- Excluí el `venv` del tar al sincronizar (evita symlinks rotos en Android).
- Extraje un runtime Python portable (paquetes Termux) y subí librerías nativas necesarias (zlib, libexpat, openssl, libandroid-support, etc.).
- Bootstrapeé `pip` con `get-pip.py` y pude instalar paquetes ligeros (`requests`, `rich`, `python-dotenv`, `jinja2`, `tabulate`, `python-multipart`).
- En `main.py` se añadieron comprobaciones `HAS_CCXT`, `HAS_PANDAS`, `HAS_PANDAS_TA` y un `run_degraded_loop()` que inicia la app en modo degradado cuando faltan dependencias críticas.

4) Qué queda pendiente (acciones propuestas)
- Opción A: Buscar e instalar ruedas (`.whl`) precompiladas para `cryptography`, `numpy` y `pandas` específicas para CPython 3.12 aarch64. (Puede funcionar pero requiere tiempo y no garantiza que existan todas las ruedas.)
- Opción B: Aceptar modo degradado permanentemente; eliminar/archivar funcionalidades que dependan de paquetes no instalables y documentarlo en la bitácora. (Rápido y estable en el teléfono.)
- Opción C: Ejecutar la versión completa en un VPS/PC donde la instalación de dependencias es trivial y mantener el teléfono como cliente ligero.

5) Comandos y rutas útiles
- Proyecto en el teléfono: `/data/local/tmp/extracted_argos`
- Log principal: `/data/local/tmp/extracted_argos/argos_bot.log`
- Intérprete portable: `/data/local/tmp/python_root/usr/bin/python3.12`
- Para reiniciar (ejemplo):
  LD_LIBRARY_PATH=/data/local/tmp/python_root/usr/lib /data/local/tmp/python_root/usr/bin/python3.12 /data/local/tmp/extracted_argos/main.py >> /data/local/tmp/extracted_argos/argos_bot.log 2>&1 &

6) Decisión tomada ahora
- Se dejó el modo degradado por defecto si faltan `ccxt`/`pandas`/`pandas_ta` y se implementó `BITACORA.md` para dejar constancia de los motivos por los que no se instalaron ciertas dependencias.

Firmado: despliegue automatizado (acciones realizadas vía ADB desde el repositorio local)
