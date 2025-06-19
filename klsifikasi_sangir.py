import streamlit as st
import folium
from streamlit_folium import folium_static
import json

# === Inisialisasi Google Earth Engine dari secrets ===
try:
    import ee
    SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
    SERVICE_ACCOUNT_JSON = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, key_data=SERVICE_ACCOUNT_JSON)
    ee.Initialize(credentials)
except ModuleNotFoundError:
    st.error("Modul `earthengine-api` belum diinstal. Silakan install dengan `pip install earthengine-api`.")
    st.stop()
except Exception as e:
    st.error(f"Gagal inisialisasi Earth Engine: {e}")
    st.stop()

# === Fungsi bantu: tambahkan Earth Engine Image ke folium Map ===
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
        st.error(f"Gagal menambahkan layer EE ke peta: {e}")

folium.Map.add_ee_layer = add_ee_layer

# === Earth Engine Asset ID ===
ASSET_ID = "users/mrgridhoarazzak/klasifikasi_asli_sangir"

# === Parameter visualisasi klasifikasi ===
vis_params = {
    "min": 0,
    "max": 3,
    "palette": [
        '#006400',  # Hutan
        '#FFD700',  # Pertanian
        '#FF0000',  # Pemukiman
        '#0000FF'   # Air
    ]
}

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Sangir")
st.markdown("**Hasil klasifikasi tutupan lahan di wilayah Sangir berdasarkan Google Earth Engine**")

# === Buat dan tampilkan peta ===
try:
    image_klasifikasi = ee.Image(ASSET_ID)
    m = folium.Map(location=[1.1, 125.4], zoom_start=10)
    m.add_ee_layer(image_klasifikasi, vis_params, "Hasil Klasifikasi")
    folium.LayerControl().add_to(m)
    folium_static(m)
except Exception as e:
    st.error(f"Gagal memuat data dari Earth Engine: {e}")
