import streamlit as st
import folium
from streamlit_folium import folium_static
import ee

# === Inisialisasi Earth Engine dengan file langsung ===
try:
    SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
    KEY_PATH = "service_account.json"  # File ini ada di folder yang sama dengan app.py

    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)

except Exception as e:
    st.error(f"❌ Gagal inisialisasi Earth Engine: {e}")
    st.stop()

# === Fungsi bantu layer EE ===
def add_ee_layer(self, ee_image_object, vis_params, name):
    try:
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.TileLayer(
            tiles=map_id_dict["tile_fetcher"].url_format,
            attr="Google Earth Engine",
            name=name,
            overlay=True,
            control=True,
        ).add_to(self)
    except Exception as e:
        st.error(f"❌ Gagal menambahkan layer EE: {e}")

folium.Map.add_ee_layer = add_ee_layer

# === Earth Engine Asset & Visualisasi ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024"
vis_params = {
    "min": 0,
    "max": 3,
    "palette": ['#006400', '#FFD700', '#FF0000', '#0000FF']
}

# === UI Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Sangir")
st.markdown("**Hasil klasifikasi tutupan lahan wilayah Sangir berdasarkan Google Earth Engine**")

try:
    image = ee.Image(ASSET_ID)
    m = folium.Map(location=[1.1, 125.4], zoom_start=10)
    m.add_ee_layer(image, vis_params, "Klasifikasi")
    folium.LayerControl().add_to(m)
    folium_static(m)
except Exception as e:
    st.error(f"❌ Gagal menampilkan data: {e}")
