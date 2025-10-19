import streamlit as st

st.set_page_config(page_title="Peru Tmin – Raster", layout="wide")

st.title("Peru Minimum Temperature (Tmin) – Raster Dashboard")
st.markdown("""
**Versión inicial (stub).**
- Sube el GeoTIFF (Tmin) o usa el que está en `/data/raw/raster/`.
- Próximamente: filtros por territorio, zonal stats, plots y mapa estático.
""")

uploaded = st.file_uploader("Sube un GeoTIFF de Tmin", type=["tif", "tiff"])
if uploaded is None:
    st.info("Aún no cargaste un raster. Equipo: conectaremos aquí el cálculo de zonal stats.")
else:
    st.success("Raster cargado. (Pendiente: parsear bandas, reescalar si ×10 y calcular métricas)")
