# 📐 NOTA METODOLÓGICA — CRUCE EPV + ECN
## Datajam CCB | Reto 1: Seguridad Empresarial

---

## El problema central del cruce

EPV y ECN son **encuestas independientes** — no comparten un identificador
de empresa o persona. Esto significa que **no podemos cruzarlas a nivel
de fila (individuo)**. El cruce debe hacerse a nivel **agregado**.

---

## Niveles de agregación disponibles

| Nivel | Variables de cruce | Años disponibles | Calidad |
|---|---|---|---|
| **Bogotá total** | Año | 2021–2024 | ✅ Robusto, pocos puntos |
| **Localidad** | Año + Localidad | 2021–2024 | ✅ Bueno para mapas |
| **Sector económico** | Año + Sector | 2024–2025 (EPV) / 2020–2024 (ECN) | ⚠️ Solo EPV 2024+ tiene sector |
| **Tamaño empresa** | Año + Tamaño | ECN 2022–2024 | ⚠️ EPV no tiene tamaño |

---

## Estrategia recomendada (incorpora feedback del tutor)

### Eje 1 — Análisis longitudinal (2021–2024)
- Cruce a nivel **Bogotá por año**
- Variables: tasa de victimización EPV + índice de clima ECN
- Pregunta: ¿cuando sube la victimización, baja el clima de negocios?
- Técnica: correlación de series de tiempo, regresión simple

### Eje 2 — Análisis por localidad (2021–2024)
- Cruce a nivel **Año + Localidad**
- Variables: percepción de seguridad EPV + indicadores ECN agregados por localidad
- Pregunta: ¿las localidades con peor percepción tienen peor clima?
- Técnica: correlación, mapa de calor Bogotá

### Eje 3 — Análisis por tamaño de empresa (ECN 2022–2024)
- Solo ECN, sin cruce con EPV
- Variables: F4/F5 tamaño + ventas + crédito + inversión
- Pregunta del tutor: ¿las empresas pequeñas son más sensibles que las grandes?
- Técnica: ANOVA o Kruskal-Wallis entre grupos de tamaño

### Eje 4 — Análisis por sector CIIU (ECN 2020–2024)
- Solo ECN + datos SCJ de delitos por sector
- Variables: sector_ciiu + clima de negocios
- Pregunta del tutor: ¿hay sectores más sensibles (comercio vs. industria)?
- Técnica: comparación de medias por sector, clustering

---

## Fuentes externas que fortalecen el análisis

Para compensar la falta de cruce directo EPV-ECN, se recomienda cruzar con:

1. **Estadísticas SCJ (scj.gov.co)** → hurtos a establecimientos por localidad
   - Esto da una medida OBJETIVA de incidencia por localidad
   - Se puede cruzar con percepción EPV → brecha objetivo/subjetivo

2. **EAM DANE** → producción y empleo por sector CIIU
   - Permite comparar clima ECN contra realidad sectorial del DANE

3. **Registro Mercantil CCB** → distribución de empresas por tamaño/sector/localidad
   - Sirve como denominador para calcular tasas (ej. empresas victimizadas / total empresas)

---

## Variables a construir para el informe final

| Variable | Fuente | Descripción |
|---|---|---|
| `tasa_victimizacion` | EPV P203 | % respondentes víctimas por año/localidad |
| `percepcion_seguridad` | EPV P102+P103 | Promedio escala 1-5 por año/localidad |
| `brecha_objetivo_subjetivo` | EPV + SCJ | Diferencia entre incidencia real y percepción |
| `indice_clima` | ECN P12+P21+P28 | Índice compuesto de salud empresarial |
| `sensibilidad_tamanio` | ECN F4/F5 | Diferencia de clima por tamaño empresa |
| `sensibilidad_sector` | ECN F3 | Diferencia de clima por sector CIIU |

---

## ✅ Hallazgos del cuestionario EPV (validados en Formulario final EPV 2024)

**La EPV NO tiene módulo de empresas.** Es una encuesta estrictamente ciudadana.
Las únicas preguntas sobre negocios son al cierre:
- `P500`: ¿Tiene negocio, empresa o establecimiento de comercio? (1=Sí, 2=No)
- `P501`: ¿Tiene matrícula mercantil? (1=Sí, 2=No)

**Variables de victimización comercial:**
- `P20423`: Opción 23 de P204 — Hurto a establecimientos comerciales (1=Sí)
- `P20422`: Extorsión
- `P20420`: Delitos cibernéticos

**Decisión metodológica adoptada:**
Filtrar solo encuestados con `P500=1` (propietarios de negocio) y analizar
su victimización comercial (`P20423`) y percepción de seguridad (`P1021`, `P1031`).
Esto da una muestra más pequeña pero directamente relevante para el reto.

**Posibilidad adicional:** Separar `P501=1` (formales) vs `P501=2` (informales)
para comparar si la formalidad empresarial modera el impacto de la inseguridad.

---

## ⚠️ Advertencias para el informe

1. **Muestra reducida.** Al filtrar solo propietarios (P500=1), la muestra EPV
   se reduce significativamente. Reportar n por año y localidad para transparencia.

2. **El índice de clima de negocios propio** debe justificarse vs. índices ya publicados
   (el tutor lo mencionó). Revisar si la CCB publica un índice oficial en las
   presentaciones PowerPoint de los resultados de la ECN.

3. **Causalidad vs. correlación.** El informe debe ser cuidadoso: encontrar correlación
   entre percepción y clima no implica que una cause la otra.

4. **Localidad como nivel de cruce.** Verificar que la ECN también tenga
   variable de localidad; de lo contrario el cruce solo será posible a nivel
   Bogotá por año (menos granular pero igualmente válido).
