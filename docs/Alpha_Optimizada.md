# AUTOTRADER AGENT — KNOWLEDGE BASE
# Estrategia Alpha — Momentum Rider v2.0

**Objetivo:** Capturar movimientos de tendencia alcista consolidada en criptomonedas, maximizando la captura de tendencias asimétricas y limitando las pérdidas mediante trailing stops basados en volatilidad.

## 1. Filosofía
La tendencia es válida hasta que la matemática demuestra lo contrario. Este agente no intenta predecir techos o suelos, ni anticipa el inicio de una tendencia. Reacciona a la evidencia de flujo de capital direccional y mantiene la posición mientras el momentum se sostenga.

**Principios del Agente:**
- **Paciencia Algorítmica:** Operar poco es un síntoma de salud. Se evitan los mercados laterales.
- **Protección de Capital:** El tamaño de la posición y los stops son estrictamente matemáticos. No se promedia a la baja. Nunca.

## 2. Filtros de Régimen y Contexto (Pre-Condiciones)
El agente DEBE validar estas condiciones secuencialmente. Si alguna falla, se aborta la evaluación del activo.

### Filtro A: Régimen Macro (BTC)
- **Tendencia BTC:** El precio de Bitcoin debe estar por encima de su EMA200 en marco de 4H.
- **Velocidad de caída:** No debe existir una vela bajista de BTC mayor al 4% en las últimas 8 horas.
- *Excepción de Correlación:* Si el activo tiene una correlación de 30 días con BTC < 0.3, puede operarse aunque BTC esté en rango, pero NO si BTC es bajista.

### Filtro B: Expansión de Volatilidad (Filtro Anti-Rango)
- **ATR Relativo:** El ATR(10) actual debe ser > Percentil 25 del ATR(10) de los últimos 60 días. (Evita operar compresiones).
- **Rango Mínimo:** Las últimas 5 velas 4H deben tener una amplitud combinada > 1.5% del precio.

## 3. Sistema de Evaluación (Score Dinámico de Entrada)
Si el activo pasa los Filtros de Régimen, se evalúa el Score. **Condición de entrada: Score Total >= 5.**

**Puntuaciones (+1 o +2 puntos por condición cumplida):**
1. **[ +2 ] Estructura de Medias:** Precio > EMA200 (4H) Y EMA20 > EMA50.
2. **[ +2 ] Estructura de Precio:** Mínimo de 3 velas consecutivas 4H formando máximos y mínimos crecientes (Higher Highs, Higher Lows).
3. **[ +1 ] Momentum Sano:** RSI (14) en pendiente positiva durante las últimas 3 velas. No importa el nivel absoluto, importa la derivada.
4. **[ +1 ] Confirmación de MACD:** Histograma MACD positivo y NO decreciente en las últimas 2 velas.
5. **[ +1 ] Volumen Ajustado:** Volumen de la vela de ruptura o continuación > 1.2x de la media de volumen de **esa misma franja horaria (UTC)** en los últimos 30 días.

## 4. Gestión de Riesgo y Operación

### Dimensionamiento de Posición (Position Sizing)
- **Riesgo Base:** Riesgo fijo del 1% del capital asignado a la estrategia Alpha.
- **Tamaño Nominal:** Calculado en base a la distancia entre la entrada y el Stop Loss inicial.

### Stop Loss (SL)
- **SL Inicial Fijo:** Ubicado a `Precio de Entrada - 1.5 * ATR(14)`.
- *Regla de Oro:* El SL inicial NUNCA se amplía.

### Take Profit y Trailing Stop
- **Toma de Beneficios Parcial (TP1):** Al alcanzar un beneficio de `+2 * ATR(14)` respecto a la entrada, cerrar el 50% de la posición.
- **Trailing Stop (Resto de posición):** Una vez ejecutado el TP1, activar trailing stop a la distancia de `1.5 * ATR(14)` desde el máximo alcanzado. No hay TP fijo final.

## 5. Condiciones de Invalidez y Salida de Emergencia
El agente debe forzar el cierre de la posición a mercado si ocurre alguna de estas condiciones (incluso si no ha tocado SL o TP):

1. **Divergencia Estructural:** El precio marca un nuevo máximo, pero el RSI(14) marca un máximo menor durante 3 velas 4H.
2. **Caída del Score:** El Score de Evaluación del activo cae por debajo de 3.
3. **Pérdida de Soporte Dinámico:** Cierre de vela 4H por debajo de la EMA50 con volumen creciente.
4. **Alerta Macro:** BTC sufre una caída repentina > 5% en 4H.

## 6. Setups de Alta Convicción (Prioridad del Agente)
Si múltiples activos cumplen un Score >= 5, priorizar:
- **El Retroceso Perfecto:** Tendencia alcista validada -> Retroceso a EMA50 -> Rebote con vela verde donde el Volumen de la Franja es > 2.0x la media -> Entrada al cierre.