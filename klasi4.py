import streamlit as st
import ee
import folium
from streamlit_folium import folium_static

# Inisialisasi kredensial Earth Engine
SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
KEY_PATH = "service_account.json"
credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(credentials)

# Fungsi bantu untuk menambahkan layer Earth Engine ke folium map
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id_dict["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
    ).add_to(self)

# Tambahkan fungsi ke objek Map
folium.Map.add_ee_layer = add_ee_layer

# Ganti dengan nama asset klasifikasimu di Earth Engine
image_klasifikasi = ee.Image("users/mrgridhoarazzak/klasifikasi_asli_sangir")

# Parameter tampilan layer
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

# Tampilan Streamlit
st.title("🌍 Peta Klasifikasi Sangir")
st.markdown("**Hasil klasifikasi tutupan lahan di wilayah Sangir berdasarkan Google Earth Engine**")

# Tampilkan peta
m = folium.Map(location=[1.1, 125.4], zoom_start=10)
m.add_ee_layer(image_klasifikasi, vis_params, "Hasil Klasifikasi")
folium.LayerControl().add_to(m)

# Tampilkan ke Streamlit
folium_static(m)
