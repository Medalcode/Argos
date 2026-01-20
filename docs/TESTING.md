# 🧪 Argos Testing Master Guide

Este documento consolida toda la información relacionada con el testing del bot Argos, desde pruebas unitarias hasta la validación en Testnet.

## 📋 Índice

1. [Tests Unitarios](#-tests-unitarios)
2. [Pruebas en Testnet](#-pruebas-en-testnet)
3. [Plan de Validación](#-plan-de-validación)

---

## 🔬 Tests Unitarios

Suite completa de tests unitarios implementada con **pytest** para validar la lógica crítica.

### Ejecución Rápida

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=. --cov-report=html
```

### Cobertura Actual

- **Memoria/Persistencia**: 100%
- **Indicadores Técnicos**: Validación de RSI, Bollinger y EMA.
- **Lógica de Trading**: Triple Filtro, Trailing Stop, SL/TP.

---

## 🌐 Pruebas en Testnet

### ⚠️ Prerrequisito: Cuenta Testnet

1. Visita [Binance Testnet](https://testnet.binance.vision/).
2. Logueate con GitHub y genera API Keys.
3. Solicita fondos ficticios (USDT).

### Configuración `.env`

Crea un archivo `.env` (o `.env.testnet`) con:

```bash
BINANCE_API_KEY=tu_testnet_key
BINANCE_SECRET_KEY=tu_testnet_secret
SIMULATION_MODE=False
# Descomenta en main.py: exchange.set_sandbox_mode(True)
```

### Checklist de Validación

Antes de ir a producción, verifica estos puntos en Testnet:

- [ ] Conexión exitosa y lectura de balance.
- [ ] Ejecución de compra REAL al cumplirse señal.
- [ ] Trailing Stop actualizando el precio de salida.
- [ ] Venta ejecutada por TP, SL o Trailing.
- [ ] Comandos de Telegram (`/status`, `/vender`) funcionando.

---

## 📅 Plan de Validación (2-4 Semanas)

### Fase 1: Estabilidad (Semana 1)

- **Objetivo**: 24h sin errores críticos.
- **Acción**: Dejar correr el bot en Docker/VPS.
- **Monitoreo**: Revisar logs cada 6h.

### Fase 2: Mecánica (Semana 2)

- **Objetivo**: 10 operaciones completas.
- **Verificación**: Que el PnL se calcule bien y las órdenes coincidan con Binance.

### Fase 3: Rentabilidad (Semana 3-4)

- **Objetivo**: Win Rate > 40% y Profit Factor > 1.2.
- **Ajuste**: Si WR bajo, ajustar RSI (30 -> 25). Si SL frecuentes, ampliar margen (1% -> 2%).

---

## 🚨 Troubleshooting Común

| Error                | Causa Probable          | Solución                                      |
| -------------------- | ----------------------- | --------------------------------------------- |
| `Invalid API Key`    | Keys de prod en testnet | Generar nuevas keys en testnet.binance.vision |
| `MIN_NOTIONAL`       | Orden < $10 USD         | Aumentar `POSITION_SIZE_PCT`                  |
| `Insufficient Funds` | Sin USDT ficticio       | Pedir faucet en la web de testnet             |
