import json
import ee
import streamlit as st
import folium  # ⬅️ ini yang kurang
import geopandas as gpd
import os
from streamlit_folium import st_folium


try:
    # Ambil string JSON dari st.secrets
    service_account_str = st.secrets["SERVICE_ACCOUNT_JSON"]

    # Ubah string JSON jadi dict → untuk ambil email
    service_account_info = json.loads(service_account_str)

    # Inisialisasi kredensial GEE
    credentials = ee.ServiceAccountCredentials(
        service_account_info["client_email"],
        key_data=service_account_str  # harus STRING, bukan dict!
    )
    ee.Initialize(credentials)

except Exception as e:
    st.error(f"❌ Gagal inisialisasi Earth Engine:\n\n{e}")
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
        st.error(f"❌ Gagal menambahkan layer EE:\n\n{e}")

folium.Map.add_ee_layer = add_ee_layer

# === Tampilkan Peta EE ===
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"
vis_params = {
    "bands": ["vis-red", "vis-green", "vis-blue"],
    "min": 0,
    "max": 255
}

st.markdown("Visualisasi RGB dari citra klasifikasi Google Earth Engine")

try:
    image = ee.Image(ASSET_ID)
    band_names = image.bandNames().getInfo()
    st.write("📌 Band citra:", band_names)

    m = folium.Map(location=[-1.5269, 101.3002], zoom_start=10)
    m.add_ee_layer(image, vis_params, "Klasifikasi RGB")
    folium.LayerControl().add_to(m)

    st_folium(m, width=700, height=500)
except Exception as e:
    st.error(f"❌ Gagal menampilkan data peta:\n\n{e}")

# === Analisis Luas Penutup Lahan ===
st.subheader("📊 Luas Kelas Penutup Lahan")

# Mapping ID kelas ke label
class_map = {
    0: "Hutan",
    1: "Pertanian",
    2: "Permukiman",
    3: "Air"
}

# Upload file GeoJSON jika tidak ada
geojson_path = "simplified_classified_all_classes_sangir_geojson.geojson"
uploaded = None

if not os.path.exists(geojson_path):
    uploaded = st.file_uploader("📂 Upload file GeoJSON klasifikasi:", type=["geojson"])
    if uploaded:
        with open(geojson_path, "wb") as f:
            f.write(uploaded.read())

if os.path.exists(geojson_path):
    try:
        gdf = gpd.read_file(geojson_path)

        # Hitung luas dalam hektar
        gdf["luas_ha"] = gdf.geometry.to_crs(epsg=3857).area / 10_000

        # Kelompokkan berdasarkan class_id
        df_luas = gdf.groupby("class_id")["luas_ha"].sum().reset_index()
        df_luas["kelas"] = df_luas["class_id"].map(class_map)
        df_luas = df_luas[["kelas", "luas_ha"]].sort_values(by="luas_ha", ascending=False)

        st.dataframe(df_luas.style.format({"luas_ha": "{:,.2f} ha"}), use_container_width=True)
        st.bar_chart(df_luas.set_index("kelas"))

        # Tombol Download CSV
        csv = df_luas.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Luas Kelas (.csv)",
            data=csv,
            file_name="luas_penutup_lahan_sangir.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.warning("⚠️ Gagal memproses GeoJSON:")
        st.text(str(e))
else:
    st.info("📎 Belum ada file GeoJSON. Upload file terlebih dahulu.")
