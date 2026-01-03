# 🔑 Guía para obtener tus Credenciales

Sigue estos pasos para obtener las claves necesarias para tu bot.

---

## 1. Telegram (Para recibir notificaciones)

Necesitamos dos cosas: el **Token del Bot** y tu **Chat ID**.

### Paso A: Crear el Bot

1. Abre Telegram en tu celular o PC.
2. En el buscador, escribe `@BotFather` (asegúrate de que tenga el verificado azul).
3. Inicia el chat y escribe: `/newbot`
4. Te pedirá un nombre (ej: `ArgosBot`).
5. Te pedirá un usuario (debe terminar en `bot`, ej: `Argos_Moi_bot`).
6. **¡Listo!** Te dará un mensaje con letras rojas que dice: `Use this token to access the HTTP API:`.
   - Copia esa cadena larga de texto/números.
   - Pégala en tu archivo `.env` donde dice `TELEGRAM_TOKEN`.

### Paso B: Obtener tu ID

1. En Telegram, busca `@userinfobot`.
2. Dale a "Iniciar" o escribe cualquer cosa.
3. Te responderá con un mensaje tipo:
   ```
   Id: 123456789
   First Name: TuNombre
   ...
   ```
4. Copia el número que aparece en `Id`.
5. Pégalo en tu archivo `.env` donde dice `TELEGRAM_CHAT_ID`.

---

## 2. Binance (Para leer precios y operar)

Necesitamos la **API Key** y el **Secret Key**.

1. Inicia sesión en tu cuenta de [Binance](https://www.binance.com/).
2. Ve al icono de tu perfil (arriba a la derecha) -> **Gestión de API** (API Management).
3. Haz clic en **Crear API** -> Selecciona "Generada por el sistema".
4. Ponle un nombre (ej: `ArgosBot`).
5. Completa la verificación de seguridad (código por email/SMS/Authenticator).
6. **¡IMPORTANTE!** Verás tu `API Key` y `Secret Key`.
   - **COPIA LA SECRET KEY AHORA.** Binance la ocultará para siempre si recargas la página.
7. Opciones de Seguridad (Editar restricciones):
   - ✅ **Enable Reading** (Habilitar lectura) - Viene activa por defecto.
   - ✅ **Enable Spot & Margin Trading** (Habilitar Spot) - **MÁRCALA** para que el bot pueda comprar/vender.
   - ❌ **Enable Withdrawals** (Habilitar retiros) - **NUNCA la marques**. Así, si te roban la clave, no pueden sacar tu dinero.
8. Pega la `API Key` en `BINANCE_API_KEY` dentro del `.env`.
9. Pega la `Secret Key` en `BINANCE_SECRET_KEY` dentro del `.env`.

---

### Resumen del archivo .env

Tu archivo debería verse algo así al terminar:

```env
BINANCE_API_KEY=xXj78... (tu clave larga)
BINANCE_SECRET_KEY=9aL0... (tu secreto largo)
TELEGRAM_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
...
```
