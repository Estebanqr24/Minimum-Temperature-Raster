# scripts/prepare_data.py
# Python 3.10+
# Objetivo: dejar shapes limpios y chequear raster para el análisis.
# Uso: python scripts/prepare_data.py

import os
import unicodedata
import warnings
warnings.filterwarnings("ignore")

import geopandas as gpd
from shapely.geometry import shape
from pyproj import CRS
import rasterio

# ---------------------------
# Config (rutas relativas)
# ---------------------------
DATA_DIR = "data"
RAW_RASTER_DIR = os.path.join(DATA_DIR, "raw", "raster")
RAW_VECTOR_DIR = os.path.join(DATA_DIR, "raw", "vectors")
CLEAN_DIR = os.path.join(DATA_DIR, "clean")
TEMP_DIR = "temp"

# archivo de salida (cámbialo a provincial si usas provincias)
OUT_VECTOR = os.path.join(CLEAN_DIR, "peru_distrital_simple.geojson")

# nombre(s) de archivo esperados (ajusta a lo que tengas)
# Ejemplo shapefile distrital: "PERU_DISTRITOS.shp" (colócalo en data/raw/vectors/)
VECTOR_FILENAME = None  # intenta autodetectar .shp o .geojson si es None
RASTER_FILENAME = None  # intenta autodetectar .tif si es None

TARGET_CRS = CRS.from_epsg(4326)  # trabajo en WGS84
# ---------------------------


def ensure_dirs():
    for d in [DATA_DIR, RAW_RASTER_DIR, RAW_VECTOR_DIR, CLEAN_DIR, TEMP_DIR]:
        os.makedirs(d, exist_ok=True)


def strip_accents_upper(s: str) -> str:
    if s is None:
        return s
    s = s.upper()
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )
    return s


def autodetect_file(folder: str, exts=(".shp", ".geojson", ".json", ".gpkg")):
    for fname in os.listdir(folder):
        if fname.lower().endswith(exts):
            return os.path.join(folder, fname)
    return None


def autodetect_tif(folder: str):
    for fname in os.listdir(folder):
        if fname.lower().endswith((".tif", ".tiff")):
            return os.path.join(folder, fname)
    return None


def clean_vector(in_path: str, out_path: str):
    print(f"[INFO] Leyendo vector: {in_path}")
    gdf = gpd.read_file(in_path)

    # asegurar CRS (si no tiene, asumir WGS84; si tiene distinto, reproyectar)
    if gdf.crs is None:
        print("[WARN] Vector sin CRS; asumiendo EPSG:4326")
        gdf.set_crs(TARGET_CRS, inplace=True)
    elif gdf.crs != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)

    # normalizar nombres de columnas clave (ubigeo/nombres)
    rename_map = {}
    for col in gdf.columns:
        col_norm = strip_accents_upper(col)
        rename_map[col] = col_norm
    gdf = gdf.rename(columns=rename_map)

    # intenta estandarizar campos típicos
    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO", "NOMBRE", "NOMBDIST", "NOMBDEP", "NOMBPROV"]:
        if col in gdf.columns:
            gdf[col] = gdf[col].astype(str).map(strip_accents_upper)

    # UBIGEO: crear si no existe y tenemos partes
    if "UBIGEO" not in gdf.columns:
        # intenta detectar otro nombre para UBIGEO
        for cand in ["UBIGEO_DIST", "UBIGEO_DPT", "UBIGEO_PROV", "CODIGO", "IDUBIGEO"]:
            if cand in gdf.columns:
                gdf["UBIGEO"] = gdf[cand].astype(str)
                break

    # Geometrías válidas (fix simples)
    gdf = gdf[~gdf.geometry.is_empty].copy()
    gdf = gdf[~gdf.geometry.isna()].copy()
    gdf["geometry"] = gdf.buffer(0)  # reparación ligera

    # guardar limpio
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"[OK] Vector limpio guardado en: {out_path}")
    print(f"[INFO] Total features: {len(gdf)} | CRS: {gdf.crs}")


def inspect_raster(raster_path: str):
    print(f"[INFO] Inspeccionando raster: {raster_path}")
    with rasterio.open(raster_path) as src:
        print(f"  - CRS: {src.crs}")
        print(f"  - Size: {src.width} x {src.height}")
        print(f"  - Count (bandas): {src.count}")
        print(f"  - Dtype: {src.dtypes[0]}")
        print(f"  - Transform (affine): {src.transform}")

        # Heurística simple: si dtype es int y valores típicos ~ -200..500, podría ser °C*10
        # (Aquí solo mostramos; el reescalado real se hará en la etapa de zonal stats)
        sample = src.read(1, masked=True)
        vmin = float(sample.min()) if sample.size else None
        vmax = float(sample.max()) if sample.size else None
        print(f"  - Valor mínimo (banda 1): {vmin}")
        print(f"  - Valor máximo (banda 1): {vmax}")
        if vmax and abs(vmax) > 90:  # >90°C sugiere escala *10
            print("  [NOTE] Los valores sugieren escala ×10 (p.ej., -30°C => -300). Reescalar luego a °C.")

        # sugerir mapping banda->año
        print("  - Asumiremos: Banda 1 = 2020, Banda 2 = 2021, ... (ajustar si el metadato indica otro mapeo)")


def main():
    ensure_dirs()

    vec_path = autodetect_file(RAW_VECTOR_DIR) if True else None
    if not vec_path:
        print(f"[ERROR] No se encontró vector en {RAW_VECTOR_DIR}. Coloca un .shp/.geojson y vuelve a correr.")
        return

    tif_path = autodetect_tif(RAW_RASTER_DIR)
    if not tif_path:
        print(f"[WARN] No se encontró raster en {RAW_RASTER_DIR}. Puedes correr la limpieza de vector igual.")

    # limpia y guarda el vector
    clean_vector(vec_path, OUT_VECTOR)

    # inspección rápida del raster (si existe)
    if tif_path:
        inspect_raster(tif_path)
        print("[TIP] Si el raster está en otra proyección, rasterio reproyecta on-the-fly al cruzar con geometrías en EPSG:4326,")
        print("     pero para zonal stats es mejor tener ambos coherentes o usar rasterstats con geometrías en el CRS del raster.")


if __name__ == "__main__":
    main()
