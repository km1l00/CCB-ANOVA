"""
SCRIPT 3 (v2): CONSTRUCCIÓN DEL DATASET ANALÍTICO UNIFICADO
Datajam CCB - Reto 1: Seguridad Empresarial
-------------------------------------------------
Diseño metodológico validado:

  UNIDAD DE ANÁLISIS EPV: Ciudadanos propietarios de negocio (P500=Sí)
  UNIDAD DE ANÁLISIS ECN: Empresas formales encuestadas directamente
  NIVEL DE CRUCE: Agregado por Año + Localidad

  Flujo EPV por encuestado:
    1. Filtrar P500 == 1 (tiene negocio)
    2. Subcategoría P501: 1=formal (con matrícula), 2=informal
    3. Victimización comercial: P20423 == 1 (hurto a establecimiento)
    4. Delitos complementarios: P20422 (extorsión), P20420 (cibernético)
    5. Percepción: P1021 (barrio), P1031 (Bogotá), escala 1-5

  Flujo ECN por empresa:
    - Sector CIIU: F3
    - Tamaño: F4/F5
    - Clima de negocios: P12 (ventas), P21/P22 (crédito), P28/P30 (inversión)

  Cruce final: EPV agregado por localidad + ECN agregado por localidad
  → Pregunta central: ¿localidades con mayor victimización/peor percepción
    tienen peor clima de negocios?

INSTRUCCIONES:
  1. Ajusta BASE_PATH
  2. Completa los nombres de archivo en ARCHIVOS_EPV y ARCHIVOS_ECN
  3. Ejecuta. Genera 7 archivos CSV en OUTPUT_DIR.
"""

import os
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURACIÓN
# ============================================================
BASE_PATH = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "datasets_analiticos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RUTA_EPV = BASE_PATH / "EPV_Encuesta de Percepción y Victimización"
RUTA_ECN = BASE_PATH / "ECN_Encuesta Clima de los Negocios"

# Completa con los nombres exactos de archivo (del Script 1)
ARCHIVOS_EPV = {
    2021: {"carpeta": "2021", "archivo": "Base2021.xlsx"},
    2022: {"carpeta": "2022", "archivo": "Base2022.xlsx"},
    2023: {"carpeta": "2023", "archivo": "Base2023.xlsx"},
    2024: {"carpeta": "2024", "archivo": "Base EPV 2024 anonimizada.xlsx"},
    2025: {"carpeta": "2025", "archivo": "Base Encuesta de Percepción Victimización 2025 anonimizada.xlsx"},
}

ARCHIVOS_ECN = {
    2020: {"carpeta": "2020", "archivo": "Base_2020.xlsx"},
    2021: {"carpeta": "2021", "archivo": "Base_2021.xlsx"},
    2022: {"carpeta": "2022", "archivo": "Base_2022.xlsx"},
    2023: {"carpeta": "2023", "archivo": "Base CLIMA DE NEGOCIOS 2023 anonimizada.xlsx"},
    2024: {"carpeta": "2024", "archivo": "Encuesta Clima de negocios 2024 final anonimizada.xlsx"},
}

# ============================================================
# MAPEO DE VARIABLES EPV
# ============================================================
EPV_VAR_MAP = {

    # FILTRO PRINCIPAL — ¿Tiene negocio? (P500: 1=Sí, 2=No)
    "tiene_negocio": {
        2021: ["P500", "p500"],
        2022: ["P500"],
        2023: ["P500"],
        2024: ["P500"],
        2025: ["P500"],
    },

    # FILTRO SECUNDARIO — ¿Tiene matrícula mercantil? (P501: 1=Sí, 2=No)
    "negocio_formal": {
        2021: ["P501", "p501"],
        2022: ["P501"],
        2023: ["P501"],
        2024: ["P501"],
        2025: ["P501"],
    },

    # VICTIMIZACIÓN GENERAL (P203: 1=Sí, 2=No)
    "victima_general": {
        2021: ["P203", "p203"],
        2022: ["P203"],
        2023: ["P203"],
        2024: ["P203"],
        2025: ["P203"],
    },

    # VICTIMIZACIÓN COMERCIAL — Opción 23 de P204
    # Hurto a establecimientos comerciales (1=Marcado, 0/NaN=No)
    "victima_hurto_comercio": {
        2021: ["P20423", "P204_23", "p20423"],
        2022: ["P20423", "P204_23"],
        2023: ["P20423", "P204_23"],
        2024: ["P20423"],
        2025: ["P20423"],
    },

    # EXTORSIÓN — Opción 22 de P204
    "victima_extorsion": {
        2021: ["P20422", "P204_22", "p20422"],
        2022: ["P20422", "P204_22"],
        2023: ["P20422", "P204_22"],
        2024: ["P20422"],
        2025: ["P20422"],
    },

    # DELITOS CIBERNÉTICOS — Opción 20 de P204
    "victima_cibernetico": {
        2021: ["P20420", "P2041_A", "P204_20"],
        2022: ["P20420", "P2041_A"],
        2023: ["P20420", "P2041_A"],
        2024: ["P20420"],
        2025: ["P20420"],
    },

    # PERCEPCIÓN BARRIO (P102.1 / P1021: escala 1-5)
    "percepcion_barrio": {
        2021: ["P102",  "P1021", "P102_1", "p102"],
        2022: ["P102",  "P1021", "P102_1"],
        2023: ["P102",  "P1021", "P102_1"],
        2024: ["P1021", "P102_1", "P102"],
        2025: ["P1021", "P102_1", "P102"],
    },

    # PERCEPCIÓN BOGOTÁ (P103.1 / P1031: escala 1-5)
    "percepcion_bogota": {
        2021: ["P103",  "P1031", "P103_1", "p103"],
        2022: ["P103",  "P1031", "P103_1"],
        2023: ["P103",  "P1031", "P103_1"],
        2024: ["P1031", "P103_1", "P103"],
        2025: ["P1031", "P103_1", "P103"],
    },

    # LOCALIDAD
    "localidad": {
        2021: ["LOCALIDAD", "localidad"],
        2022: ["LOCALIDAD"],
        2023: ["NOMBRE_LOCALIDAD", "LOCALIDAD"],
        2024: ["LOCALIDAD"],
        2025: ["Localidad", "LOCALIDAD"],
    },

    # SECTOR ECONÓMICO (solo disponible en EPV 2024-2025)
    "sector_epv": {
        2024: ["COD_DANE_SECTOR", "SECTOR"],
        2025: ["Sector", "SECTOR"],
    },
}

# ============================================================
# MAPEO DE VARIABLES ECN
# ============================================================
ECN_VAR_MAP = {

    "sector_ciiu": {
        2020: ["sector",    "SECTOR",    "ciiu"],
        2021: ["COD_CIIU",  "SECTOR",    "F3",   "sector"],
        2022: ["F3"],
        2023: ["F3",        "CIIU"],
        2024: ["F3"],
    },

    # Tamaño empresa (disponible desde 2022)
    "tamanio_empresa": {
        2022: ["F4"],
        2023: ["F4", "F5"],
        2024: ["F4", "F5"],
    },

    "num_empleados": {
        2020: ["p_f4",  "F4",  "empleados"],
        2021: ["F4",    "empleados"],
        2022: ["F5"],
        2023: ["F5"],
        2024: ["F5"],
    },

    "localidad": {
        2020: ["localidad", "LOCALIDAD", "zona"],
        2021: ["localidad", "LOCALIDAD"],
        2022: ["localidad", "LOCALIDAD"],
        2023: ["Jurisdicción", "jurisdiccion", "localidad", "LOCALIDAD"],
        2024: ["REGION", "F3", "localidad", "LOCALIDAD"],
    },

    # Ventas: 1=Aumentó, 2=Igual, 3=Disminuyó
    "ventas_comportamiento": {
        2020: ["p_p12_1",  "p_p12_2", "p_p12"],
        2021: ["P12_1",    "P12_2",   "P12"],
        2022: ["P12",      "P5"],
        2023: ["P12",      "P5"],
        2024: ["P12"],
    },

    "ventas_expectativa": {
        2020: ["p_p13_1", "p_p13"],
        2021: ["P13_1",   "P13"],
        2022: ["P13"],
        2023: ["P13"],
        2024: ["P13"],
    },

    "credito_solicito": {
        2020: ["p_p21_1", "p_p21"],
        2021: ["P21_1",   "P21"],
        2022: ["P21"],
        2023: ["P21"],
        2024: ["P21"],
    },

    "credito_obtuvo": {
        2020: ["p_p22_1", "p_p22"],
        2021: ["P22_1",   "P22"],
        2022: ["P22"],
        2023: ["P22"],
        2024: ["P22"],
    },

    "inversion_realizo": {
        2020: ["p_p28_1", "p_p28"],
        2021: ["P28"],
        2022: ["P28"],
        2023: ["P28"],
        2024: ["P28"],
    },

    "inversion_expectativa": {
        2020: ["p_p30_p30", "p_p30"],
        2021: ["P30"],
        2022: ["P30"],
        2023: ["P30"],
        2024: ["P30"],
    },
}

# ============================================================
# FUNCIONES BASE
# ============================================================

def cargar_base(ruta, hoja=0):
    ext = Path(ruta).suffix.lower()
    try:
        if ext in [".xlsx", ".xls"]:
            xl = pd.ExcelFile(ruta)
            target_sheet = hoja
            if "Sin Etiquetas" in xl.sheet_names:
                target_sheet = "Sin Etiquetas"
            elif "Con Etiquetas" in xl.sheet_names:
                target_sheet = "Con Etiquetas"
            elif "Hoja1" in xl.sheet_names:
                target_sheet = "Hoja1"
            elif len(xl.sheet_names) > 1 and xl.sheet_names[0] == "RES":
                target_sheet = xl.sheet_names[1]
                
            df = xl.parse(sheet_name=target_sheet)
        elif ext == ".csv":
            df = pd.read_csv(ruta, encoding="latin-1", sep=None, engine="python")
        elif ext == ".txt":
            df = pd.read_csv(ruta, encoding="latin-1", sep="\t")
        else:
            return None
        return df
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None


def resolver_columna(df, candidatos):
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidatos:
        if cand in df.columns:
            return cand
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
        matches = [c for c in df.columns
                   if c.upper() == cand.upper()
                   or c.upper().startswith(cand.upper() + "_")]
        if matches:
            return matches[0]
    return None


def estandarizar_df(df, año, var_map, nombre):
    out = pd.DataFrame(index=df.index)
    out["año"] = año
    log = []
    for var, mapa in var_map.items():
        if año not in mapa:
            out[var] = np.nan
            continue
        col = resolver_columna(df, mapa[año])
        if col:
            out[var] = df[col].values
            log.append(f"    ✅ {var:35s} ← {col}")
        else:
            out[var] = np.nan
            log.append(f"    ⚠️  {var:35s} ← NO ENCONTRADA {mapa[año]}")
    print(f"\n  [{nombre} {año}] Mapeo:")
    for l in log:
        print(l)
    return out


# ============================================================
# TRANSFORMACIONES EPV
# ============================================================

def transformar_epv(df, año):

    # 1. Propietario de negocio (P500: 1=Sí, 2=No)
    if "tiene_negocio" in df.columns:
        df["es_propietario"] = df["tiene_negocio"].map(
            lambda x: 1 if str(x).strip() in ["1", "1.0", "Sí", "Si", "SI"]
            else (0 if str(x).strip() in ["2", "2.0", "No", "NO"] else np.nan)
        )
    else:
        df["es_propietario"] = np.nan

    # 2. Negocio formal (P501: 1=Sí, 2=No)
    if "negocio_formal" in df.columns:
        df["negocio_con_matricula"] = df["negocio_formal"].map(
            lambda x: 1 if str(x).strip() in ["1", "1.0", "Sí", "Si", "SI"]
            else (0 if str(x).strip() in ["2", "2.0", "No", "NO"] else np.nan)
        )
    else:
        df["negocio_con_matricula"] = np.nan

    # 3. Victimización general (P203: 1=Sí, 2=No)
    if "victima_general" in df.columns:
        df["victima_general_bin"] = df["victima_general"].map(
            lambda x: 1 if str(x).strip() in ["1", "1.0", "Sí", "Si", "SI"]
            else (0 if str(x).strip() in ["2", "2.0", "No", "NO"] else np.nan)
        )

    # 4. Victimización comercial (P20423: 1=Marcado, 0/NaN=No marcado)
    if "victima_hurto_comercio" in df.columns:
        df["victima_comercio_bin"] = pd.to_numeric(
            df["victima_hurto_comercio"], errors="coerce"
        ).apply(lambda x: 1 if x == 1 else (0 if x == 0 else np.nan))

    # 5. Delitos complementarios
    for var, nueva in [("victima_extorsion",  "extorsion_bin"),
                       ("victima_cibernetico", "cibernetico_bin")]:
        if var in df.columns:
            df[nueva] = pd.to_numeric(df[var], errors="coerce").apply(
                lambda x: 1 if x == 1 else (0 if x == 0 else np.nan)
            )

    # Si tiene P203 respondida (está en la encuesta) pero P20423 es NaN → es un 0 real
    tiene_p203 = df["victima_general"].notna() | df["victima_general_bin"].notna()
    if "victima_comercio_bin" in df.columns:
        df.loc[tiene_p203 & df["victima_comercio_bin"].isna(), "victima_comercio_bin"] = 0
    if "extorsion_bin" in df.columns:
        df.loc[tiene_p203 & df["extorsion_bin"].isna(), "extorsion_bin"] = 0
    if "cibernetico_bin" in df.columns:
        df.loc[tiene_p203 & df["cibernetico_bin"].isna(), "cibernetico_bin"] = 0

    # 6. Percepción de seguridad (escala 1-5, validar rango)
    for var in ["percepcion_barrio", "percepcion_bogota"]:
        if var in df.columns:
            df[var] = pd.to_numeric(df[var], errors="coerce")
            df.loc[~df[var].between(1, 5), var] = np.nan

    cols_p = [c for c in ["percepcion_barrio", "percepcion_bogota"]
              if c in df.columns and df[c].notna().any()]
    if cols_p:
        df["percepcion_promedio"] = df[cols_p].mean(axis=1)
        # Invertir: 5=muy inseguro (facilita correlación con victimización)
        df["inseguridad_percibida"] = 6 - df["percepcion_promedio"]

    if all(c in df.columns for c in ["percepcion_barrio", "percepcion_bogota"]):
        df["brecha_percepcion"] = df["percepcion_barrio"] - df["percepcion_bogota"]

    return df


# ============================================================
# TRANSFORMACIONES ECN
# ============================================================

def transformar_ecn(df):

    # Tamaño empresa → categoría estandarizada
    if "tamanio_empresa" in df.columns:
        mapa = {"1": "Microempresa", "micro": "Microempresa",
                "2": "Pequeña",      "peque": "Pequeña",
                "3": "Mediana",      "media": "Mediana",
                "4": "Grande",       "grand": "Grande"}
        df["tamanio_cat"] = df["tamanio_empresa"].astype(str).str.strip().apply(
            lambda x: next((v for k, v in mapa.items()
                            if k.lower() in x.lower()), np.nan)
        )

    # Ventas: numérico, etiqueta y flag positivo
    if "ventas_comportamiento" in df.columns:
        df["ventas_num"] = pd.to_numeric(df["ventas_comportamiento"], errors="coerce")
        df["ventas_cat"] = df["ventas_num"].map({1:"Aumentó", 2:"Igual", 3:"Disminuyó"})
        df["ventas_positivo"] = (df["ventas_num"] == 1).astype(float)
        df.loc[df["ventas_num"].isna(), "ventas_positivo"] = np.nan

    # Crédito obtenido
    if "credito_obtuvo" in df.columns:
        df["credito_num"] = pd.to_numeric(df["credito_obtuvo"], errors="coerce")
        df["credito_positivo"] = (df["credito_num"] == 1).astype(float)
        df.loc[df["credito_num"].isna(), "credito_positivo"] = np.nan

    # Inversión realizada
    if "inversion_realizo" in df.columns:
        df["inversion_num"] = pd.to_numeric(df["inversion_realizo"], errors="coerce")
        df["inversion_positivo"] = (df["inversion_num"] == 1).astype(float)
        df.loc[df["inversion_num"].isna(), "inversion_positivo"] = np.nan

    # Índice de clima compuesto
    cols_clima = [c for c in ["ventas_positivo", "credito_positivo", "inversion_positivo"]
                  if c in df.columns]
    if cols_clima:
        # User requested to calculate without inversion just in case
        cols_clima_sin_inv = [c for c in ["ventas_positivo", "credito_positivo"] if c in df.columns]
        if cols_clima_sin_inv:
            df["indice_clima_sin_inversion"] = df[cols_clima_sin_inv].mean(axis=1)
        
        # Use only these for the final index to have full coverage
        if "indice_clima_sin_inversion" in df.columns:
            df["indice_clima"] = df["indice_clima_sin_inversion"]
        else:
            df["indice_clima"] = df[cols_clima].mean(axis=1)

    return df


# ============================================================
# CONSTRUCCIÓN DE PANELES
# ============================================================

print("\n" + " CONSTRUYENDO PANEL EPV (propietarios de negocio) ".center(65, "="))

dfs_epv = []
for año, cfg in ARCHIVOS_EPV.items():
    if not cfg["archivo"]:
        continue
    ruta = os.path.join(RUTA_EPV, cfg["carpeta"], cfg["archivo"])
    if not os.path.exists(ruta):
        ruta = os.path.join(RUTA_EPV, cfg["archivo"])
    print(f"\n{'─'*65}\n  EPV {año} — {cfg['archivo']}")
    df_raw = cargar_base(ruta)
    if df_raw is None:
        continue
    print(f"  Total encuestados: {len(df_raw):,}")
    df_std = estandarizar_df(df_raw, año, EPV_VAR_MAP, "EPV")
    df_std = transformar_epv(df_std, año)
    if "es_propietario" in df_std.columns:
        n = int(df_std["es_propietario"].sum())
        pct = n / len(df_std) * 100
        print(f"\n  Propietarios de negocio (P500=Sí): {n:,} ({pct:.1f}%)")
        if "negocio_con_matricula" in df_std.columns:
            nf = int(df_std.loc[df_std["es_propietario"]==1, "negocio_con_matricula"].sum())
            print(f"  Con matrícula mercantil (P501=Sí):  {nf:,}")
        if "victima_comercio_bin" in df_std.columns:
            nv = int(df_std.loc[df_std["es_propietario"]==1, "victima_comercio_bin"].sum())
            print(f"  Víctimas hurto a comercio (P20423): {nv:,}")
    dfs_epv.append(df_std)

epv_panel = pd.concat(dfs_epv, ignore_index=True) if dfs_epv else None

print("\n\n" + " CONSTRUYENDO PANEL ECN ".center(65, "="))

dfs_ecn = []
for año, cfg in ARCHIVOS_ECN.items():
    if not cfg["archivo"]:
        continue
    ruta = os.path.join(RUTA_ECN, cfg["carpeta"], cfg["archivo"])
    if not os.path.exists(ruta):
        ruta = os.path.join(RUTA_ECN, cfg["archivo"])
    print(f"\n{'─'*65}\n  ECN {año} — {cfg['archivo']}")
    df_raw = cargar_base(ruta)
    if df_raw is None:
        continue
    print(f"  Total empresas: {len(df_raw):,}")
    df_std = estandarizar_df(df_raw, año, ECN_VAR_MAP, "ECN")
    df_std = transformar_ecn(df_std)
    dfs_ecn.append(df_std)

ecn_panel = pd.concat(dfs_ecn, ignore_index=True) if dfs_ecn else None

# ============================================================
# GUARDAR PANELES BASE
# ============================================================

if epv_panel is not None:
    epv_panel.to_csv(os.path.join(OUTPUT_DIR, "epv_panel.csv"),
                     index=False, encoding="utf-8-sig")
    print(f"\n✅ epv_panel.csv  →  {epv_panel.shape[0]:,} filas")

if ecn_panel is not None:
    ecn_panel.to_csv(os.path.join(OUTPUT_DIR, "ecn_panel.csv"),
                     index=False, encoding="utf-8-sig")
    print(f"✅ ecn_panel.csv  →  {ecn_panel.shape[0]:,} filas")

# ============================================================
# AGREGACIÓN EPV — solo propietarios, por Año + Localidad
# ============================================================

agg_epv = None
if epv_panel is not None and "localidad" in epv_panel.columns:
    epv_prop = epv_panel[epv_panel["es_propietario"] == 1].copy()
    print(f"\n  Propietarios totales en panel: {len(epv_prop):,}")
    agg_epv = epv_prop.groupby(["año", "localidad"], as_index=False).agg(
        n_propietarios        =("es_propietario",        "sum"),
        n_formales            =("negocio_con_matricula", "sum"),
        tasa_victima_general  =("victima_general_bin",   "mean"),
        tasa_victima_comercio =("victima_comercio_bin",  "mean"),
        tasa_extorsion        =("extorsion_bin",         "mean"),
        percepcion_barrio_prom=("percepcion_barrio",     "mean"),
        inseguridad_percibida =("inseguridad_percibida", "mean"),
        brecha_percepcion     =("brecha_percepcion",     "mean"),
    ).round(4)
    agg_epv.to_csv(os.path.join(OUTPUT_DIR, "epv_agg_localidad.csv"),
                   index=False, encoding="utf-8-sig")
    print(f"✅ epv_agg_localidad.csv  →  {agg_epv.shape}")

# ============================================================
# AGREGACIÓN ECN — por Localidad / Sector / Tamaño
# ============================================================

agg_ecn_loc = None
if ecn_panel is not None:
    if "localidad" in ecn_panel.columns and ecn_panel["localidad"].notna().sum() > 0:
        agg_ecn_loc = ecn_panel.groupby(["año", "localidad"], as_index=False).agg(
            n_empresas        =("indice_clima",      "count"),
            indice_clima_prom =("indice_clima",      "mean"),
            pct_ventas_subio  =("ventas_positivo",   "mean"),
            pct_credito_obtuvo=("credito_positivo",  "mean"),
            pct_invirtio      =("inversion_positivo","mean"),
        ).round(4)
        agg_ecn_loc.to_csv(os.path.join(OUTPUT_DIR, "ecn_agg_localidad.csv"),
                           index=False, encoding="utf-8-sig")
        print(f"✅ ecn_agg_localidad.csv  →  {agg_ecn_loc.shape}")

    if "sector_ciiu" in ecn_panel.columns:
        agg_ecn_sector = ecn_panel.groupby(["año", "sector_ciiu"], as_index=False).agg(
            n_empresas        =("indice_clima",    "count"),
            indice_clima_prom =("indice_clima",    "mean"),
            pct_ventas_subio  =("ventas_positivo", "mean"),
        ).round(4)
        agg_ecn_sector.to_csv(os.path.join(OUTPUT_DIR, "ecn_agg_sector.csv"),
                              index=False, encoding="utf-8-sig")
        print(f"✅ ecn_agg_sector.csv     →  {agg_ecn_sector.shape}")

    if "tamanio_cat" in ecn_panel.columns:
        ecn_tam = ecn_panel[ecn_panel["tamanio_cat"].notna()]
        if len(ecn_tam) > 0:
            agg_ecn_tam = ecn_tam.groupby(["año", "tamanio_cat"], as_index=False).agg(
                n_empresas        =("indice_clima",     "count"),
                indice_clima_prom =("indice_clima",     "mean"),
                pct_ventas_subio  =("ventas_positivo",  "mean"),
                pct_credito_obtuvo=("credito_positivo", "mean"),
            ).round(4)
            orden = ["Microempresa", "Pequeña", "Mediana", "Grande"]
            agg_ecn_tam["tamanio_cat"] = pd.Categorical(
                agg_ecn_tam["tamanio_cat"], categories=orden, ordered=True)
            agg_ecn_tam = agg_ecn_tam.sort_values(["año", "tamanio_cat"])
            agg_ecn_tam.to_csv(os.path.join(OUTPUT_DIR, "ecn_agg_tamanio.csv"),
                               index=False, encoding="utf-8-sig")
            print(f"✅ ecn_agg_tamanio.csv    →  {agg_ecn_tam.shape}")

# ============================================================
# DATASET ANALÍTICO PRINCIPAL — Cruce EPV + ECN por Localidad
# ============================================================

print("\n\n" + " DATASET ANALÍTICO PRINCIPAL ".center(65, "="))

# Agregar EPV a nivel Bogotá por año (todos los propietarios, o si no hay esa preg. se incluyen todos)
epv_bogota_filter = epv_panel[(epv_panel["es_propietario"] == 1) | (epv_panel["es_propietario"].isna())]
epv_bogota = epv_bogota_filter.groupby("año", as_index=False).agg(
    n_propietarios        =("es_propietario",        "sum"),
    tasa_victima_comercio =("victima_comercio_bin",  "mean"),
    tasa_victima_general  =("victima_general_bin",   "mean"),
    tasa_extorsion        =("extorsion_bin",         "mean"),
    percepcion_barrio_prom=("percepcion_barrio",     "mean"),
    inseguridad_percibida =("inseguridad_percibida", "mean"),
    brecha_percepcion     =("brecha_percepcion",     "mean"),
).round(4)

# Agregar ECN a nivel Bogotá por año
ecn_bogota = ecn_panel.groupby("año", as_index=False).agg(
    n_empresas        =("indice_clima",      "count"),
    indice_clima_prom =("indice_clima",      "mean"),
    pct_ventas_subio  =("ventas_positivo",   "mean"),
    pct_credito_obtuvo=("credito_positivo",  "mean"),
    pct_invirtio      =("inversion_positivo","mean"),
).round(4)

# Cruce por año
dataset_principal = epv_bogota.merge(ecn_bogota, on="año", how="inner")
dataset_principal.to_csv(
    os.path.join(OUTPUT_DIR, "dataset_analitico_principal.csv"),
    index=False, encoding="utf-8-sig"
)
print(f"✅ dataset_analitico_principal.csv → {dataset_principal.shape}")
print(dataset_principal.to_string(index=False))

# ============================================================
# DIAGNÓSTICO FINAL
# ============================================================

print(f"\n\n{'='*65}")
print("  ARCHIVOS GENERADOS EN:", OUTPUT_DIR)
print(f"{'='*65}")
archivos = [
    ("epv_panel.csv",                   "Panel EPV — todos los encuestados"),
    ("ecn_panel.csv",                   "Panel ECN — todas las empresas"),
    ("epv_agg_localidad.csv",           "EPV propietarios por localidad   ← CLAVE"),
    ("ecn_agg_localidad.csv",           "ECN empresas por localidad       ← CLAVE"),
    ("ecn_agg_sector.csv",              "ECN por sector CIIU"),
    ("ecn_agg_tamanio.csv",             "ECN por tamaño empresa (2022-2024)"),
    ("dataset_analitico_principal.csv", "CRUCE EPV+ECN por localidad      ← ANÁLISIS"),
]
for archivo, desc in archivos:
    existe = "✅" if os.path.exists(os.path.join(OUTPUT_DIR, archivo)) else "⬜"
    print(f"  {existe}  {archivo:45s}  {desc}")

print(f"""
🎯 SIGUIENTE PASO — Script 4: Análisis y visualizaciones
   Correlaciones clave a explorar:
   • tasa_victima_comercio   ↔  indice_clima_prom
   • inseguridad_percibida   ↔  pct_ventas_subio
   • brecha_percepcion       ↔  pct_credito_obtuvo
   • Diferencias por tamaño: ¿Microempresas más afectadas?
   • Diferencias por sector CIIU: ¿Comercio vs industria?
""")
