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

## Folder structure

Minimum-Temperature-Raster/
├── README.md
├── requirements.txt
├── .streamlit/
│ └── config.toml
├── data/
│ ├── raw/
│ │ ├── raster/
│ │ │ └── tmin_peru.tif
│ │ └── vectors/
│ │ └── DISTRITOS_LIMITES.zip
│ ├── clean/
│ │ └── peru_distrital_simple.geojson
│ └── processed/
│ ├── tmin_zonal_distritos.csv
│ ├── top15_tmin_mean_alta.csv
│ ├── top15_tmin_mean_baja.csv
│ └── tmin_choropleth.png
├── scripts/
│ ├── prepare_data.py
│ └── zonal_stats.py
└── app/
└── streamlit_app.py


> Tip: Keep heavy shapefiles zipped in `data/raw/vectors/`. The scripts can read from the cleaned GeoJSON in `data/clean/`.

---

## Reproducibility

### 1) Environment
- Python **3.10+**
- Install deps:
```bash
pip install -r requirements.txt

2) Place datasets

GeoTIFF → data/raw/raster/tmin_peru.tif

Vectors (INEI districts zipped) → data/raw/vectors/DISTRITOS_LIMITES.zip

3) Prepare data
python scripts/prepare_data.py

Creates:

data/clean/peru_distrital_simple.geojson (cleaned vectors)

Raster inspection (CRS, bands, dtype, min/max; warns if °C×10)

4) Zonal statistics & plots
python scripts/zonal_stats.py

Outputs to data/processed/:

tmin_zonal_distritos.csv

top15_tmin_mean_alta.csv

top15_tmin_mean_baja.csv

tmin_choropleth.png

5) Run the app
streamlit run app/streamlit_app.py

The app includes:

Choropleth PNG full-width with styled caption & download.

Interactive Altair bars (Top/Bottom 15) with metric selector.

Filtered table with gradient + two decimals and CSV export.

KPIs with thousand separators & emojis.

Public policies tab (3 prioritized measures).

Technical requirements

Python 3.10+

Packages: geopandas, rasterio, rasterstats, rioxarray, shapely, pyproj, matplotlib, pandas, numpy, streamlit, altair

Use relative paths and EPSG:4326 (unless computing areas).

Use /temp/ for intermediates as per class convention.

What’s done so far

Repository structure consolidated (data/raw, data/clean, data/processed, scripts, app).

Vectors managed as ZIP in data/raw/vectors/ and cleaned to GeoJSON.

Processed outputs present (zonal stats, top/bottom, choropleth PNG).

Streamlit app polished:

Centered title + compact typography (CSS).

Altair interactive bars for Top/Bottom 15.

DataFrames with 2-decimal formatting + gradient heatmap.

KPIs with thousand separators and emojis.

Choropleth PNG displayed full width with caption and download.

Team & Responsibilities

Sarita Sánchez – Data preparation, repository setup, reproducibility.

Vivi Saurino – Zonal statistics & data aggregation; wiring datasets; Streamlit polishing
(CSS title/typography, Altair charts, gradient tables with 2 decimals, KPIs con separadores y emojis, styled choropleth with caption & download); folder hygiene and data placement decisions.

[Nombre 3] – Visualization (extra plots/maps/rankings).

[Nombre 4] – Streamlit deployment & public policy write-up.

Replace placeholders with your teammates’ names and scopes.

Next steps

Validate band-year mapping in the GeoTIFF.

Add a custom risk index (e.g., combine p10 with altitude).

Deploy to Streamlit Community Cloud and add the link here.

Add a screenshot of the app to this README.
