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

$readme = Get-Content README.md -Raw
$readme = $readme -replace '(?s)## Folder structure.*?## Reproducibility', "$blockrnrn## Reproducibility"
Set-Content -Encoding UTF8 README.md $readme


> Notas:
> - Asegúrate de que las tres comillas invertidas (```) estén **solas en su línea** arriba y abajo del árbol.
> - Usa fuente mono-espaciada (GitHub lo hace automáticamente dentro del bloque de código).
> - Si te resulta más cómodo, edítalo directo en la UI de GitHub: **Edit** → pega el bloque → **Commit**.
