# AUTOTRADER AGENT — KNOWLEDGE BASE
# Estrategia Gamma — Breakout Hunter v2.0

**Objetivo:** Capturar movimientos direccionales violentos (expansión) que ocurren inmediatamente después de períodos prolongados de compresión de volatilidad (acumulación/distribución).

## 1. Filosofía
Un breakout validado NO es un movimiento al azar; es la resolución de una compresión de energía acumulada en el mercado. Esta estrategia asume una tasa de acierto estadísticamente baja (35%-42%). El beneficio neto a largo plazo proviene exclusivamente de gestionar las pérdidas mecánicamente al primer signo de falsa ruptura (fakeout) y cabalgar las rupturas verdaderas con trailing stops agresivos.

**Principios del Agente:**
- **Filtro de Liquidez Extrema:** Los breakouts en pares con poca liquidez son casi siempre trampas de manipulación.
- **Validación Matemática, No Discrecional:** Un breakout no es "una vela que parece grande", es una alteración cuantitativa del flujo estadístico.

## 2. Filtros de Régimen y Contexto (Pre-Condiciones)
El agente abortará la monitorización si estas condiciones no se cumplen rígidamente.

### Filtro A: Liquidez y Manipulación
- **Volumen Real Requerido:** Media móvil de volumen diario a 7 días > 15,000,000 USD.
- **Ratio Anti-Manipulación:** `(Market Cap) / (Avg Daily Volume)` debe ser menor a 50 y mayor a 5. (Evita monedas *zombies* o *pump-and-dumps* coordinados).
- **Spread:** El spread bid/ask actual debe ser < 0.15% en el libro de órdenes.

### Filtro B: Entorno Macro BTC (Tendencia o Nada)
- **Alineación Obligatoria:** BTC debe tener `EMA20 > EMA50` en 4H. Si BTC no está en fase de crecimiento de corto plazo, se prohíben operaciones Gamma de ruptura alcista.

### Filtro C: Definición de Compresión (Energía Potencial)
- **Cálculo de Contracción ATR:** `ATR(10) / ATR(50) < 0.55`.
- **Duración:** Esta condición debe mantenerse durante al menos 8 velas 4H (32h continuas).
- **Bollinger Band Width (BBW):** El BBW(20,2) actual debe encontrarse en el percentil 20 inferior de sus últimos 100 periodos.

## 3. Sistema de Evaluación de Ruptura (Score de Entrada)
Ocurrido el Breakout (cierre de vela sobre la resistencia del rango de compresión), se evalúa la entrada real.
**Condición de entrada: Score Total >= 7.**

**Puntuación (+1 o +2 puntos):**
1. **[ +2 ] Rotura Histórica Reciente:** Cierre por encima del precio máximo de las últimas 20 velas 4H.
2. **[ +2 ] Anomalía de Volumen:** Volumen de la vela de ruptura > 2.0x la media de su grupo horario ajustado.
3. **[ +1 ] Expansión Volatilidad Creciente:** El ATR(14) de esta vela de rotura es > ATR de las 5 velas previas combinadas.
4. **[ +1 ] Dominancia Intravela:** `(Cuerpo de vela / Longitud total incluyendo mechas) > 0.6` (Asegura cierre cerca del máximo).
5. **[ +2 ] Compresión Previa Validada:** Condición del Filtro C completamente cumplida.

## 4. Gestión de Riesgo y Operación

### Ejecución de Entrada (Limit y Timeout)
- **Orden Mecánica:** Entrada via Limit Order al precio `Cierre de Breakout * 0.998` (buscando micro-pullback del 0.2%).
- **Timeout Activo:** Si la orden no se llena en 45 minutos dentro de la nueva vela 4H, cancelar inmediatamente.

### Stop Loss (SL)
- **SL de Cancelación (Hard Stop):** Si el precio vuelve al rango previo (`< Precio de Breakout - 1.5%`), forzar cierre a mercado. Este es el *Fail-Safe*.

### Take Profit y Trailing Stop
- **Asimetría Requerida:** La siguiente zona lógica de resistencia histórica debe estar a un mínimo del 8-10% del precio actual de ruptura. De lo contrario, no operar.
- **Cierre por Tiempo (Time-based Exit):** Si tras 72 horas (18 velas 4H) la posición no ha generado al menos `+2.0 * ATR` en beneficio, cerrar el trade 100%. Elimina las posiciones "zombies".
- **Trailing Stop:** A partir de `+2.0 * ATR(14)`, trailing stop dinámico a una distancia de `1.5 * ATR`.

## 5. Setups de Alta Convicción (Prioridad del Agente)
- **El Retesteo Limpio (Pullback Post-Breakout):** Si el agente no entró en la vela inicial, puede entrar en el re-testeo de la línea rota si y solo si: (a) El precio no baja más del 38.2% de Fibonacci del impulso de la ruptura inicial, (b) El volumen del retroceso es < 50% del volumen de la ruptura, y (c) Ocurre en un margen menor a 3 velas tras el breakout.