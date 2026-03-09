# 📋 GUÍA DE TRABAJO — DÍA 1: DEFINICIÓN Y EXPLORACIÓN
## Datajam CCB | Reto 1: Seguridad Empresarial

---

## OBJETIVO DEL DÍA
Al final de hoy deben tener:
- ✅ Inventario completo de todas las bases de datos
- ✅ Nombres exactos de las variables clave en EPV y ECN
- ✅ Confirmación de qué años tienen en común EPV y ECN
- ✅ Entender si el Registro Mercantil permite cruzar tamaño/sector con las encuestas
- ✅ Primeras visualizaciones exploratorias

---

## PASO A PASO

### PASO 1 — Instalar dependencias (1 vez)
```bash
pip install pandas openpyxl xlrd matplotlib seaborn
```

### PASO 2 — Correr Script 1: Reconocimiento
```bash
python 01_reconocimiento_bases.py
```
**Qué hacer con el resultado:**
- Abre `inventario_bases.xlsx`
- Para EPV: busca los archivos con "resultado" o "datos" en el nombre (no diccionarios)
- Para ECN: igual
- Anota los nombres exactos de archivo por año
- Revisa cuántas hojas tiene cada Excel (el script las lista)

### PASO 3 — Llenar la configuración del Script 2
Abre `02_exploracion_dirigida.py` y completa:
```python
ARCHIVOS_EPV = {
    2021: "nombre_exacto_epv_2021.xlsx",
    2022: "nombre_exacto_epv_2022.xlsx",
    # etc.
}
ARCHIVOS_ECN = {
    2020: "nombre_exacto_ecn_2020.xlsx",
    # etc.
}
ARCHIVO_REGISTRO_2024 = "nombre_exacto_registro.xlsx"
```

### PASO 4 — Correr Script 2: Exploración Dirigida
```bash
python 02_exploracion_dirigida.py
```

---

## QUÉ BUSCAR EN LOS RESULTADOS

### En EPV — Variables críticas a encontrar:
| Variable | ¿Qué buscar en el nombre de columna? |
|----------|--------------------------------------|
| Victimización de empresa | "victima", "delito", "hurto", "robo empresa" |
| Percepción de seguridad | "percep", "segur", "insegur" |
| Tipo de delito sufrido | "tipo_delito", "modalidad" |
| Sector o actividad económica | "sector", "actividad", "ciiu" |
| Tamaño de empresa | "tamaño", "tamano", "empleados", "personal" |
| Localidad | "localidad", "upz", "barrio", "zona" |

### En ECN — Variables críticas a encontrar:
| Variable | ¿Qué buscar? |
|----------|--------------|
| Indicador de clima de negocios | "clima", "expectativa", "situacion" |
| Ventas / ingresos | "ventas", "ingres", "factur" |
| Acceso a crédito | "credito", "financ", "prestamo" |
| Inversión | "inversion", "activos" |
| Sector CIIU | "sector", "ciiu", "actividad" |
| Tamaño empresa | "tamaño", "empleados", "personal" |

### En Registro Mercantil:
| Variable | ¿Qué buscar? |
|----------|--------------|
| Sector CIIU | "ciiu", "actividad", "codigo_actividad" |
| Tamaño empresa | "tamaño", "activos", "empleados" |
| Localidad/dirección | "localidad", "direccion", "zona" |
| NIT o identificador | "nit", "id", "codigo" |

---

## PREGUNTAS CLAVE A RESPONDER HOY

Al terminar la exploración, deben poder responder:

1. **¿La EPV tiene módulo específico para empresas o solo para hogares/personas?**
   → Si hay módulo empresarial, es el corazón del análisis de victimización objetiva

2. **¿La ECN tiene variable de tamaño de empresa (micro/pequeña/mediana/grande)?**
   → Esta es la variable de segmentación que pidió el tutor

3. **¿La ECN tiene código CIIU o clasificación por sector?**
   → Necesaria para el análisis por sector

4. **¿Hay un identificador común entre EPV y ECN para cruzarlas?**
   → Si no lo hay, el cruce será a nivel agregado (por localidad, sector o año)

5. **¿Los datos del Registro Mercantil tienen estructura que permita cruzar con EPV/ECN?**
   → Puede servir como referencia de universo empresarial de Bogotá

---

## FUENTES DANE A CONSULTAR PARALELAMENTE

Mientras corre la exploración, alguien del equipo puede descargar:

- **EAM (Encuesta Anual Manufacturera):**
  https://www.dane.gov.co/index.php/estadisticas-por-tema/industria/encuesta-anual-manufacturera-eam

- **Encuesta de Micronegocios:**
  https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/micronegocios

- **Estadísticas de delitos (SCJ Bogotá):**
  https://scj.gov.co/es/oficina-oaiee/estadisticas-mapas
  → Descargar datos de hurto a establecimientos comerciales por localidad

---

## RESULTADO ESPERADO AL FINAL DEL DÍA

Un documento/nota compartida con el equipo que tenga:
```
EPV:
- Módulo empresarial: SÍ/NO
- Variable victimización empresa: [nombre columna]
- Variable percepción seguridad: [nombre columna]
- Variable sector: [nombre columna]
- Variable tamaño: [nombre columna]
- Años disponibles: [lista]
- Filas por año: [cifras]

ECN:
- Variable clima de negocios: [nombre columna]
- Variable ventas: [nombre columna]
- Variable crédito: [nombre columna]
- Variable tamaño empresa: [nombre columna]
- Variable sector CIIU: [nombre columna]
- Años disponibles: [lista]

CRUCE:
- Años en común EPV + ECN: [lista]
- Variable de cruce posible: [nombre o "solo agregado"]

REGISTRO MERCANTIL:
- Variables útiles encontradas: [lista]
```
