# Métricas de Performance - Argos Trading Bot

## 📊 Descripción

Sistema avanzado de métricas para evaluar objetivamente la performance del bot de trading. Incluye métricas estándar de la industria financiera para análisis profesional.

---

## 📈 Métricas Implementadas

### 1. 🎯 **Sharpe Ratio**

**Definición**: Mide el retorno ajustado por riesgo. Indica cuánto retorno adicional obtienes por cada unidad de riesgo (volatilidad).

**Fórmula**:
```
Sharpe Ratio = (Retorno Promedio - Tasa Libre de Riesgo) / Desviación Estándar
```

**Interpretación**:
- **< 0**: Malo (retorno negativo)
- **0 - 1**: Pobre (mucho riesgo vs retorno)
- **1 - 2**: Bueno (retorno aceptable)
- **2 - 3**: Muy bueno (excelente retorno)
- **> 3**: Excepcional

**Uso**:
```python
from metricas import MetricasPerformance

metricas = MetricasPerformance()
sharpe = metricas.calcular_sharpe_ratio(periodo_dias=30)
print(f"Sharpe Ratio (30d): {sharpe}")
```

**Ejemplo**: Un Sharpe de 2.5 significa que obtienes 2.5 unidades de retorno por cada unidad de riesgo.

---

### 2. 📉 **Maximum Drawdown (Max DD)**

**Definición**: Mayor caída porcentual desde un pico hasta un valle. Mide el peor escenario de pérdida.

**Fórmula**:
```
Max DD = ((Pico - Valle) / Pico) × 100
```

**Interpretación**:
- **< 5%**: Excelente (bajo riesgo)
- **5-10%**: Bueno (riesgo moderado)
- **10-20%**: Aceptable (riesgo medio)
- **20-30%**: Alto (riesgo significativo)
- **> 30%**: Muy alto (riesgo extremo)

**Uso**:
```python
max_dd, fecha_pico, fecha_valle = metricas.calcular_maximum_drawdown(30)
print(f"Max Drawdown: {max_dd}% (desde {fecha_pico} hasta {fecha_valle})")
```

**Ejemplo**: Un Max DD de 8% significa que en el peor momento perdiste 8% desde tu pico de capital.

---

### 3. 💰 **Profit Factor**

**Definición**: Ratio entre ganancias totales y pérdidas totales. Mide la rentabilidad bruta.

**Fórmula**:
```
Profit Factor = Ganancias Totales / Pérdidas Totales
```

**Interpretación**:
- **< 1**: Malo (pérdidas superan ganancias)
- **1 - 1.5**: Aceptable (ligeramente rentable)
- **1.5 - 2**: Bueno (ganancias duplican pérdidas)
- **2 - 3**: Muy bueno (ganancias triplican pérdidas)
- **> 3**: Excelente

**Uso**:
```python
pf = metricas.calcular_profit_factor(periodo_dias=30)
print(f"Profit Factor: {pf}")
```

**Ejemplo**: Un PF de 2.5 significa que por cada $1 perdido, ganas $2.50.

---

### 4. 💵 **Expectancy**

**Definición**: Valor esperado en USD por cada trade. Indica cuánto esperas ganar/perder en promedio.

**Fórmula**:
```
Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
```

**Interpretación**:
- **> 0**: Positivo (rentable a largo plazo)
- **< 0**: Negativo (no rentable)
- **> $10**: Muy bueno para trading con capital moderado
- **> $50**: Excelente

**Uso**:
```python
exp = metricas.calcular_expectancy(periodo_dias=30)
print(f"Expectancy: ${exp} por trade")
```

**Ejemplo**: Una expectancy de $15 significa que cada vez que operas, esperas ganar $15 en promedio.

---

### 5. 🔄 **Recovery Factor**

**Definición**: Capacidad de recuperación del sistema. Mide qué tan rápido recuperas pérdidas.

**Fórmula**:
```
Recovery Factor = Net Profit / Maximum Drawdown
```

**Interpretación**:
- **< 2**: Bajo (recuperación lenta)
- **2 - 5**: Aceptable (recuperación moderada)
- **5 - 10**: Bueno (buena recuperación)
- **> 10**: Excelente (recuperación rápida)

**Uso**:
```python
rf = metricas.calcular_recovery_factor(periodo_dias=30)
print(f"Recovery Factor: {rf}")
```

**Ejemplo**: Un RF de 8 significa que el profit neto es 8 veces mayor que el peor drawdown.

---

### 6. 📊 **Win Rate por Periodo**

**Definición**: Porcentaje de trades ganadores en diferentes periodos (diario/semanal/mensual).

**Fórmula**:
```
Win Rate = (Trades Ganadores / Total Trades) × 100
```

**Interpretación**:
- **< 40%**: Bajo (requiere alto ratio ganancia/pérdida)
- **40-50%**: Aceptable (típico en trading)
- **50-60%**: Bueno (rentable con ratios 1:1)
- **> 60%**: Muy bueno (alta consistencia)

**Uso**:
```python
win_rates = metricas.calcular_win_rate_por_periodo("diario")
for wr in win_rates[:10]:
    print(f"{wr['periodo']}: {wr['win_rate']}% ({wr['ganadoras']}/{wr['total']})")
```

---

### 7. 📉 **MAE (Maximum Adverse Excursion)**

**Definición**: Máxima pérdida flotante durante un trade antes de cerrarlo. Mide el "susto" máximo.

**Uso**: Ayuda a optimizar stop loss.

---

### 8. 📈 **MFE (Maximum Favorable Excursion)**

**Definición**: Máxima ganancia flotante durante un trade antes de cerrarlo. Mide el potencial máximo.

**Uso**: Ayuda a optimizar take profit y trailing stop.

---

## 🎯 Reporte Completo

Genera un reporte con todas las métricas:

```python
from metricas import MetricasPerformance, imprimir_reporte_consola

metricas = MetricasPerformance()

# Generar reporte
reporte = metricas.generar_reporte_completo(periodo_dias=30)

# Imprimir en consola
imprimir_reporte_consola(reporte)

# Acceder a valores específicos
print(f"Sharpe: {reporte['sharpe_ratio']}")
print(f"Max DD: {reporte['max_drawdown_pct']}%")
print(f"Win Rate: {reporte['win_rate_promedio']}%")
```

**Output de ejemplo**:
```
======================================================================
  📊 REPORTE DE MÉTRICAS DE PERFORMANCE (30 días)
======================================================================

🎯 MÉTRICAS PRINCIPALES:
  • Sharpe Ratio: 2.34 - Muy bueno (excelente retorno ajustado)
  • Maximum Drawdown: 7.5% - Bueno (riesgo moderado)
  • Profit Factor: 2.8 - Muy bueno (ganancias triplican pérdidas)
  • Expectancy: $18.50 por trade
  • Recovery Factor: 9.2 - Bueno (buena recuperación)

📈 ESTADÍSTICAS GENERALES:
  • Total Trades: 45
  • Win Rate Promedio: 58.00%
  • PnL Total: $832.50
  • PnL Promedio: 1.85%
  • Mejor Trade: $125.00
  • Peor Trade: -$45.00
  • Duración Promedio: 135 minutos

💹 MAE/MFE:
  • MAE Promedio: $12.50
  • MFE Promedio: $38.20

📉 Drawdown Máximo:
  • Pico: 2026-01-05T14:30:00
  • Valle: 2026-01-06T09:15:00

======================================================================
```

---

## 📊 Integración con Dashboard

Puedes integrar las métricas en el dashboard de Rich:

```python
from rich.table import Table
from metricas import MetricasPerformance

metricas = MetricasPerformance()
reporte = metricas.generar_reporte_completo(30)

# Crear tabla de métricas
tabla_metricas = Table(title="📊 Métricas de Performance (30d)")
tabla_metricas.add_column("Métrica", style="cyan")
tabla_metricas.add_column("Valor", style="green")
tabla_metricas.add_column("Interpretación", style="yellow")

tabla_metricas.add_row(
    "Sharpe Ratio",
    str(reporte['sharpe_ratio']),
    reporte['interpretacion']['sharpe']
)
tabla_metricas.add_row(
    "Max Drawdown",
    f"{reporte['max_drawdown_pct']}%",
    reporte['interpretacion']['max_dd']
)

console.print(tabla_metricas)
```

---

## 📚 Comandos de Script

### Generar reporte por periodo

```bash
# Reporte de 7 días
python -c "from metricas import MetricasPerformance, imprimir_reporte_consola; m = MetricasPerformance(); imprimir_reporte_consola(m.generar_reporte_completo(7))"

# Reporte de 30 días (default)
python metricas.py

# Reporte de 90 días
python -c "from metricas import MetricasPerformance, imprimir_reporte_consola; m = MetricasPerformance(); imprimir_reporte_consola(m.generar_reporte_completo(90))"
```

---

## 🎯 Benchmarks de la Industria

### Comparación con estrategias profesionales

| Métrica | Argos Target | Trading Profesional | Hedge Funds |
|---------|--------------|---------------------|-------------|
| **Sharpe Ratio** | > 1.5 | > 1.0 | > 2.0 |
| **Max Drawdown** | < 15% | < 20% | < 10% |
| **Profit Factor** | > 1.8 | > 1.5 | > 2.5 |
| **Win Rate** | > 50% | 40-60% | 50-70% |
| **Recovery Factor** | > 5 | > 3 | > 8 |

---

## 🔍 Análisis de Mejora

### Cómo usar las métricas para mejorar

1. **Sharpe Ratio bajo** → Reducir volatilidad (tighter stops, menor leverage)
2. **Max DD alto** → Mejorar gestión de riesgo (trailing stops más conservadores)
3. **Profit Factor < 1.5** → Revisar filtros de entrada (mejores señales)
4. **Win Rate < 40%** → Mejorar timing de entrada o reducir operaciones
5. **Recovery Factor bajo** → Optimizar trailing stop (capturar más ganancia)
6. **MAE alto** → Stops demasiado amplios (ajustar niveles)
7. **MFE no capturado** → Trailing stop demasiado agresivo (dar más margen)

---

## ⚙️ Configuración Avanzada

### Personalizar cálculos

```python
from metricas import MetricasPerformance

metricas = MetricasPerformance()

# Sharpe con tasa libre de riesgo del 4% anual
sharpe = metricas.calcular_sharpe_ratio(
    periodo_dias=30,
    rf_rate=0.04/252  # 4% anual / 252 días
)

# Win rate semanal
win_rates = metricas.calcular_win_rate_por_periodo("semanal")

# Drawdown de 90 días
max_dd, pico, valle = metricas.calcular_maximum_drawdown(90)
```

---

## 📊 Export a CSV

Exportar métricas para análisis externo:

```python
import csv
from metricas import MetricasPerformance

metricas = MetricasPerformance()
reporte = metricas.generar_reporte_completo(30)

# Guardar en CSV
with open('metricas_performance.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Métrica', 'Valor'])
    writer.writerow(['Sharpe Ratio', reporte['sharpe_ratio']])
    writer.writerow(['Max Drawdown', reporte['max_drawdown_pct']])
    writer.writerow(['Profit Factor', reporte['profit_factor']])
    writer.writerow(['Expectancy', reporte['expectancy_usd']])
```

---

## 🚀 Automatización

### Generar reporte diario automático

```python
from metricas import MetricasPerformance
from datetime import datetime
import json

metricas = MetricasPerformance()
reporte = metricas.generar_reporte_completo(30)

# Guardar como JSON
with open(f"metricas_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
    json.dump(reporte, f, indent=2)

# Enviar por Telegram
from notificaciones import enviar_telegram

mensaje = f"""
📊 Reporte Diario de Performance

🎯 Sharpe Ratio: {reporte['sharpe_ratio']}
📉 Max Drawdown: {reporte['max_drawdown_pct']}%
💰 Profit Factor: {reporte['profit_factor']}
📈 Win Rate: {reporte['win_rate_promedio']}%
💵 PnL Total: ${reporte['pnl_total']}
"""

enviar_telegram(mensaje)
```

---

**Documentación generada**: 7 de enero de 2026  
**Versión del Bot**: 2.3.0  
**Framework**: Python 3.13 + SQLite
