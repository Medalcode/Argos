# 🤖 ARGOS Trading Bot v2.4.0

Bot de trading algorítmico profesional para **Binance Spot** con estrategia Triple Filtro, Trailing Stop dinámico y Dashboard Web.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Tests](https://img.shields.io/badge/Tests-100%25-success.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ⭐ Novedades v2.4

- 📊 **Web Dashboard**: Panel en tiempo real en `http://localhost:8000`.
- 🐳 **Docker**: Despliegue en un solo comando con `docker-compose`.
- 🧠 **Optimizador AI**: Grid Search con multiprocessing para encontrar los mejores parámetros.
- 📚 **Docs Consolidados**: Toda la documentación ordenada en `docs/`.

---

## 🚀 Inicio Rápido (Docker)

La forma recomendada de ejecutar Argos.

```bash
# 1. Configurar credenciales
cp .env.example .env
nano .env

# 2. Iniciar Bot + Dashboard
docker-compose up -d

# 3. Ver Dashboard
# Abre http://localhost:8000 en tu navegador
```

---

## 📚 Documentación

Toda la información detallada se encuentra en la carpeta `docs/`.

| Documento                              | Descripción                                                |
| -------------------------------------- | ---------------------------------------------------------- |
| [📖 DEPLOYMENT.md](docs/DEPLOYMENT.md) | Guía de instalación en VPS y gestión de credenciales.      |
| [🧪 TESTING.md](docs/TESTING.md)       | Guía de tests unitarios y validación en Testnet.           |
| [🗄️ DATABASE.md](docs/DATABASE.md)     | Esquema de la base de datos SQLite.                        |
| [📈 METRICS.md](docs/METRICS.md)       | Explicación de métricas de performance (Sharpe, Drawdown). |
| [🛡️ SECURITY.md](docs/SECURITY.md)     | Política de seguridad y manejo de secretos.                |
| [📝 CHANGELOG.md](docs/CHANGELOG.md)   | Historial de cambios y versiones.                          |

---

## 🛠️ Herramientas Extra

### Optimización de Estrategia

Encuentra los parámetros matemáticamente perfectos para el mercado actual:

```bash
python3 optimize.py
```

### Tests

Ejecuta la suite de pruebas para asegurar la estabilidad:

```bash
pytest tests/
```

---

## ⚠️ Disclaimer

Este software es para fines educativos. El trading de criptomonedas conlleva alto riesgo. Usa el **Modo Testnet** (ver `docs/TESTING.md`) antes de arriesgar capital real.
