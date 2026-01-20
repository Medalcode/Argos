# 📱 Guía de Despliegue en Android (Termux)

¡Excelente idea! Tu viejo Motorola es perfecto para esto. Es básicamente un mini-servidor Linux de bajo consumo que puede correr 24/7.

Usaremos **Termux**, una potente terminal para Android.

---

## 📥 Paso 1: Instalar Termux

⛔ **NO uses la versión de Play Store** (está desactualizada).

1.  Descarga **F-Droid** (una tienda de apps open source) en tu celular: [f-droid.org](https://f-droid.org/).
2.  Instala F-Droid y ábrelo.
3.  Busca **Termux**.
4.  Instala **Termux** y **Termux:API**.

---

## 🛠️ Paso 2: Configuración Inicial

Abre Termux y ejecuta estos comandos (puedes conectar un teclado USB/Bluetooth o usar WhatsApp Web para copiar/pegar los comandos y enviártelos al móvil):

```bash
# 1. Actualizar repositorios
pkg update && pkg upgrade -y

# 2. Instalar dependencias base
pkg install python git rust binutils build-essential tur-repo -y

# 3. Instalar librerías matemáticas (para pandas/numpy)
pkg install python-numpy python-pandas -y
```

> **Nota**: Instalamos numpy/pandas desde pkg de Termux porque compilarlos en el celular puede tardar horas.

---

## 📥 Paso 3: Clonar Argos

```bash
# 1. Dar acceso al almacenamiento (opcional, para guardar backups fácil)
termux-setup-storage

# 2. Clonar el repositorio
git clone https://github.com/Medalcode/Argos.git

# 3. Entrar a la carpeta
cd Argos
```

---

## 🐍 Paso 4: Instalar Entorno Virtual

En Termux, a veces es mejor usar `--system-site-packages` para aprovechar el numpy/pandas que instalamos con `pkg`.

```bash
# 1. Crear entorno virtual (con acceso a librerías de sistema)
python -m venv venv --system-site-packages

# 2. Activar
source venv/bin/activate

# 3. Instalar resto de requerimientos (ignorando numpy/pandas que ya tenemos)
pip install -r requirements.txt --ignore-installed numpy pandas
```

---

## 🔑 Paso 5: Configuración

```bash
# 1. Crear .env
cp .env.example .env

# 2. Editar .env (nano es un editor de texto)
nano .env
```

- Navega con las flechas (o tocando la pantalla).
- Borra los valores de ejemplo y pon tus keys reales.
- Para guardar: **CTRL + O** (El botón CTRL suele aparecer arriba del teclado en Termux).
- Para salir: **CTRL + X**.

---

## 🚀 Paso 6: Ejecutar el Bot

```bash
python main.py
```

Si todo sale bien, verás los logs iniciando.

---

## 🔋 Paso 7: Mantenerlo vivo 24/7 (CRÍTICO)

Android intenta "matar" aplicaciones en segundo plano para ahorrar batería. Debemos evitarlo.

1.  **En la barra de notificaciones**: Verás una notificación de Termux "0 sessions". Expándela y dale a **"Acquire wakelock"**. Esto evita que el CPU se duerma.
2.  **Configuración de Android**:
    - Ve a Ajustes -> Batería -> Optimización de batería.
    - Busca Termux y selecciona "No optimizar" o "Sin restricciones".
3.  **Mantener pantalla encendida (Opcional)**:
    - Si el wakelock no basta, puedes dejar el cargador conectado y activar "Pantalla activa al cargar" en las opciones de desarrollador.

---

## 📡 Acceso Remoto (SSH)

Para controlar el bot desde tu PC sin tocar el celular:

1.  En Termux: `pkg install openssh`
2.  Ponle password: `passwd`
3.  Inicia el servidor: `sshd`
4.  Averigua tu IP: `ifconfig` (busca algo como `192.168.1.XX`).
5.  Desde tu PC: `ssh -p 8022 u0_aXXX@192.168.1.XX` (el usuario lo ves al escribir `whoami` en termux).

---

## 🐞 Solución de Problemas

- **Error "Killed"**: El celular se quedó sin RAM. Cierra otras apps.
- **Error compilando pandas**: Asegúrate de haber hecho `pkg install python-pandas` y usar `--system-site-packages` al crear el venv.
