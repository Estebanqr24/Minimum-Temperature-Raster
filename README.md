# Peru Minimum Temperature (Tmin) – Raster Analysis

This repository contains the materials for the team assignment on **minimum temperature (Tmin) raster analysis** for Peru, including zonal statistics, risk insights (frost/cold surges), a public policy section, and a public **Streamlit** app.

## Purpose
- Compute **zonal statistics** from a Tmin **GeoTIFF** (districts preferred).
- Analyze **climate risks** (Andean frosts & Amazon cold surges).
- Propose **evidence-based public policies**.
- Deliver a **Streamlit app** with maps, rankings, filters, and downloads.

---

## Data description
- **Raster (Tmin GeoTIFF)**: Minimum temperature (daily/monthly/annual, per source).
  - If multiband, assume **Band 1 = 2020**, **Band 2 = 2021**, etc. (adjust if metadata differs).
  - If values are scaled (e.g., **°C × 10**), rescale to real °C during analysis.
- **Vectors (administrative boundaries)**: Peru districts preferred (else provinces/departments).
  - Expected fields: **UBIGEO, DEPARTAMENTO, PROVINCIA, DISTRITO**.
  - Standardize to **UPPERCASE** and **remove diacritics**.
- **CRS**: Work in **EPSG:4326 (WGS84)**. Reproject to UTM only when computing areas.

---

## Reproducibility

1) Environment
Python 3.10+
- Option A (minimal for the app): pip install -r requirements.txt
- Option B (local analysis / dev extras: Geo stack): pip install -r requirements-dev.txt


Si usas conda/mamba, crea un env y luego instala con pip dentro del env.

2) Place datasets

- GeoTIFF → data/raw/raster/tmin_peru.tif
- Vectors (INEI districts zipped) → data/raw/vectors/DISTRITOS_LIMITES.zip

3) Prepare data
python scripts/prepare_data.py

Creates:

- data/clean/peru_distrital_simple.geojson (uppercase, sin tildes, geometrías reparadas)
- Chequeos básicos del ráster (CRS, dtype, min/max, multibanda)

4) Zonal statistics + artifacts
python scripts/zonal_stats.py

Creates:

- data/processed/tmin_zonal_distritos.csv
- data/processed/top15_tmin_mean_alta.csv
- data/processed/top15_tmin_mean_baja.csv
- data/processed/tmin_choropleth.png (mapa estático exportado)

---

## Run the Streamlit app

From the repo root:

streamlit run app/streamlit_app.py

The theme is configured in .streamlit/config.toml.

---

## Notes / Conventions

- Prefer relative paths.
- Work in EPSG:4326 unless computing areas (then reproject to a suitable UTM).
- Use data/raw/ for originals, data/clean/ para vectores estandarizados, data/processed/ para resultados/artefactos.

---

## Team & Responsibilities

Sarita Sánchez – Data preparation, repository setup, reproducibility (estructura base, preparación de vectores y ráster, guías de setup).
Vivi Saurino – Zonal statistics, análisis y app:

- Reorganizó la carpeta data/ (unificación de raw/ y processed/, .gitkeep para estructura limpia).
- Subió y ubicó correctamente DISTRITOS_LIMITES.zip y el ráster tmin_peru.tif.
- Ejecutó y depuró scripts/zonal_stats.py (resolución de error por columnas duplicadas en GeoDataFrame).
- Generó artefactos en data/processed/: tmin_zonal_distritos.csv, top15_tmin_mean_alta.csv, top15_tmin_mean_baja.csv y tmin_choropleth.png.
- Implementó y dejó funcionando la app Streamlit (app/streamlit_app.py) con:
- Pestañas: Mapa coroplético, Top/Bottom 15, Resumen y descargas, Políticas públicas.
- Altair para barras interactivas (Top/Bottom).
- Tablas con formato a 2 decimales y filtros (departamento y umbral).
- Métricas/KPI y estilo de página (título centrado, tipografía compacta).
- Tema visual en .streamlit/config.toml y aviso de deprecación resuelto (use_container_width).











## Folder structure
```text
Minimum-Temperature-Raster/
├── README.md
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/
│   │   ├── raster/
│   │   │   └── tmin_peru.tif
│   │   └── vectors/
│   │       └── DISTRITOS_LIMITES.zip
│   ├── clean/
│   │   └── peru_distrital_simple.geojson
│   └── processed/
│       ├── tmin_zonal_distritos.csv
│       ├── top15_tmin_mean_alta.csv
│       ├── top15_tmin_mean_baja.csv
│       └── tmin_choropleth.png
├── scripts/
│   ├── prepare_data.py
│   └── zonal_stats.py
└── app/
    └── streamlit_app.py


Tip: Keep heavy shapefiles zipped in data/raw/vectors/. The scripts can read from the cleaned GeoJSON in data/clean/.

---



