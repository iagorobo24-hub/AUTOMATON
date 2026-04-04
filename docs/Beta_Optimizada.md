# AUTOTRADER AGENT — KNOWLEDGE BASE
# Estrategia Beta — Range Scalper v2.0

**Objetivo:** Explotar consolidaciones laterales (rangos) de baja volatilidad cuando la Estrategia Alpha está en pausa, capitalizando el rebote en zonas de liquidez bien definidas.

## 1. Filosofía
Los mercados cripto no están siempre en tendencia. Pasan la mayor parte de su tiempo buscando equilibrio en consolidación. Esta estrategia asume que el precio tiene "memoria" temporal, y que compradores y vendedores repetirán su comportamiento en niveles donde encontraron volumen antes.

**Principios del Agente:**
- **Estadística sobre Amplitud:** Acertar un 65% del tiempo con ratio R/R 1:1.5 es mejor que buscar grandes ganancias en mercados que no las ofrecen.
- **Riesgo por Invalidez:** El stop loss no significa "pérdida de dinero", significa "invalidez matemática del rango".

## 2. Filtros de Régimen y Contexto (Pre-Condiciones)
El agente valida estas condiciones antes de entrar al mercado.

### Filtro A: Entorno Macro (BTC Lateral)
- **BTC Consolidado:** BTC NO debe tener 3 o más velas de 4H consecutivas > 1.5% de cuerpo en una misma dirección con volumen creciente.
- **Volatilidad Baja:** El ATR(14) de BTC actual debe ser < Percentil 60 de los últimos 30 días.

### Filtro B: Identificación Cuantitativa del Rango
- **Duración Mínima:** Al menos 10 velas de 4H (40h) con el precio oscilando sin tendencias intradiarias sostenidas.
- **Amplitud Rentable:** La distancia porcentual entre Resistencia (R) y Soporte (S) debe ser >= 3.0%. Rangos menores se ignoran por no compensar el spread.
- **Confirmación Estructural:** Al menos 2 toques previos en la zona de Soporte (con desviación ±0.3x ATR) y 2 en la zona de Resistencia.
- **Volatilidad Local Contenida:** ATR(14) actual del activo < 2.0x su Media Móvil de ATR(20).

## 3. Sistema de Evaluación (Score Dinámico de Entrada)
Si el rango es validado, se evalúa una entrada en Soporte (Long) o Resistencia (Short).
**Condición de entrada: Score Total >= 5.**

**Puntuación para LONG en Soporte (+1 o +2 puntos):**
1. **[ +2 ] Precisión de Precio:** Precio actual dentro del ±(0.3 * ATR_14) del nivel de Soporte histórico.
2. **[ +2 ] Rechazo Mecánico:** Presencia de al menos una vela de indecisión (Doji/Martillo) donde `Mecha Inferior > 2x Cuerpo de la vela`.
3. **[ +1 ] Sobrevendida Relativa:** RSI (14) < Percentil 30 de las últimas 20 velas de este par (no valor estático <40, sino relativo).
4. **[ +1 ] Agotamiento de Venta:** Volumen de la vela bajista previa < 80% del Volumen Medio Ajustado a su franja horaria.
5. **[ +1 ] Momentum MACD:** Histograma MACD negativo pero en barras progresivamente menos profundas.

*(Las condiciones para SHORT son inversas simétricamente).*

## 4. Gestión de Riesgo y Operación

### Dimensionamiento de Posición (Position Sizing)
- **Riesgo Base:** 0.5% a 1.0% del capital asignado a la estrategia Beta.
- **Tamaño Nominal:** Reducido por la volatilidad. Fórmula: `Tamaño Base * (ATR_30d / ATR_14 actual)`. Nunca mayor al 8%.

### Stop Loss (SL) y Take Profit (TP)
- **SL Rígido (Invalidación):** Ubicado un 1.0% o `1 * ATR(14)` fuera de la zona de soporte/resistencia. Se ejecuta de inmediato ante un cierre de vela de 4H fuera del rango. NUNCA se ajusta a favor ni en contra de la operación.
- **Take Profit (TP):** Cierre del 100% de la posición al alcanzar el 75-80% de la amplitud del rango hacia el extremo opuesto.

## 5. Condiciones de Invalidez y Salida de Emergencia
El agente debe abortar o no iniciar operaciones en este activo si:

1. **Breakout (Ruptura):** Se produce un cierre de vela de 4H fuera del rango con volumen > Media + 1 DevStd. El rango está muerto.
2. **Anomalía de Volumen:** El volumen general del activo (sin importar la franja) cae al mínimo de los últimos 7 días. Se asume falta de liquidez y alto riesgo de *whipsaw* manipulado.
3. **Múltiples Toques ("El Tercer Toque"):** Si el precio llega por 3ª vez consecutiva al soporte/resistencia SIN haber alcanzado la mitad del rango en el rebote previo, la probabilidad de ruptura es del 60%. El agente cancela entradas Beta y alerta a la Estrategia Gamma.

## 6. Setups de Alta Convicción (Prioridad del Agente)
- **El Falso Breakout (Liquidity Grab):** Ruptura del nivel durante la vela de 4H (mecha larga) pero el cierre finaliza dentro de la banda de S/R histórica. Indica barrido de stops. Entrada inmediata al cierre de esa vela con SL ajustado justo debajo de esa mecha específica.