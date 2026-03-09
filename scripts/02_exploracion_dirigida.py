import pandas as pd
from pathlib import Path

# =======================================================
# CONFIGURACIÓN (Llenar basándose en el inventario_bases.xlsx)
# =======================================================

ARCHIVOS_EPV = {
    2021: "EPV_Encuesta de Percepción y Victimización/2021/Base2021.xlsx",
    2022: "EPV_Encuesta de Percepción y Victimización/2022/Base2022.xlsx",
    2023: "EPV_Encuesta de Percepción y Victimización/2023/Base2023.xlsx",
    2024: "EPV_Encuesta de Percepción y Victimización/2024/Base EPV 2024 anonimizada.xlsx",
    2025: "EPV_Encuesta de Percepción y Victimización/2025/Base Encuesta de Percepción Victimización 2025 anonimizada.xlsx"
}

ARCHIVOS_ECN = {
    2020: "ECN_Encuesta Clima de los Negocios/2020/Base_2020.xlsx",
    2021: "ECN_Encuesta Clima de los Negocios/2021/Base_2021.xlsx",
    2022: "ECN_Encuesta Clima de los Negocios/2022/Base_2022.xlsx",
    2023: "ECN_Encuesta Clima de los Negocios/2023/Base CLIMA DE NEGOCIOS 2023 anonimizada.xlsx",
    2024: "ECN_Encuesta Clima de los Negocios/2024/Encuesta Clima de negocios 2024 final anonimizada.xlsx"
}

ARCHIVO_REGISTRO = "Base Registro Mercantil 2024/Base total activas 2024 - anonimizada.xlsx"

# =======================================================

def explorar_archivo(ruta_archivo, palabras_clave, tipo):
    if not ruta_archivo.exists() or ruta_archivo.is_dir():
        print(f"⚠️  [OMITIDO] Archivo no encontrado o no configurado: {ruta_archivo.name}")
        return

    print(f"\n🔍 Explorando {tipo} - {ruta_archivo.name}:")
    try:
        if ruta_archivo.suffix in ['.xlsx', '.xls']:
            xls = pd.ExcelFile(ruta_archivo)
            hojas = xls.sheet_names
            diccionarios_omitir = ['diccionario', 'label', 'datamap', 'opciones']
            
            encontrado_general = False
            for hoja in hojas:
                if any(omit in hoja.lower() for omit in diccionarios_omitir):
                    continue
                df = xls.parse(hoja, nrows=5)
                columnas = df.columns
                
                encontrado_hoja = False
                for key, aliases in palabras_clave.items():
                    # Check if exact match or partial match
                    cols_match = []
                    for c in columnas:
                        c_str = str(c).lower().strip()
                        if any((a.lower() == c_str) or (len(a)>2 and a.lower() in c_str) for a in aliases):
                            cols_match.append(str(c))
                            
                    if cols_match:
                        if not encontrado_hoja:
                            print(f"  📂 En hoja '{hoja}':")
                            encontrado_hoja = True
                        print(f"    ✅ {key}: {', '.join(cols_match)}")
                        encontrado_general = True
                        
            if not encontrado_general:
                print("  ❌ No se encontraron variables clave en ninguna hoja analizada.")
                
        else:
            df = pd.read_csv(ruta_archivo, nrows=5)
            columnas = df.columns
            encontrado = False
            
            for key, aliases in palabras_clave.items():
                cols_match = []
                for c in columnas:
                    c_str = str(c).lower().strip()
                    if any((a.lower() == c_str) or (len(a)>2 and a.lower() in c_str) for a in aliases):
                        cols_match.append(str(c))
                if cols_match:
                    print(f"  ✅ {key}: {', '.join(cols_match)}")
                    encontrado = True
                    
            if not encontrado:
                print("  ❌ No se encontraron variables clave en las primeras filas/columnas.")
                
    except Exception as e:
        print(f"  ❌ Error leyendo archivo {ruta_archivo.name}: {e}")

def main():
    print("=========================================")
    print(" INICIANDO EXPLORACIÓN DIRIGIDA CCB-ANOVA")
    print("=========================================")
    
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw"
    
    # DICCIONARIOS DE BÚSQUEDA (Basado en la Guía Día 1)
    kw_epv = {
        "Victimización de empresa": ["victima", "delito", "hurto", "robo", "empresa"],
        "Percepción de seguridad": ["percep", "segur", "insegur"],
        "Tipo de delito sufrido": ["tipo_delito", "modalidad"],
        "Sector o actividad económica": ["sector", "actividad", "ciiu"],
        "Tamaño de empresa": ["tamaño", "tamano", "empleados", "personal"],
        "Localidad": ["localidad", "upz", "barrio", "zona"]
    }
    
    kw_ecn = {
        "Indicador de clima de negocios": ["clima", "expectativa", "situacion"],
        "Ventas / ingresos": ["ventas", "ingres", "factur", "P5", "P12", "P13"],
        "Acceso a crédito": ["credito", "financ", "prestamo", "P21", "P22"],
        "Inversión": ["inversion", "activos", "P28", "P30"],
        "Sector CIIU": ["sector", "ciiu", "actividad", "F3"],
        "Tamaño empresa": ["tamaño", "empleados", "personal", "F4", "F5"]
    }
    
    kw_registro = {
        "Sector CIIU": ["ciiu", "actividad", "codigo_actividad"],
        "Tamaño empresa": ["tamaño", "activos", "empleados"],
        "Localidad/dirección": ["localidad", "direccion", "zona"],
        "NIT o identificador": ["nit", "id", "codigo"]
    }

    # Exploración EPV
    print("\n--- PASO 1: Encuesta de Percepción de Victimización (EPV) ---")
    if not ARCHIVOS_EPV:
        print("💡 No se han configurado archivos EPV. Actualiza el diccionario ARCHIVOS_EPV en el script.")
    for anio, name in ARCHIVOS_EPV.items():
        explorar_archivo(raw_dir / name, kw_epv, f"EPV {anio}")

    # Exploración ECN
    print("\n--- PASO 2: Encuesta de Clima de Negocios (ECN) ---")
    if not ARCHIVOS_ECN:
        print("💡 No se han configurado archivos ECN. Actualiza el diccionario ARCHIVOS_ECN en el script.")
    for anio, name in ARCHIVOS_ECN.items():
        explorar_archivo(raw_dir / name, kw_ecn, f"ECN {anio}")

    # Exploración Registro
    print("\n--- PASO 3: Registro Mercantil ---")
    if not ARCHIVO_REGISTRO:
        print("💡 No se ha configurado el archivo de Registro. Actualiza la variable ARCHIVO_REGISTRO en el script.")
    else:
        explorar_archivo(raw_dir / ARCHIVO_REGISTRO, kw_registro, "Registro Mercantil")

    print("\n=========================================")
    print("             EXPLORACIÓN FINALIZADA      ")
    print("=========================================")

if __name__ == "__main__":
    main()
