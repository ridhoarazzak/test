import streamlit as st
import folium
from streamlit_folium import st_folium
import ee
import pandas as pd
import altair as alt
import json
import os

# === Inisialisasi Earth Engine ===
try:
    SERVICE_ACCOUNT = "razza-earth-engine-2025@ee-mrgridhoarazzak.iam.gserviceaccount.com"
    KEY_PATH = "service_account.json"
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)
except Exception as e:
    st.error("❌ Gagal inisialisasi Earth Engine: %s" % e)
    st.stop()

# === Fungsi bantu untuk menambah layer EE ke folium ===
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

# === UI Streamlit ===
st.set_page_config(layout="wide")
st.title("🌍 Peta Klasifikasi Penutupan Lahan Wilayah Sangir")
st.markdown("Visualisasi RGB dan Luas Tiap Kelas Berdasarkan Google Earth Engine")

# === Load asset klasifikasi dari GEE ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"
vis_params = {
    "bands": ["vis-red", "vis-green", "vis-blue"],
    "min": 0,
    "max": 255
}

try:
    image = ee.Image(ASSET_ID)

    # === Load file GeoJSON lokal atau dari subfolder 'data/' ===
    geojson_path = "data/simplified_classified_all_classes_sangir.geojson"
    if not os.path.exists(geojson_path):
        st.error(f"❌ File GeoJSON tidak ditemukan: {geojson_path}")
        st.stop()

    with open(geojson_path, "r") as f:
        geojson_data = json.load(f)

    feature = ee.FeatureCollection(geojson_data)

    # === Reduce region untuk menghitung jumlah pixel per kelas
    class_stats = image.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=feature.geometry(),
        scale=30,
        maxPixels=1e13
    )

    hist = class_stats.getInfo()
    pixel_counts = hist.get('classification') or {}

    # === Mapping angka ke nama kelas ===
    kelas_dict = {
        "0": "Hutan",
        "1": "Pertanian",
        "2": "Permukiman",
        "3": "Air"
    }

    # === Konversi hasil ke dataframe ===
    hasil = []
    for kelas, jumlah in pixel_counts.items():
        kelas_nama = kelas_dict.get(str(kelas), f"Unknown ({kelas})")
        luas_ha = jumlah * 30 * 30 / 10000  # m2 ke hektar
        hasil.append({
            "Kelas": kelas_nama,
            "Luas (Ha)": round(luas_ha, 2)
        })

    df = pd.DataFrame(hasil).sort_values("Kelas")

    # === Peta ===
    m = folium.Map(location=[-1.5269, 101.3002], zoom_start=10)
    m.add_ee_layer(image, vis_params, "RGB Image")
    folium.GeoJson(geojson_data, name="Wilayah Sangir").add_to(m)
    folium.LayerControl().add_to(m)
    st_folium(m, width=700, height=500)

    # === Chart dan tabel ===
    st.subheader("📊 Luas Tutupan Lahan per Kelas (ha)")
    st.dataframe(df)

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Kelas:N", title="Kelas"),
        y=alt.Y("Luas (Ha):Q", title="Luas (hektar)"),
        tooltip=["Kelas", "Luas (Ha)"]
    ).properties(title="Luas Tutupan Lahan per Kelas")
    st.altair_chart(chart, use_container_width=True)

    # === Tombol Download CSV ===
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV Luas Kelas",
        data=csv,
        file_name="luas_tutupan_per_kelas.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"❌ Terjadi kesalahan: {e}")
