"""
SCRIPT 3b: NORMALIZACIÓN DE LOCALIDADES Y RE-CRUCE EPV + ECN
Datajam CCB - Reto 1: Seguridad Empresarial
-------------------------------------------------
Problema identificado: el inner join entre EPV y ECN por "localidad"
solo emparejó 2 filas porque los strings de localidad tienen formatos
distintos entre bases y años:
  EPV: "Usaquén", "USAQUEN", "Usaquen"
  ECN: "01 - Usaquén", "1", "USAQUEN (1)"

Solución: normalizar ambas columnas a una forma canónica antes del join.
Pasos:
  1. Minúsculas
  2. Eliminar tildes y caracteres especiales
  3. Eliminar números y guiones al inicio ("01 - ", "1.")
  4. Strip de espacios
  5. Tabla de equivalencias manual para casos que no se resuelven solos
  6. Re-hacer el join y verificar cobertura
  7. Guardar dataset_analitico_principal.csv actualizado

INSTRUCCIONES:
  1. Usa la misma lógica de BASE_PATH automático que en Script 3.
  2. Ejecuta. Imprime diagnóstico de matches antes y después.
  3. Si quedan localidades sin match, aparecen en la sección REVISIÓN MANUAL.
"""

import os
import re
import unicodedata
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURACIÓN — igual que en Script 3
# ============================================================
from pathlib import Path
BASE_PATH = Path(__file__).parent.parent / "data" / "processed"
DATA_DIR  = BASE_PATH / "datasets_analiticos"

# ============================================================
# FUNCIÓN DE NORMALIZACIÓN
# ============================================================

def normalizar_localidad(valor):
    """
    Convierte cualquier representación de localidad a forma canónica:
    sin tildes, sin números iniciales, sin guiones, en minúsculas, sin espacios extras.

    Ejemplos:
      "01 - Usaquén"   → "usaquen"
      "USAQUEN"        → "usaquen"
      "1. Usaquén"     → "usaquen"
      "Usaquén (1)"    → "usaquen"
      "usaquen"        → "usaquen"
      "Kennedy"        → "kennedy"
      "08-Kennedy"     → "kennedy"
      nan              → nan
    """
    if pd.isna(valor):
        return np.nan

    s = str(valor).strip()

    # 1. Eliminar tildes (NFD → ASCII)
    s = unicodedata.normalize("NFD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")

    # 2. Minúsculas
    s = s.lower()

    # 3. Quitar patrones numéricos al inicio: "01 - ", "1.", "08-", "(1)", etc.
    s = re.sub(r"^\d+[\s\-\.\)]*", "", s)       # número al inicio
    s = re.sub(r"\s*\(\d+\)\s*$", "", s)         # (número) al final
    s = re.sub(r"\s*-\s*\d+\s*$", "", s)         # - número al final

    # 4. Quitar caracteres no alfanuméricos excepto espacios internos
    s = re.sub(r"[^a-z0-9\s]", " ", s)

    # 5. Colapsar espacios múltiples
    s = re.sub(r"\s+", " ", s).strip()

    return s if s else np.nan


# ============================================================
# TABLA DE EQUIVALENCIAS MANUAL
# (para casos que la normalización automática no resuelve)
# Formato: {valor_normalizado_incorrecto: valor_canonico_correcto}
# Completar si el diagnóstico muestra localidades sin match.
# ============================================================

EQUIVALENCIAS = {
    # Ejemplos comunes en Bogotá — ajustar según lo que salga en el diagnóstico
    "barrios unidos":        "barrios unidos",
    "los martires":          "los martires",
    "santa fe":              "santa fe",
    "san cristobal":         "san cristobal",
    "antonio narino":        "antonio narino",
    "la candelaria":         "la candelaria",
    "rafael uribe uribe":    "rafael uribe uribe",
    "ciudad bolivar":        "ciudad bolivar",
    "puente aranda":         "puente aranda",
    "teusaquillo":           "teusaquillo",
    "engativa":              "engativa",
    "fontibon":              "fontibon",
    "bosa":                  "bosa",
    "kennedy":               "kennedy",
    "tunjuelito":            "tunjuelito",
    "usme":                  "usme",
    "usaquen":               "usaquen",
    "chapinero":             "chapinero",
    "suba":                  "suba",
    "sumapaz":               "sumapaz",
}

def aplicar_equivalencias(valor):
    if pd.isna(valor):
        return valor
    return EQUIVALENCIAS.get(str(valor).strip(), str(valor).strip())


# ============================================================
# CARGA DE AGREGADOS
# ============================================================

print("\n" + " NORMALIZACIÓN DE LOCALIDADES — DIAGNÓSTICO ".center(65, "="))

def cargar(nombre):
    ruta = os.path.join(DATA_DIR, nombre)
    if not os.path.exists(ruta):
        print(f"  ⚠️  No encontrado: {nombre}")
        return None
    return pd.read_csv(ruta, encoding="utf-8-sig")

epv_loc = cargar("epv_agg_localidad.csv")
ecn_loc = cargar("ecn_agg_localidad.csv")

if epv_loc is None or ecn_loc is None:
    print("ERROR: Faltan archivos. Corre primero el Script 3.")
    exit()

print(f"\n  EPV agregado: {epv_loc.shape}  | Años: {sorted(epv_loc['año'].unique())}")
print(f"  ECN agregado: {ecn_loc.shape}  | Años: {sorted(ecn_loc['año'].unique())}")

# ============================================================
# DIAGNÓSTICO ANTES DE NORMALIZAR
# ============================================================

print("\n\n--- ANTES de normalizar ---")
epv_loc["localidad"] = epv_loc["localidad"].astype(str)
ecn_loc["localidad"] = ecn_loc["localidad"].astype(str)
cross_antes = epv_loc.merge(ecn_loc, on=["año", "localidad"], how="inner")
print(f"  Filas cruzadas (inner join): {len(cross_antes)}")
print(f"  Localidades EPV únicas:      {epv_loc['localidad'].nunique()}")
print(f"  Localidades ECN únicas:      {ecn_loc['localidad'].nunique()}")

# Mostrar muestra de valores actuales
print(f"\n  Muestra valores localidad EPV: {sorted(epv_loc['localidad'].dropna().unique())[:10]}")
print(f"  Muestra valores localidad ECN: {sorted(ecn_loc['localidad'].dropna().unique())[:10]}")

# ============================================================
# APLICAR NORMALIZACIÓN
# ============================================================

print("\n\n--- Aplicando normalización ---")

epv_loc["localidad_norm"] = (
    epv_loc["localidad"]
    .apply(normalizar_localidad)
    .apply(aplicar_equivalencias)
)

ecn_loc["localidad_norm"] = (
    ecn_loc["localidad"]
    .apply(normalizar_localidad)
    .apply(aplicar_equivalencias)
)

print(f"\n  Localidades EPV normalizadas: {sorted(epv_loc['localidad_norm'].dropna().unique())}")
print(f"\n  Localidades ECN normalizadas: {sorted(ecn_loc['localidad_norm'].dropna().unique())}")

# ============================================================
# DIAGNÓSTICO DESPUÉS DE NORMALIZAR
# ============================================================

print("\n\n--- DESPUÉS de normalizar ---")
cross_despues = epv_loc.merge(
    ecn_loc,
    left_on=["año", "localidad_norm"],
    right_on=["año", "localidad_norm"],
    how="inner"
)

n_antes   = len(cross_antes)
n_despues = len(cross_despues)
print(f"  Filas cruzadas ANTES:  {n_antes}")
print(f"  Filas cruzadas DESPUÉS: {n_despues}  ← {'✅ Mejoró' if n_despues > n_antes else '⚠️  Sin mejora'}")
print(f"  Localidades en cruce: {cross_despues['localidad_norm'].nunique()}")

# ============================================================
# LOCALIDADES SIN MATCH — REVISIÓN MANUAL
# ============================================================

loc_epv = set(epv_loc["localidad_norm"].dropna().unique())
loc_ecn = set(ecn_loc["localidad_norm"].dropna().unique())

solo_epv = loc_epv - loc_ecn
solo_ecn = loc_ecn - loc_epv
en_ambas = loc_epv & loc_ecn

print(f"\n\n--- Cobertura de localidades ---")
print(f"  En AMBAS bases (matchean):       {len(en_ambas):2d} → {sorted(en_ambas)}")
print(f"  Solo en EPV (sin match en ECN):  {len(solo_epv):2d} → {sorted(solo_epv)}")
print(f"  Solo en ECN (sin match en EPV):  {len(solo_ecn):2d} → {sorted(solo_ecn)}")

if solo_epv or solo_ecn:
    print("""
  ⚠️  ACCIÓN REQUERIDA:
  Si hay localidades sin match que deberían emparejar, agrégalas al
  diccionario EQUIVALENCIAS al inicio del script y vuelve a ejecutar.
  Ejemplo: si EPV tiene "chapinero norte" y ECN tiene "chapinero",
  agrega: "chapinero norte": "chapinero"
    """)

# ============================================================
# GUARDAR VERSIÓN ACTUALIZADA DEL DATASET PRINCIPAL
# ============================================================

if n_despues >= 5:
    # Renombrar localidad_norm como localidad para el dataset final
    cross_final = cross_despues.copy()

    # Conservar el nombre original de EPV como referencia
    if "localidad_x" in cross_final.columns:
        cross_final = cross_final.rename(columns={
            "localidad_x": "localidad_epv_original",
            "localidad_y": "localidad_ecn_original",
        })
    cross_final = cross_final.rename(columns={"localidad_norm": "localidad"})

    ruta_out = os.path.join(DATA_DIR, "dataset_analitico_principal.csv")
    cross_final.to_csv(ruta_out, index=False, encoding="utf-8-sig")

    print(f"\n✅ dataset_analitico_principal.csv actualizado")
    print(f"   Shape: {cross_final.shape}")
    print(f"   Años:  {sorted(cross_final['año'].unique())}")
    print(f"   Localidades: {cross_final['localidad'].nunique()}")

    cols_vista = ["año", "localidad",
                  "tasa_victima_comercio", "inseguridad_percibida",
                  "indice_clima_prom",     "pct_ventas_subio"]
    cols_ok = [c for c in cols_vista if c in cross_final.columns]
    print(f"\n  Vista previa:")
    print(cross_final[cols_ok].head(12).to_string(index=False))

    print(f"""
{'='*65}
  SIGUIENTE PASO:
  Corre el Script 4 nuevamente con este dataset actualizado.
  Con N >= {n_despues} filas ya tienes suficiente para:
    • Pearson / Spearman por pares de variables
    • Scatter con línea de regresión
    • Heatmap de correlaciones completo
{'='*65}
    """)

else:
    print(f"""
  ⚠️  Solo {n_despues} filas en el cruce. Aún insuficiente para correlaciones.
  Pasos para depurar:

  1. Revisa las listas "Solo en EPV" y "Solo en ECN" de arriba.
  2. Identifica pares que son la misma localidad con distinto nombre.
  3. Agrégalos al diccionario EQUIVALENCIAS y re-ejecuta este script.

  Alternativa si el problema persiste:
  → Hacer el cruce SOLO por año (nivel Bogotá), sin localidad.
    Con 4-5 años tienes N=4-5 puntos para el análisis longitudinal.
    Agrega al análisis la dimensión de tamaño y sector de la ECN
    como variables de heterogeneidad (que sí tienen suficiente N).
    """)
