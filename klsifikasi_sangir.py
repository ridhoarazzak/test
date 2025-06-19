import streamlit as st
import folium
from streamlit_folium import folium_static
import ee

# === Ambil langsung key dari secrets (dalam format dict TOML) ===
try:
    key_data = dict(st.secrets["SERVICE_ACCOUNT_JSON"])  # langsung dict, tidak json.loads
    credentials = ee.ServiceAccountCredentials(
        service_account=key_data["client_email"],
        key_data=key_data
    )
    ee.Initialize(credentials)
except Exception as e:
    st.error(f"❌ Gagal inisialisasi Earth Engine: {e}")
    st.stop()

# === Fungsi bantu menampilkan EE layer di folium ===
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
        st.error(f"❌ Gagal menambahkan layer EE ke peta: {e}")

folium.Map.add_ee_layer = add_ee_layer

# === Earth Engine Asset & Visualisasi ===
ASSET_ID = "users/mrgridhoarazzak/klasifikasi_asli_sangir"
vis_params = {
    "min": 0,
    "max": 3,
    "palette": ['#006400', '#FFD700', '#FF0000', '#0000FF']
}

# === Tampilan Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Sangir")
st.markdown("**Hasil klasifikasi tutupan lahan di wilayah Sangir berdasarkan Google Earth Engine**")

try:
    image = ee.Image(ASSET_ID)
    m = folium.Map(location=[1.1, 125.4], zoom_start=10)
    m.add_ee_layer(image, vis_params, "Klasifikasi")
    folium.LayerControl().add_to(m)
    folium_static(m)
except Exception as e:
    st.error(f"❌ Gagal menampilkan data: {e}")
