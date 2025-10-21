import os
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------
# Rutas
# -------------------------
RASTER_PATH = 'data/raw/raster/tmin_peru.tif'
VECTORS_ZIP = 'data/raw/vectors/DISTRITOS_LIMITES.zip'
OUT_DIR     = 'data/processed'
CSV_OUT     = os.path.join(OUT_DIR, 'tmin_zonal_distritos.csv')
PNG_OUT     = os.path.join(OUT_DIR, 'tmin_choropleth.png')

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------
# Utilidades
# -------------------------
def dedup_columns(cols):
    """Devuelve una lista de nombres únicos: col, col_1, col_2, ..."""
    seen = {}
    out = []
    for c in cols:
        key = str(c)
        if key not in seen:
            seen[key] = 0
            out.append(key)
        else:
            seen[key] += 1
            out.append(f"{key}_{seen[key]}")
    return out

def pick(lst, default=None):
    return lst[0] if len(lst)>0 else default

# -------------------------
# Leer distritos desde ZIP
# -------------------------
gdf = gpd.read_file(f'zip://{VECTORS_ZIP}')

# Deduplicar nombres de columnas para evitar el error
gdf = gdf.copy()
gdf.columns = dedup_columns(gdf.columns)

# Intentar detectar columnas clave
cand_ubigeo = [c for c in gdf.columns if 'UBIGEO' in c.upper() or c.upper()=='UBIGEO']
cand_dep    = [c for c in gdf.columns if 'DEP' in c.upper() or 'DEPART' in c.upper()]
cand_pro    = [c for c in gdf.columns if 'PROV' in c.upper()]
cand_dis    = [c for c in gdf.columns if 'DIST' in c.upper()]

ubigeo_col = pick(cand_ubigeo)
dep_col    = pick(cand_dep)
pro_col    = pick(cand_pro)
dis_col    = pick(cand_dis)

rename_map = {}
if ubigeo_col: rename_map[ubigeo_col] = 'UBIGEO'
if dep_col:    rename_map[dep_col]    = 'DEPARTAMENTO'
if pro_col:    rename_map[pro_col]    = 'PROVINCIA'
if dis_col:    rename_map[dis_col]    = 'DISTRITO'
gdf = gdf.rename(columns=rename_map)

# Asegurar CRS WGS84
if gdf.crs is None or gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(4326)

# Conservar solo atributos básicos + geometry (evita problemas)
keep_cols = [c for c in ['UBIGEO','DEPARTAMENTO','PROVINCIA','DISTRITO'] if c in gdf.columns]
gdf_min = gdf[keep_cols + ['geometry']].copy()

# -------------------------
# Leer raster
# -------------------------
if not os.path.exists(RASTER_PATH):
    raise FileNotFoundError(f'No se encontró el raster en {RASTER_PATH}')
rds = rasterio.open(RASTER_PATH)

# Si tu ráster estuviera en °C×10, pon scale_factor=0.1
scale_factor = 1.0

# -------------------------
# Estadísticas zonales
#   → pasamos SOLO geometrías para evitar atributos duplicados
# -------------------------
shapes = [geom.__geo_interface__ for geom in gdf_min.geometry]
zs = zonal_stats(
    shapes,
    RASTER_PATH,
    stats=['count','mean','min','max','std','percentile_10','percentile_90'],
    nodata=rds.nodata,
    geojson_out=False
)
df_stats = pd.DataFrame(zs)

# Reescalar si corresponde
if scale_factor != 1.0:
    for c in ['mean','min','max','std','percentile_10','percentile_90']:
        if c in df_stats:
            df_stats[c] = df_stats[c] * (1/scale_factor)

# Índice personalizado de riesgo por frío
p10 = df_stats['percentile_10']
risk_index = np.maximum(0, 5 - p10)               # >0 si p10<5°C
risk_flag  = (df_stats['mean'] < 0).astype(int)   # 1 si Tmin media<0°C
df_stats['risk_index'] = risk_index
df_stats['risk_flag']  = risk_flag

# Unir (atributos básicos + stats)
out = pd.concat([gdf_min[keep_cols].reset_index(drop=True), df_stats], axis=1)

# Guardar CSV
os.makedirs(OUT_DIR, exist_ok=True)
out.to_csv(CSV_OUT, index=False, encoding='utf-8')
print(f'✓ CSV guardado en {CSV_OUT}')

# -------------------------
# Mapa estático
# -------------------------
gplot = gdf_min.join(df_stats[['mean']], how='left')
fig, ax = plt.subplots(figsize=(7.5, 9))
gplot.plot(column='mean', legend=True, linewidth=0.1, edgecolor='black', ax=ax)
ax.set_title('Temperatura mínima media (Tmin) – Distritos')
ax.set_axis_off()
plt.tight_layout()
plt.savefig(PNG_OUT, dpi=200)
plt.close()
print(f'✓ Mapa PNG guardado en {PNG_OUT}')

# Histograma de la Tmin promedio
plt.figure(figsize=(12, 6))
sns.histplot(out['mean'], kde=True, bins=30, color='skyblue', edgecolor='black')

plt.title('Distribución de Temperatura Mínima Promedio (°C) en Distritos del Perú')
plt.xlabel('Temperatura Mínima Promedio (°C)')
plt.ylabel('Número de Distritos')

plt.axvline(out['mean'].mean(), color='red', linestyle='--',
            label=f'Media: {out["mean"].mean():.2f}°C')
plt.axvline(out['mean'].median(), color='green', linestyle='--',
            label=f'Mediana: {out["mean"].median():.2f}°C')

plt.legend()
plt.tight_layout()

# Guardar histograma
hist_png = os.path.join(OUT_DIR, 'histograma_tmin.png')
plt.savefig(hist_png, dpi=300)
plt.close()
print(f'✓ Histograma guardado en {hist_png}')

# Top/Bottom 15
top_csv  = os.path.join(OUT_DIR, 'top15_tmin_mean_alta.csv')
bot_csv  = os.path.join(OUT_DIR, 'top15_tmin_mean_baja.csv')
rank_cols = keep_cols + ['mean','percentile_10','percentile_90','risk_index','risk_flag']

out.sort_values('mean', ascending=False).head(15)[rank_cols].to_csv(top_csv, index=False, encoding='utf-8')
out.sort_values('mean', ascending=True ).head(15)[rank_cols].to_csv(bot_csv, index=False, encoding='utf-8')
print('✓ Rankings top/bottom 15 exportados')
print('Listo ✅')
