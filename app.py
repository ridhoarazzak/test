import streamlit as st
import folium
from streamlit_folium import st_folium
import ee
import json
import pandas as pd
import geopandas as gpd

# === Inisialisasi Earth Engine dari st.secrets ===
try:
    service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
    credentials = ee.ServiceAccountCredentials(
        service_account_info["client_email"], key_data=service_account_info
    )
    ee.Initialize(credentials)
except Exception as e:
    st.error("❌ Gagal inisialisasi Earth Engine: %s" % e)
    st.stop()

# === Fungsi bantu: Tambahkan Layer EE ke Folium ===
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

# === Pengaturan Visualisasi ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"
vis_params = {
    "bands": ["vis-red", "vis-green", "vis-blue"],
    "min": 0,
    "max": 255
}

# === UI Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Penutupan & Penggunaan Lahan - Sangir")
st.markdown("Visualisasi RGB berbasis Google Earth Engine")

# === Load dan Tampilkan Peta ===
try:
    image = ee.Image(ASSET_ID)
    band_names = image.bandNames().getInfo()
    st.write("📌 Band citra:", band_names)

    m = folium.Map(location=[-1.5269, 101.3002], zoom_start=10)
    m.add_ee_layer(image, vis_params, "Citra RGB")
    folium.LayerControl().add_to(m)

    st_folium(m, width=700, height=500)

except Exception as e:
    st.error("❌ Gagal menampilkan data: %s" % e)

# === Analisis Luas per Kelas (dari geojson) ===
st.subheader("📊 Luas Kelas Penutup Lahan")

# Mapping ID kelas
class_map = {
    0: "Hutan",
    1: "Pertanian",
    2: "Permukiman",
    3: "Air"
}

try:
    # Load geojson lokal (sudah diupload via Streamlit file uploader atau disiapkan sebelumnya)
    gdf = gpd.read_file("simplified_classified_all_classes_sangir_geojson.geojson")

    # Hitung luas (dalam hektar)
    gdf["luas_ha"] = gdf.geometry.to_crs(epsg=3857).area / 10_000

    # Agregasi per kelas
    df_luas = gdf.groupby("class_id")["luas_ha"].sum().reset_index()
    df_luas["kelas"] = df_luas["class_id"].map(class_map)
    df_luas = df_luas[["kelas", "luas_ha"]].sort_values(by="luas_ha", ascending=False)

    # Tampilkan tabel
    st.dataframe(df_luas.style.format({"luas_ha": "{:,.2f} ha"}), use_container_width=True)

    # Tampilkan chart
    st.bar_chart(df_luas.set_index("kelas"))

    # Tombol download CSV
    csv = df_luas.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Luas Kelas (.csv)",
        data=csv,
        file_name="luas_penutup_lahan_sangir.csv",
        mime="text/csv"
    )

except Exception as e:
    st.warning("⚠️ Gagal membaca atau memproses file GeoJSON. Pastikan file bernama `simplified_classified_all_classes_sangir_geojson.geojson` tersedia.")
    st.text(str(e))
