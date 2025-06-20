import streamlit as st
import folium
from streamlit_folium import st_folium  # Ganti folium_static
import ee

# === Inisialisasi Earth Engine ===
try:
    SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
    KEY_PATH = "service_account.json"
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)
except Exception as e:
    st.error("❌ Gagal inisialisasi Earth Engine: %s" % e)
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
        st.error("❌ Gagal menambahkan layer EE: %s" % e)

folium.Map.add_ee_layer = add_ee_layer

# === Visualisasi RGB ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"
vis_params = {
    "bands": ["vis-red", "vis-green", "vis-blue"],
    "min": 0,
    "max": 255
}

# === UI Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Penutupan Lahan dan Penggunaan Lahan Wilayah Sangir")
st.markdown("**Visualisasi RGB berdasarkan citra di Google Earth Engine**")

try:
    image = ee.Image(ASSET_ID)

    # DEBUG: Tampilkan nama band
    band_names = image.bandNames().getInfo()
    st.write("Band citra:", band_names)

    m = folium.Map(location=[-1.5269, 101.3002], zoom_start=10)
    m.add_ee_layer(image, vis_params, "RGB Image")
    folium.LayerControl().add_to(m)

    # Gunakan st_folium (pengganti folium_static)
    st_folium(m, width=700, height=500)
except Exception as e:
    st.error("❌ Gagal menampilkan data: %s" % e)
