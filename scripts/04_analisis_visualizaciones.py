"""
SCRIPT 4: ANÁLISIS ESTADÍSTICO Y VISUALIZACIONES
Datajam CCB - Reto 1: Seguridad Empresarial
-------------------------------------------------
Bloques de análisis:

  BLOQUE A — Longitudinal Bogotá (2021-2024)
    ¿Cómo han evolucionado victimización, percepción y clima juntos?

  BLOQUE B — Correlaciones por Localidad
    ¿Las localidades más inseguras tienen peor clima de negocios?
    Correlación de Pearson/Spearman + scatter con línea de tendencia

  BLOQUE C — Diferencias por Tamaño de Empresa (ECN 2022-2024)
    ¿Las microempresas son más sensibles que las grandes?
    Kruskal-Wallis + boxplot comparativo

  BLOQUE D — Diferencias por Sector CIIU (ECN 2020-2024)
    ¿Hay sectores más vulnerables al clima de inseguridad?
    Comparación de medias + heatmap

Outputs: 10+ gráficos PNG + tabla de resultados estadísticos en Excel
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from pathlib import Path

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURACIÓN
# ============================================================
BASE_PATH = Path(__file__).parent.parent / "data" / "processed"
DATA_DIR  = BASE_PATH / "datasets_analiticos"
OUT_DIR   = BASE_PATH / "visualizaciones"
os.makedirs(OUT_DIR, exist_ok=True)

# Paleta de colores consistente en todo el informe
COLOR_VICTIMA     = "#E63946"   # rojo — victimización / inseguridad
COLOR_PERCEPCION  = "#F4A261"   # naranja — percepción
COLOR_CLIMA       = "#2A9D8F"   # verde azulado — clima de negocios
COLOR_NEUTRAL     = "#457B9D"   # azul — elementos neutros
PALETTE_TAMANIO   = ["#264653", "#2A9D8F", "#E9C46A", "#E76F51"]

plt.rcParams.update({
    "figure.dpi": 130,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

# ============================================================
# CARGA DE DATOS
# ============================================================

def cargar(nombre):
    ruta = os.path.join(DATA_DIR, nombre)
    if not os.path.exists(ruta):
        print(f"  ⚠️  No encontrado: {nombre}")
        return None
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    print(f"  ✅ {nombre:45s} → {df.shape[0]} filas × {df.shape[1]} cols")
    return df

print("\n" + " CARGANDO DATASETS ANALÍTICOS ".center(65, "="))
df_principal  = cargar("dataset_analitico_principal.csv")  # EPV+ECN por localidad
df_epv_loc    = cargar("epv_agg_localidad.csv")            # EPV por localidad
df_ecn_loc    = cargar("ecn_agg_localidad.csv")            # ECN por localidad
df_ecn_sector = cargar("ecn_agg_sector.csv")               # ECN por sector
df_ecn_tam    = cargar("ecn_agg_tamanio.csv")              # ECN por tamaño

# ============================================================
# UTILIDADES
# ============================================================

def guardar(fig, nombre):
    ruta = os.path.join(OUT_DIR, nombre)
    fig.savefig(ruta, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  💾 {nombre}")
    return ruta

def tabla_corr(x, y, label_x, label_y, df):
    """Calcula Pearson y Spearman, retorna dict con resultados."""
    datos = df[[x, y]].dropna()
    n = len(datos)
    if n < 4:
        return None
    r_p, p_p = stats.pearsonr(datos[x], datos[y])
    r_s, p_s = stats.spearmanr(datos[x], datos[y])
    return {
        "Variable X": label_x, "Variable Y": label_y,
        "N":           n,
        "Pearson r":   round(r_p, 3), "Pearson p":  round(p_p, 4),
        "Spearman r":  round(r_s, 3), "Spearman p": round(p_s, 4),
        "Sig. (α=0.05)": "✅ Sí" if p_p < 0.05 else "❌ No",
    }

resultados_estadisticos = []

# ============================================================
# BLOQUE A — EVOLUCIÓN LONGITUDINAL BOGOTÁ
# ============================================================

print("\n\n" + " BLOQUE A: EVOLUCIÓN LONGITUDINAL ".center(65, "="))

if df_principal is not None:

    # Agregar a nivel Bogotá por año
    bogota_año = df_principal.groupby("año", as_index=False).agg(
        tasa_victima_comercio =("tasa_victima_comercio",  "mean"),
        inseguridad_percibida =("inseguridad_percibida",  "mean"),
        indice_clima_prom     =("indice_clima_prom",      "mean"),
        pct_ventas_subio      =("pct_ventas_subio",       "mean"),
        pct_credito_obtuvo    =("pct_credito_obtuvo",     "mean"),
    ).round(4)
    print(bogota_año.to_string(index=False))

    # ── Gráfico A1: Tres líneas en el tiempo ──────────────────────────────
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    años = bogota_año["año"]

    ax1.plot(años, bogota_año["tasa_victima_comercio"], "o-",
             color=COLOR_VICTIMA, lw=2.2, ms=7, label="Tasa victimización comercial (EPV)")
    ax1.plot(años, bogota_año["inseguridad_percibida"] / 5, "s--",
             color=COLOR_PERCEPCION, lw=2, ms=6, label="Inseguridad percibida /5 (EPV)")
    ax1.set_ylabel("Proporción / Escala normalizada", color="black")
    ax1.set_ylim(0, 1)
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))

    ax2.plot(años, bogota_año["indice_clima_prom"], "^-.",
             color=COLOR_CLIMA, lw=2.2, ms=7, label="Índice clima de negocios (ECN)")
    ax2.set_ylabel("Índice clima (0–1)", color=COLOR_CLIMA)
    ax2.set_ylim(0, 1)

    # Unir leyendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=9)

    ax1.set_title("Evolución longitudinal: Seguridad y Clima de Negocios en Bogotá")
    ax1.set_xlabel("Año")
    ax1.set_xticks(años)
    fig.tight_layout()
    guardar(fig, "A1_evolucion_longitudinal.png")

    # ── Gráfico A2: Barras apiladas — composición del clima ───────────────
    if all(c in bogota_año.columns for c in
           ["pct_ventas_subio", "pct_credito_obtuvo", "indice_clima_prom"]):
        fig, ax = plt.subplots(figsize=(9, 5))
        x = np.arange(len(años))
        w = 0.25
        ax.bar(x - w, bogota_año["pct_ventas_subio"],    w, label="Ventas aumentaron",
               color=COLOR_CLIMA,    alpha=0.85)
        ax.bar(x,     bogota_año["pct_credito_obtuvo"],  w, label="Crédito obtenido",
               color=COLOR_NEUTRAL,  alpha=0.85)
        ax.bar(x + w, bogota_año["indice_clima_prom"],   w, label="Índice clima compuesto",
               color=COLOR_PERCEPCION, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(años)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.set_title("Componentes del Clima de Negocios por Año — Bogotá")
        ax.set_ylabel("Proporción de empresas")
        ax.legend(fontsize=9)
        fig.tight_layout()
        guardar(fig, "A2_componentes_clima_por_año.png")


# ============================================================
# BLOQUE B — CORRELACIONES POR LOCALIDAD
# ============================================================

print("\n\n" + " BLOQUE B: CORRELACIONES POR LOCALIDAD ".center(65, "="))

if df_principal is not None and len(df_principal) >= 4:

    PARES_CORRELACION = [
        ("tasa_victima_comercio", "indice_clima_prom",
         "Tasa victimización comercial", "Índice clima de negocios"),
        ("inseguridad_percibida", "indice_clima_prom",
         "Inseguridad percibida (1-5)", "Índice clima de negocios"),
        ("inseguridad_percibida", "pct_ventas_subio",
         "Inseguridad percibida", "% empresas con ventas al alza"),
        ("tasa_victima_comercio", "pct_credito_obtuvo",
         "Tasa victimización comercial", "% empresas que obtuvieron crédito"),
        ("brecha_percepcion", "indice_clima_prom",
         "Brecha percepción barrio-ciudad", "Índice clima de negocios"),
    ]

    for x_col, y_col, label_x, label_y in PARES_CORRELACION:
        if x_col not in df_principal.columns or y_col not in df_principal.columns:
            print(f"  ⚠️  Columnas no disponibles: {x_col}, {y_col}")
            continue

        res = tabla_corr(x_col, y_col, label_x, label_y, df_principal)
        if res:
            resultados_estadisticos.append(res)
            print(f"\n  {label_x}  ↔  {label_y}")
            print(f"    N={res['N']}  Pearson r={res['Pearson r']} (p={res['Pearson p']})  "
                  f"Spearman r={res['Spearman r']} (p={res['Spearman p']})  {res['Sig. (α=0.05)']}")

        # Scatter con línea de regresión
        cols_to_extract = [x_col, y_col, "año"]
        if "localidad" in df_principal.columns:
            cols_to_extract.append("localidad")
        
        datos = df_principal[cols_to_extract].dropna()
        if len(datos) < 4:
            continue

        fig, ax = plt.subplots(figsize=(9, 6))
        scatter = ax.scatter(
            datos[x_col], datos[y_col],
            c=datos["año"], cmap="viridis",
            alpha=0.65, s=60, edgecolors="white", linewidths=0.5
        )
        plt.colorbar(scatter, ax=ax, label="Año")

        # Línea de regresión
        m, b = np.polyfit(datos[x_col], datos[y_col], 1)
        x_line = np.linspace(datos[x_col].min(), datos[x_col].max(), 100)
        ax.plot(x_line, m * x_line + b, "--", color=COLOR_VICTIMA, lw=1.8, alpha=0.8)

        # Anotar algunas localidades destacadas
        if "localidad" in df_principal.columns:
            for _, row in datos.nlargest(3, x_col).iterrows():
                ax.annotate(str(row["localidad"]),
                            (row[x_col], row[y_col]),
                            xytext=(5, 3), textcoords="offset points",
                            fontsize=7.5, color="#333333")

        # Añadir r y p al gráfico
        if res:
            ax.text(0.05, 0.95,
                    f"Pearson r = {res['Pearson r']}  (p = {res['Pearson p']})\n"
                    f"Spearman r = {res['Spearman r']}  (p = {res['Spearman p']})",
                    transform=ax.transAxes, fontsize=9,
                    verticalalignment="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        ax.set_xlabel(label_x)
        ax.set_ylabel(label_y)
        title_suffix = "(por localidad-año)" if "localidad" in df_principal.columns else "(por año)"
        ax.set_title(f"{label_x}\n↔ {label_y}  {title_suffix}")
        fig.tight_layout()
        nombre_graf = f"B_scatter_{x_col[:12]}_{y_col[:12]}.png"
        guardar(fig, nombre_graf)

    # ── Mapa de calor: correlaciones entre todas las variables ────────────
    vars_heatmap = [c for c in [
        "tasa_victima_comercio", "tasa_victima_general", "tasa_extorsion",
        "inseguridad_percibida", "brecha_percepcion",
        "indice_clima_prom", "pct_ventas_subio", "pct_credito_obtuvo", "pct_invirtio"
    ] if c in df_principal.columns]

    if len(vars_heatmap) >= 4:
        corr_matrix = df_principal[vars_heatmap].corr(method="spearman")
        etiquetas = {
            "tasa_victima_comercio": "Victimización\ncomercial",
            "tasa_victima_general":  "Victimización\ngeneral",
            "tasa_extorsion":        "Extorsión",
            "inseguridad_percibida": "Inseguridad\npercibida",
            "brecha_percepcion":     "Brecha\npercepción",
            "indice_clima_prom":     "Índice\nclima",
            "pct_ventas_subio":      "Ventas\naumentaron",
            "pct_credito_obtuvo":    "Crédito\nobtenido",
            "pct_invirtio":          "Inversión\nrealizada",
        }
        corr_matrix.index   = [etiquetas.get(c, c) for c in corr_matrix.index]
        corr_matrix.columns = [etiquetas.get(c, c) for c in corr_matrix.columns]

        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(
            corr_matrix, mask=mask,
            annot=True, fmt=".2f", center=0,
            cmap="RdYlGn", vmin=-1, vmax=1,
            linewidths=0.5, ax=ax,
            annot_kws={"size": 9}
        )
        ax.set_title("Matriz de Correlación (Spearman)\nVariables de Seguridad y Clima de Negocios por Localidad")
        fig.tight_layout()
        guardar(fig, "B_heatmap_correlaciones.png")


# ============================================================
# BLOQUE C — DIFERENCIAS POR TAMAÑO DE EMPRESA
# ============================================================

print("\n\n" + " BLOQUE C: ANÁLISIS POR TAMAÑO DE EMPRESA ".center(65, "="))

if df_ecn_tam is not None and len(df_ecn_tam) > 0:

    orden_tam = ["Microempresa", "Pequeña", "Mediana", "Grande"]
    df_ecn_tam["tamanio_cat"] = pd.Categorical(
        df_ecn_tam["tamanio_cat"], categories=orden_tam, ordered=True
    )

    # ── Kruskal-Wallis: diferencias en clima por tamaño ───────────────────
    grupos = [
        df_ecn_tam.loc[df_ecn_tam["tamanio_cat"] == t, "indice_clima_prom"].dropna().values
        for t in orden_tam if t in df_ecn_tam["tamanio_cat"].values
    ]
    grupos_validos = [g for g in grupos if len(g) > 1]

    if len(grupos_validos) >= 2:
        stat_kw, p_kw = stats.kruskal(*grupos_validos)
        print(f"\n  Kruskal-Wallis (índice clima por tamaño):")
        print(f"    H = {stat_kw:.3f}  |  p = {p_kw:.4f}  |  "
              f"{'✅ Diferencias significativas' if p_kw < 0.05 else '❌ Sin diferencias significativas'}")
        resultados_estadisticos.append({
            "Variable X": "Tamaño empresa",
            "Variable Y": "Índice clima de negocios",
            "N": sum(len(g) for g in grupos_validos),
            "Pearson r": None, "Pearson p": None,
            "Spearman r": round(stat_kw, 3), "Spearman p": round(p_kw, 4),
            "Sig. (α=0.05)": "✅ Sí (KW)" if p_kw < 0.05 else "❌ No (KW)",
        })

    # ── Gráfico C1: Líneas de clima por tamaño a lo largo del tiempo ──────
    if "año" in df_ecn_tam.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        for tam, color in zip(orden_tam, PALETTE_TAMANIO):
            sub = df_ecn_tam[df_ecn_tam["tamanio_cat"] == tam].sort_values("año")
            if sub.empty:
                continue
            if "indice_clima_prom" in sub.columns:
                axes[0].plot(sub["año"], sub["indice_clima_prom"],
                             "o-", label=tam, color=color, lw=2, ms=6)
            if "pct_ventas_subio" in sub.columns:
                axes[1].plot(sub["año"], sub["pct_ventas_subio"],
                             "s--", label=tam, color=color, lw=2, ms=6)

        axes[0].set_title("Índice de Clima por Tamaño de Empresa")
        axes[0].set_ylabel("Índice clima (0–1)")
        axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        axes[0].legend(title="Tamaño", fontsize=9)

        axes[1].set_title("% Empresas con Ventas al Alza por Tamaño")
        axes[1].set_ylabel("Proporción")
        axes[1].yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        axes[1].legend(title="Tamaño", fontsize=9)

        for ax in axes:
            ax.set_xlabel("Año")

        fig.suptitle("Sensibilidad del Clima de Negocios según Tamaño de Empresa\n(Pregunta del tutor: ¿son las microempresas más sensibles?)",
                     fontsize=12, fontweight="bold")
        fig.tight_layout()
        guardar(fig, "C1_clima_por_tamanio_tiempo.png")

    # ── Gráfico C2: Boxplot de clima por tamaño (agregado) ────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    tamanios_presentes = [t for t in orden_tam if t in df_ecn_tam["tamanio_cat"].values]
    datos_box = [
        df_ecn_tam.loc[df_ecn_tam["tamanio_cat"] == t, "indice_clima_prom"].dropna().values
        for t in tamanios_presentes
    ]
    bp = ax.boxplot(datos_box, patch_artist=True, notch=False)
    for patch, color in zip(bp["boxes"], PALETTE_TAMANIO[:len(tamanios_presentes)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_xticklabels(tamanios_presentes)
    ax.set_title("Distribución del Índice de Clima por Tamaño de Empresa")
    ax.set_ylabel("Índice clima de negocios (0–1)")
    if len(grupos_validos) >= 2:
        ax.text(0.98, 0.95,
                f"Kruskal-Wallis\nH={stat_kw:.2f}, p={p_kw:.4f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    fig.tight_layout()
    guardar(fig, "C2_boxplot_clima_tamanio.png")

    # ── Gráfico C3: Barras comparativas crédito + ventas por tamaño ───────
    cols_comp = [c for c in ["pct_ventas_subio", "pct_credito_obtuvo"]
                 if c in df_ecn_tam.columns]
    if cols_comp:
        resumen_tam = df_ecn_tam.groupby("tamanio_cat", observed=True)[cols_comp].mean()
        fig, ax = plt.subplots(figsize=(9, 5))
        x = np.arange(len(resumen_tam))
        w = 0.35
        etiq = {"pct_ventas_subio": "Ventas aumentaron", "pct_credito_obtuvo": "Crédito obtenido"}
        colores = [COLOR_CLIMA, COLOR_NEUTRAL]
        for i, (col, color) in enumerate(zip(cols_comp, colores)):
            offset = (i - len(cols_comp) / 2 + 0.5) * w
            ax.bar(x + offset, resumen_tam[col], w,
                   label=etiq.get(col, col), color=color, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(resumen_tam.index)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.set_title("Indicadores de Desempeño por Tamaño de Empresa (2022-2024)")
        ax.set_ylabel("Proporción de empresas")
        ax.legend(fontsize=9)
        fig.tight_layout()
        guardar(fig, "C3_desempeno_por_tamanio.png")


# ============================================================
# BLOQUE D — DIFERENCIAS POR SECTOR CIIU
# ============================================================

print("\n\n" + " BLOQUE D: ANÁLISIS POR SECTOR CIIU ".center(65, "="))

if df_ecn_sector is not None and len(df_ecn_sector) > 0:

    # Limpiar nombres de sector para visualización
    df_ecn_sector["sector_label"] = (
        df_ecn_sector["sector_ciiu"].astype(str).str.strip().str[:35]
    )

    # ── Gráfico D1: Ranking de clima por sector (promedio 2020-2024) ──────
    resumen_sector = (
        df_ecn_sector.groupby("sector_label")[["indice_clima_prom", "pct_ventas_subio"]]
        .mean().sort_values("indice_clima_prom", ascending=True)
    )

    if len(resumen_sector) > 1:
        fig, ax = plt.subplots(figsize=(10, max(5, len(resumen_sector) * 0.45)))
        colores_bar = [COLOR_CLIMA if v >= resumen_sector["indice_clima_prom"].median()
                       else COLOR_VICTIMA for v in resumen_sector["indice_clima_prom"]]
        bars = ax.barh(resumen_sector.index, resumen_sector["indice_clima_prom"],
                       color=colores_bar, alpha=0.82)
        ax.axvline(resumen_sector["indice_clima_prom"].median(),
                   color="gray", ls="--", lw=1.2, label="Mediana")
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.set_title("Índice de Clima de Negocios por Sector CIIU\n(Promedio 2020-2024)")
        ax.set_xlabel("Índice clima (0–1)")
        ax.legend(fontsize=9)
        fig.tight_layout()
        guardar(fig, "D1_ranking_clima_sector.png")

    # ── Gráfico D2: Heatmap sector × año ──────────────────────────────────
    if "año" in df_ecn_sector.columns and "indice_clima_prom" in df_ecn_sector.columns:
        pivot = df_ecn_sector.pivot_table(
            index="sector_label", columns="año",
            values="indice_clima_prom", aggfunc="mean"
        )
        if pivot.shape[0] > 1 and pivot.shape[1] > 1:
            fig, ax = plt.subplots(figsize=(11, max(5, len(pivot) * 0.45)))
            sns.heatmap(
                pivot, annot=True, fmt=".2f", center=pivot.mean().mean(),
                cmap="RdYlGn", ax=ax, linewidths=0.4,
                annot_kws={"size": 8}
            )
            ax.set_title("Índice de Clima de Negocios — Sector × Año")
            ax.set_ylabel("")
            ax.set_xlabel("Año")
            fig.tight_layout()
            guardar(fig, "D2_heatmap_sector_año.png")

    # ── ANOVA de un factor: diferencias entre sectores ───────────────────
    sectores = df_ecn_sector["sector_label"].unique()
    grupos_sector = [
        df_ecn_sector.loc[df_ecn_sector["sector_label"] == s, "indice_clima_prom"]
        .dropna().values
        for s in sectores
    ]
    grupos_sector = [g for g in grupos_sector if len(g) > 1]
    if len(grupos_sector) >= 2:
        stat_f, p_f = stats.kruskal(*grupos_sector)
        print(f"\n  Kruskal-Wallis (clima por sector CIIU):")
        print(f"    H = {stat_f:.3f}  |  p = {p_f:.4f}  |  "
              f"{'✅ Sectores significativamente diferentes' if p_f < 0.05 else '❌ Sin diferencias significativas'}")
        resultados_estadisticos.append({
            "Variable X": "Sector CIIU",
            "Variable Y": "Índice clima de negocios",
            "N": sum(len(g) for g in grupos_sector),
            "Pearson r": None, "Pearson p": None,
            "Spearman r": round(stat_f, 3), "Spearman p": round(p_f, 4),
            "Sig. (α=0.05)": "✅ Sí (KW)" if p_f < 0.05 else "❌ No (KW)",
        })


# ============================================================
# TABLA DE RESULTADOS ESTADÍSTICOS
# ============================================================

print("\n\n" + " TABLA DE RESULTADOS ".center(65, "="))

if resultados_estadisticos:
    df_resultados = pd.DataFrame(resultados_estadisticos)
    print(df_resultados.to_string(index=False))

    ruta_tabla = os.path.join(OUT_DIR, "tabla_resultados_estadisticos.xlsx")
    df_resultados.to_excel(ruta_tabla, index=False)
    print(f"\n  💾 tabla_resultados_estadisticos.xlsx")


# ============================================================
# RESUMEN FINAL PARA EL INFORME
# ============================================================

print(f"""
{'='*65}
  ARCHIVOS GENERADOS EN: {OUT_DIR}
{'='*65}

  BLOQUE A — Longitudinal
  ✅ A1_evolucion_longitudinal.png
  ✅ A2_componentes_clima_por_año.png

  BLOQUE B — Correlaciones por localidad
  ✅ B_scatter_[par].png  (uno por cada par de variables)
  ✅ B_heatmap_correlaciones.png

  BLOQUE C — Por tamaño de empresa
  ✅ C1_clima_por_tamanio_tiempo.png
  ✅ C2_boxplot_clima_tamanio.png
  ✅ C3_desempeno_por_tamanio.png

  BLOQUE D — Por sector CIIU
  ✅ D1_ranking_clima_sector.png
  ✅ D2_heatmap_sector_año.png

  ESTADÍSTICOS
  ✅ tabla_resultados_estadisticos.xlsx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HALLAZGOS CLAVE PARA EL INFORME (interpretar con los valores reales):

  H1: ¿Más victimización → peor clima?
      → Ver Pearson/Spearman en B_scatter_tasa_victima_indice_clima

  H2: ¿Más inseguridad percibida → menos ventas?
      → Ver B_scatter_inseguridad_pct_ventas

  H3: ¿Microempresas más afectadas que grandes?
      → Ver C1 y resultado Kruskal-Wallis Bloque C

  H4: ¿Sectores con diferente vulnerabilidad?
      → Ver D1 y D2, resultado Kruskal-Wallis Bloque D
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
