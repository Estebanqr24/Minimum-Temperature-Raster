# Peru Minimum Temperature (Tmin) – Raster Analysis

This repository is the starting point for the team assignment.

## Purpose
Use a minimum temperature (Tmin) GeoTIFF to extract zonal statistics (by department/province/district), analyze climate risks (frost/cold surges), and propose evidence-based public policies. Deliver a public Streamlit app at the end.

## Data description
- **Raster (Tmin GeoTIFF)**: Minimum temperature (daily/monthly/annual depending on the source).
  - If the dataset is multiband, we assume **Band 1 = 2020**, Band 2 = 2021, etc. Adjust if metadata says otherwise.
  - Units: if values are scaled (e.g., °C × 10), we will **rescale to real °C** later in the analysis.
- **Vectors**: Administrative boundaries of **Peru** (preferred: **districts**; if hardware limits, use provinces).
  - Expected fields: `UBIGEO`, `DEPARTAMENTO`, `PROVINCIA`, `DISTRITO`.
  - We standardize to **UPPERCASE** and remove **diacritics**.
  - Working CRS: **EPSG:4326** (WGS84). If you need areas, reproject to a suitable **UTM** zone.

## Folder structure
```
Minimum-Temperature-Raster/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── raster/         # put the Tmin GeoTIFF here
│   │   └── vectors/        # put original shapefiles/GeoJSON here
│   └── clean/              # cleaned vectors will be saved here
├── temp/                   # temporary files (pattern used by class)
├── scripts/
│   └── prepare_data.py     # limpieza de vectores + inspección del raster
└── app/
    └── streamlit_app.py    # stub; to be expanded by the team
```

## Reproducibility
1. Create and activate a Python 3.10+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place datasets:
   - GeoTIFF → `data/raw/raster/`
   - Shapefile/GeoJSON → `data/raw/vectors/`
4. Run the preparation script:
   ```bash
   python scripts/prepare_data.py
   ```
   It will:
   - Clean the vector (uppercase + no diacritics, repair simple geometries, set CRS).
   - Save a cleaned GeoJSON to `data/clean/peru_distrital_simple.geojson`.
   - Inspect the raster (CRS, bands, dtype, min/max) and warn if values look like °C×10.
5. (Next steps) Run zonal stats and build plots/app.

## Technical requirements
- Python 3.10+
- Packages: geopandas, rasterio, rasterstats, rioxarray, shapely, pyproj, matplotlib, pandas, numpy, streamlit

## Notes
- Keep **relative paths** (penalty for absolute paths).
- Work in **EPSG:4326** unless you specifically need areas (then reproject).
- Use `/temp/` for intermediates to follow class conventions.
- 
## Team & Responsibilities
- **Sarita Sánchez** – Data preparation, repository setup, reproducibility.
- **[Nombre 2]** – Zonal statistics and data aggregation.
- **[Nombre 3]** – Visualization (plots, maps, rankings).
- **[Nombre 4]** – Streamlit app and public policy proposals.
