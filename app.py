import json
import ee
import streamlit as st
import folium
import geopandas as gpd
import plotly.express as px
from streamlit_folium import st_folium

# → Inisialisasi Earth Engine
try:
    service_account_str = st.secrets["SERVICE_ACCOUNT_JSON"]
    service_account_info = json.loads(service_account_str)
    credentials = ee.ServiceAccountCredentials(
        service_account_info["client_email"],
        key_data=service_account_str
    )
    ee.Initialize(credentials)
except Exception as e:
    st.error(f"❌ Gagal inisialisasi Earth Engine:\n\n{e}")
    st.stop()

# → Fungsi tambah layer EE ke folium
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

# → Tampilkan Peta
st.markdown("### 🌍 Peta Klasifikasi Kecamatan Sangir RGB")
ASSET_ID = "projects/ee-mrgridhoarazzak/assets/Klasifikasi_Sangir_2024_aset_asli"
vis_params = {"bands": ["vis-red", "vis-green", "vis-blue"], "min": 0, "max": 255}

try:
    image = ee.Image(ASSET_ID)
    m = folium.Map(location=[-1.5269, 101.3002], zoom_start=10)
    m.add_ee_layer(image, vis_params, "Klasifikasi RGB")
    folium.LayerControl().add_to(m)
    st_folium(m, width=700, height=500)
except Exception as e:
    st.error(f"❌ Gagal menampilkan peta:\n\n{e}")

# → Hitung dan Visualisasikan Luas per Kelas
st.subheader("📊 Luas Penutup Lahan per Kelas")

GEOJSON_URL = "https://raw.githubusercontent.com/ridhoarazzak/test/main/simplified_classified_all_classes_sangir_geojson.geojson"

try:
    gdf = gpd.read_file(GEOJSON_URL)

    if gdf.empty:
        st.warning("⚠️ GeoJSON berhasil dimuat tapi tidak ada data (kosong).")
        st.stop()

    if "class" not in gdf.columns:
        st.error("❌ Kolom 'class' tidak ditemukan dalam GeoJSON.")
        st.stop()

    # 1. Map class_id ke nama kelas
    class_map = {
        0: "Hutan",
        1: "Pertanian",
        2: "Permukiman",
        3: "Air"
    }

    # 2. Warna RGB peta (harus cocok dengan warna layer di peta)
    color_map = {
        "Hutan": "#008000",        # Hijau
        "Pertanian": "#FFFF00",    # Kuning
        "Permukiman": "#FF0000",   # Merah
        "Air": "#0000FF"           # Biru
    }

    # 3. Hitung luas dalam hektar
    gdf["luas_ha"] = gdf.geometry.to_crs(epsg=3857).area / 10_000

    # 4. Agregasi dan pemetaan
    df_luas = gdf.groupby("class")["luas_ha"].sum().reset_index()
    df_luas["kelas"] = df_luas["class"].map(class_map).fillna("Lainnya")
    df_luas["warna"] = df_luas["kelas"].map(color_map).fillna("#888888")
    df_luas = df_luas[["kelas", "luas_ha", "warna"]].sort_values(by="luas_ha", ascending=False)

    # 5. Tampilkan tabel
    st.dataframe(df_luas.style.format({"luas_ha": "{:,.2f} ha"}), use_container_width=True)

    # 6. Bar chart dengan warna sesuai RGB
    fig = px.bar(
        df_luas,
        x="kelas",
        y="luas_ha",
        title="Luas Lahan per Kelas (hektar)",
        labels={"kelas": "Kelas", "luas_ha": "Luas (ha)"},
        color="kelas",
        color_discrete_map=color_map,
        text_auto=".2s",
        height=400
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # 7. Tombol download
    csv = df_luas[["kelas", "luas_ha"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Data Luas per Kelas",
        data=csv,
        file_name="luas_per_kelas_sangir.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("❌ Gagal memproses GeoJSON dari URL.")
    st.text(str(e))
