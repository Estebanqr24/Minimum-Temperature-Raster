import os
from pathlib import Path
import io

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import altair as alt  # NEW: para barras bonitas e interactivas

# ---------------------------
# Rutas relativas del proyecto
# ---------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
PNG_MAP = DATA_PROCESSED / "tmin_choropleth.png"
CSV_MAIN = DATA_PROCESSED / "tmin_zonal_distritos.csv"
CSV_TOP  = DATA_PROCESSED / "top15_tmin_mean_alta.csv"
CSV_BOT  = DATA_PROCESSED / "top15_tmin_mean_baja.csv"

st.set_page_config(
    page_title="Tmin Perú – Análisis ráster",
    layout="wide",
    page_icon="❄️"
)

# ===== Estilo (centrar título + tipografía compacta) =====
def inject_css():
    st.markdown("""
        <style>
        /* tipografía y compacidad general */
        html, body, [class*="css"] {
            font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell,
                         "Noto Sans", Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
            font-size: 15px;
            line-height: 1.28;
        }
        /* título centrado y un poco más compacto */
        .stApp h1 {
            text-align: center;
            font-weight: 700;
            letter-spacing: .2px;
            margin-bottom: .4rem;
        }
        /* subtítulos un pelín más compactos */
        .stApp h2 { margin-top: .8rem;  margin-bottom: .45rem; font-weight: 650; }
        .stApp h3 { margin-top: .6rem;  margin-bottom: .35rem; }
        /* padding del contenedor para que todo se vea respirado pero compacto */
        .block-container { padding-top: .9rem; padding-bottom: 1.0rem; }
        /* métrica un poco más pequeña y legible */
        div[data-testid="stMetricValue"] { font-size: 1.15rem; }
        div[data-testid="stMetricDelta"] { font-size: .9rem; }
        /* tabs con un poquito de aire entre ellos */
        div[data-baseweb="tab-list"] { gap: .25rem; }
        </style>
    """, unsafe_allow_html=True)

inject_css()
# ========================================================

# --- Barras Altair (helper) ---
def make_bar_chart(df: pd.DataFrame, metric: str, color: str = "#4E79A7", sort: str = "-y"):
    """
    df: dataframe con columnas 'label' y la métrica numérica.
    metric: 'mean', 'p10', 'p90' o 'risk_index'
    color: color de las barras (hex)
    sort: '-y' para ordenar de mayor a menor (Top), 'y' para menor a mayor (Bottom)
    """
    data = df[["label", metric]].copy()
    data[metric] = pd.to_numeric(data[metric], errors="coerce")

    chart = (
        alt.Chart(data)
        .mark_bar(color=color, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("label:N", sort=sort, axis=alt.Axis(labelAngle=-45, title=None)),
            y=alt.Y(f"{metric}:Q", title=metric),
            tooltip=[
                alt.Tooltip("label:N", title="Distrito"),
                alt.Tooltip(f"{metric}:Q", title=metric, format=".2f"),
            ],
        )
        .properties(height=280)
        .interactive()
    )
    return chart

# --- Tablas bonitas (Paso 4) ---
def style_table(df: pd.DataFrame, metric_cols: list[str], cmap: str = "YlGnBu"):
    """
    Devuelve un Styler con 2 decimales + gradiente para las columnas métricas.
    """
    fmt = {c: "{:.2f}" for c in metric_cols if c in df.columns}
    return (
        df.style
        .format(fmt)
        .background_gradient(cmap=cmap, subset=[c for c in metric_cols if c in df.columns])
        .set_properties(**{"font-size": "0.9rem"})
    )

# ---------------------------
# Utilidades
# ---------------------------
@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Normaliza nombres esperados si existen
    rename = {
        "percentile_10": "p10",
        "percentile_90": "p90"
    }
    df = df.rename(columns=rename)
    return df

@st.cache_data
def load_image(path: Path):
    if path.exists():
        return Image.open(path)
    return None

def bytes_from_df(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

# ---------------------------
# Carga de datos
# ---------------------------
df = load_csv(CSV_MAIN)
top = load_csv(CSV_TOP)
bot = load_csv(CSV_BOT)
img = load_image(PNG_MAP)

# Si faltan top/bottom, los calculamos desde df
if df.shape[0] > 0 and (top.shape[0] == 0 or bot.shape[0] == 0):
    rank_cols = [c for c in ["UBIGEO","DEPARTAMENTO","PROVINCIA","DISTRITO"] if c in df.columns]
    rank_cols += [c for c in ["mean","p10","p90","risk_index","risk_flag"] if c in df.columns]
    top = df.sort_values("mean", ascending=False).head(15)[rank_cols].copy()
    bot = df.sort_values("mean", ascending=True ).head(15)[rank_cols].copy()

# ---------------------------
# Encabezado
# ---------------------------
st.title("Temperatura mínima en Perú (Tmin) – Análisis ráster")
st.caption("Repositorio: **Minimum-Temperature-Raster** · App Streamlit")

# KPI rápidos si hay datos
if df.shape[0] > 0:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distritos", f"{df.shape[0]:,}")
    if "mean" in df:
        c2.metric("Tmin media (°C)", f"{df['mean'].mean():.2f}")
    if "p10" in df:
        c3.metric("P10 (°C) promedio", f"{df['p10'].mean():.2f}")
    if "risk_flag" in df:
        c4.metric("Distritos con Tmin<0°C", int(df["risk_flag"].sum()))

# ---------------------------
# Pestañas
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Mapa coroplético",
    "📊 Top / Bottom 15",
    "🧾 Resumen y descargas",
    "🏛️ Políticas públicas"
])

# ===========
# TAB 1: MAPA
# ===========
with tab1:
    st.subheader("Mapa coroplético – Tmin media por distrito")
    if img is not None:
        # reemplazo para eliminar el warning deprecado
        st.image(img, caption="Coropleta de Tmin media (GeoPandas)", use_container_width=True)
        st.info("Este mapa se genera en el script `scripts/zonal_stats.py` y se guarda en `data/processed/tmin_choropleth.png`.")
    else:
        st.warning("No se encontró el mapa PNG. Asegúrate de ejecutar el script y de que exista `data/processed/tmin_choropleth.png`.")

# ======================
# TAB 2: RANKINGS BARRAS
# ======================
with tab2:
    st.subheader("Ranking de distritos")
    if top.shape[0] == 0 or bot.shape[0] == 0:
        st.warning("No se encontraron archivos de ranking. Se pueden generar desde `scripts/zonal_stats.py`.")
    else:
        metric = st.selectbox(
            "Métrica para ordenar",
            options=[m for m in ["mean","p10","p90","risk_index"] if m in top.columns],
            index=0
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top 15 Tmin media más ALTA**")
            tplot = top.sort_values(metric, ascending=False).copy()
            label_cols = [c for c in ["DEPARTAMENTO","PROVINCIA","DISTRITO"] if c in tplot.columns]
            tplot["label"] = tplot[label_cols].agg(" - ".join, axis=1) if label_cols else tplot.index.astype(str)

            # NEW: barras Altair (Top)
            chart_top = make_bar_chart(tplot, metric, color="#4E79A7", sort="-y")
            st.altair_chart(chart_top, use_container_width=True)

            # (Paso 4) 2 decimales + gradiente
            fmt_cols_top = [c for c in ["mean","p10","p90","risk_index"] if c in tplot.columns]
            st.dataframe(
                style_table(tplot, fmt_cols_top),
                use_container_width=True,
                height=350
            )
            st.download_button("Descargar Top 15 (CSV)", data=bytes_from_df(tplot), file_name="top15.csv", mime="text/csv")

        with c2:
            st.markdown("**Top 15 Tmin media más BAJA**")
            bplot = bot.sort_values(metric, ascending=True).copy()
            label_cols = [c for c in ["DEPARTAMENTO","PROVINCIA","DISTRITO"] if c in bplot.columns]
            bplot["label"] = bplot[label_cols].agg(" - ".join, axis=1) if label_cols else bplot.index.astype(str)

            # NEW: barras Altair (Bottom)
            chart_bot = make_bar_chart(bplot, metric, color="#E15759", sort="y")
            st.altair_chart(chart_bot, use_container_width=True)

            # (Paso 4) 2 decimales + gradiente
            fmt_cols_bot = [c for c in ["mean","p10","p90","risk_index"] if c in bplot.columns]
            st.dataframe(
                style_table(bplot, fmt_cols_bot),
                use_container_width=True,
                height=350
            )
            st.download_button("Descargar Bottom 15 (CSV)", data=bytes_from_df(bplot), file_name="bottom15.csv", mime="text/csv")

# =========================
# TAB 3: RESUMEN + DESCARGA
# =========================
with tab3:
    st.subheader("Filtrado, resumen y descargas")
    if df.shape[0] == 0:
        st.warning("No se encontró `data/processed/tmin_zonal_distritos.csv`.")
    else:
        # Filtros
        colf1, colf2, colf3 = st.columns([2,2,2])
        dep_col = "DEPARTAMENTO" if "DEPARTAMENTO" in df.columns else None
        pro_col = "PROVINCIA" if "PROVINCIA" in df.columns else None

        sel_dep = None
        if dep_col:
            deps = ["(Todos)"] + sorted(df[dep_col].dropna().unique().tolist())
            sel_dep = colf1.selectbox("Departamento", deps, index=0)

        umbral = colf2.slider(
            "Umbral Tmin media (°C)",
            min_value=float(np.nanmin(df["mean"])),
            max_value=float(np.nanmax(df["mean"])),
            value=float(np.nanmedian(df["mean"]))
        )
        criterio = colf3.selectbox("Criterio de umbral", ["≤ (más frío)", "≥ (más cálido)"], index=0)

        df_view = df.copy()
        if sel_dep and dep_col and sel_dep != "(Todos)":
            df_view = df_view[df_view[dep_col] == sel_dep]

        if criterio.startswith("≤"):
            df_view = df_view[df_view["mean"] <= umbral]
        else:
            df_view = df_view[df_view["mean"] >= umbral]

        st.write(f"**Registros filtrados:** {df_view.shape[0]}")

        # (Paso 4) 2 decimales + gradiente en la tabla de resumen
        fmt_cols_view = [c for c in ["mean","p10","p90","risk_index"] if c in df_view.columns]
        st.dataframe(
            style_table(df_view, fmt_cols_view),
            use_container_width=True,
            height=420
        )

        # KPIs del subset
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Tmin media (°C)", f"{df_view['mean'].mean():.2f}")
        if "p10" in df_view:
            k2.metric("P10 promedio", f"{df_view['p10'].mean():.2f}")
        if "p90" in df_view:
            k3.metric("P90 promedio", f"{df_view['p90'].mean():.2f}")
        if "risk_flag" in df_view:
            k4.metric("Distritos Tmin<0°C", int(df_view["risk_flag"].sum()))

        st.download_button("Descargar tabla filtrada (CSV)", data=bytes_from_df(df_view), file_name="tmin_filtrado.csv", mime="text/csv")

        # Descargas “oficiales”
        st.markdown("### Descargas")
        cdl1, cdl2, cdl3 = st.columns(3)
        if CSV_MAIN.exists():
            cdl1.download_button("📥 Zonal stats (CSV)", data=CSV_MAIN.read_bytes(), file_name=CSV_MAIN.name)
        if CSV_TOP.exists():
            cdl2.download_button("📥 Top 15 (CSV)", data=CSV_TOP.read_bytes(), file_name=CSV_TOP.name)
        if CSV_BOT.exists():
            cdl3.download_button("📥 Bottom 15 (CSV)", data=CSV_BOT.read_bytes(), file_name=CSV_BOT.name)

# =========================
# TAB 4: POLÍTICAS PÚBLICAS
# =========================
with tab4:
    st.subheader("Propuestas de políticas públicas")
    st.markdown("""
**Diagnóstico:**  
- Heladas altoandinas concentradas en Puno, Cusco, Ayacucho, Huancavelica y Pasco (P10 y medias bajas).  
- Oleadas de frío amazónico en Loreto, Ucayali y Madre de Dios.  
- Impactos: IRA/ILI, pérdidas agrícolas, mortalidad de camélidos, ausentismo escolar.
""")

    st.markdown("### Medidas priorizadas")
    medidas = [
        {
            "nombre": "1) Viviendas térmicas (ISUR / mejoramiento de envolvente)",
            "objetivo": "Reducir morbilidad respiratoria por frío y pérdidas de calor en hogares vulnerables.",
            "poblacion": "Hogares en distritos con p10 ≤ 3°C y altitud > 3,500 msnm.",
            "costo": "S/ 7,500 por vivienda (materiales + mano de obra + supervisión).",
            "kpi": "↓10–20% casos IRA (Minsa/EsSalud) y ↑2–5% asistencia escolar."
        },
        {
            "nombre": "2) Refugios y kits antiheladas para ganado (camélidos)",
            "objetivo": "Disminuir la mortalidad y morbilidad del hato por heladas.",
            "poblacion": "Productores en distritos con p10 ≤ 0°C y alta densidad de camélidos.",
            "costo": "S/ 4,000 por refugio (módulo) + S/ 300 por kit (medicado/abrigo).",
            "kpi": "↓15–30% mortalidad y ↓20% pérdidas productivas."
        },
        {
            "nombre": "3) Calendario agrícola y alertas tempranas",
            "objetivo": "Ajustar siembras y proteger cultivos ante eventos de friaje.",
            "poblacion": "Productores en distritos con mean ≤ 5°C o alta variabilidad térmica.",
            "costo": "S/ 1.2 millones/año (plataforma + SMS + extensión).",
            "kpi": "↓10% pérdidas por eventos, ↑adopción de prácticas de adaptación."
        }
    ]

    for m in medidas:
        with st.expander(m["nombre"], expanded=False):
            st.write(f"**Objetivo específico:** {m['objetivo']}")
            st.write(f"**Población/territorio objetivo:** {m['poblacion']}")
            st.write(f"**Costo estimado:** {m['costo']}")
            st.write(f"**KPI propuesto:** {m['kpi']}")

    st.info("💡 Ajusta los umbrales con los filtros del panel *Resumen y descargas* para identificar distritos objetivo (por ejemplo, p10 ≤ 3°C).")
