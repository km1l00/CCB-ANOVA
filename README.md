# CCB-ANOVA Project

Este proyecto está basado en el documento `00_guia-dia1.md` del Datajam CCB para el Reto 1: Seguridad Empresarial.

## Estructura del proyecto

- `data/raw/`: Colocar aquí todas las bases de datos originales en Excel o CSV (EPV, ECN, Registro Mercantil).
- `data/processed/`: Archivos procesados y resultados de inventarios.
- `docs/`: Documentación importante, como el objetivo del proyecto `00_guia_dia1.md` originario, notas del equipo y reportes de base.
- `notebooks/`: Cuadernos de Jupyter (Jupyter Notebook) para exploración de datos profunda (EDA) y gráficos (matplotlib, seaborn).
- `scripts/`: Scripts automatizados de Python diseñados para correr rápido.
- `src/`: Código fuente principal, tales como módulos custom para limpieza, unificación de formatos y transformaciones de bases de datos.

## Guía de Inicip Rápido (Basado en el Día 1)

1. **Instalar Dependencias**
   Instala todas las librerías base necesarias para el proyecto:
   ```bash
   pip install -r requirements.txt
   ```

2. **Almacenar Datos (Manual)**
   Mueve o descarga las bases proporcionadas (Encuesta de Percepción de Victimización EPV, Encuesta de Clima de Negocios ECN y el Registro) y asegúrate de colocarlas en la carpeta `data/raw/`.

3. **Ejecutar Reconocimiento de Bases**
   Ejecuta el script para generar un inventario con el número de hojas y nombre de todas tus bases de datos:
   ```bash
   cd scripts
   python 01_reconocimiento_bases.py
   ```
   *Esto generará automáticamente `data/processed/inventario_bases.xlsx`.*

4. **Configuración Exploración Dirigida**
   Usando el Excel generado del punto anterior, abre `scripts/02_exploracion_dirigida.py` y completa las variables de configuración en la parte superior del archivo (`ARCHIVOS_EPV`, `ARCHIVOS_ECN` y `ARCHIVO_REGISTRO`) con los nombres exactos de los archivos.

5. **Ejecutar Exploración Dirigida**
   Corre el segundo script, el cual te mostrará exactamente en qué columnas del Excel o CSV están los identificadores clave, encuestas, victimización y más métricas de tu reto.
   ```bash
   python 02_exploracion_dirigida.py
   ```

6. **Consolidar Documentación**
   Ve a la carpeta `docs/` o crea un archivo de equipo, documentando las respuestas y resultados del módulo y llenando las "PREGUNTAS CLAVE A RESPONDER HOY" de la Guía 1.
