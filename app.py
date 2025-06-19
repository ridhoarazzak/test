import streamlit as st
import folium
from streamlit_folium import folium_static
import ee

# === Inisialisasi Earth Engine ===
try:
    SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
    KEY_PATH = "service_account.json"

    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)
except Exception as e:
    st.error(f"❌ Gagal inisialisasi Earth Engine: {e}")
    st.stop()

# === Fungsi bantu tambah layer EE ===
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

# === Earth Engine Asset & Visualisasi RGB ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"

# GUNAKAN nama band RGB kamu, misalnya vis-red, vis-green, vis-blue
vis_params = {
    "bands": ["vis-red", "vis-green", "vis-blue"],
    "min": 0,
    "max": 255
}

# === UI Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta RGB Wilayah Sangir")
st.markdown("**Visualisasi RGB berdasarkan citra di Google Earth Engine**")

try:
    image = ee.Image(ASSET_ID)
    
    # DEBUG: Tampilkan band untuk verifikasi
    band_names = image.bandNames().getInfo()
    st.write("Band citra:", band_names)

    m = folium.Map(location=[-1.80, 101.15], zoom_start=10)
    m.add_ee_layer(image, vis_params, "RGB Image")
    folium.LayerControl().add_to(m)
    folium_static(m)
except Exception as e:
    st.error(f"❌ Gagal menampilkan data: {e}")
