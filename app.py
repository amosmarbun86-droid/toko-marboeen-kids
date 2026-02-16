import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# =====================
# KONFIGURASI
# =====================

st.set_page_config(
    page_title="Toko Marboeen Kids",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"
BACKGROUND = "background.png"


# =====================
# BACKGROUND FULL HP
# =====================

def set_bg():
    if os.path.exists(BACKGROUND):
        with open(BACKGROUND, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .block-container {{
            background: rgba(255,255,255,0.92);
            padding: 20px;
            border-radius: 10px;
        }}

        button {{
            height: 60px;
            font-size: 18px !important;
            font-weight: bold !important;
        }}
        </style>
        """, unsafe_allow_html=True)

set_bg()


# =====================
# LOAD DATA
# =====================

def load_barang():
    if os.path.exists(DATA_BARANG):
        return pd.read_csv(DATA_BARANG)
    else:
        df = pd.DataFrame(columns=[
            "kode","nama","modal","jual","stok","expired"
        ])
        df.to_csv(DATA_BARANG, index=False)
        return df

def load_transaksi():
    if os.path.exists(DATA_TRANSAKSI):
        return pd.read_csv(DATA_TRANSAKSI)
    else:
        df = pd.DataFrame(columns=[
            "tanggal","kode","nama","jumlah","total","profit"
        ])
        df.to_csv(DATA_TRANSAKSI, index=False)
        return df

barang = load_barang()
transaksi = load_transaksi()


# =====================
# NAVIGASI
# =====================

if "page" not in st.session_state:
    st.session_state.page = "Menu"

def go(page):
    st.session_state.page = page
    st.rerun()


# =====================
# MENU UTAMA
# =====================

if st.session_state.page == "Menu":

    st.title("🏪 TOKO MARBOEEN KIDS")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("🧾 KASIR", use_container_width=True):
            go("Kasir")

        if st.button("📦 DATA BARANG", use_container_width=True):
            go("Barang")

    with col2:
        if st.button("📊 GRAFIK PROFIT", use_container_width=True):
            go("Grafik")

        if st.button("📜 TRANSAKSI", use_container_width=True):
            go("Riwayat")


# =====================
# KASIR
# =====================

elif st.session_state.page == "Kasir":

    st.title("🧾 KASIR")

    if barang.empty:
        st.warning("Belum ada barang")
    else:

        pilih = st.selectbox("Pilih Barang", barang["nama"])

        data = barang[barang["nama"]==pilih].iloc[0]

        st.info(f"Harga: {data['jual']} | Stok: {data['stok']}")

        jumlah = st.number_input(
            "Jumlah",
            min_value=1,
            max_value=int(data["stok"]) if data["stok"]>0 else 1,
            value=1
        )

        if st.button("BAYAR", use_container_width=True):

            if data["stok"] >= jumlah:

                total = data["jual"] * jumlah
                profit = (data["jual"] - data["modal"]) * jumlah

                idx = barang.index[barang.nama==pilih][0]
                barang.loc[idx,"stok"] -= jumlah
                barang.to_csv(DATA_BARANG,index=False)

                new = pd.DataFrame([{
                    "tanggal": datetime.now(),
                    "kode": data["kode"],
                    "nama": pilih,
                    "jumlah": jumlah,
                    "total": total,
                    "profit": profit
                }])

                global transaksi
                transaksi = pd.concat([transaksi,new],ignore_index=True)
                transaksi.to_csv(DATA_TRANSAKSI,index=False)

                st.success(f"Berhasil. Total: Rp {total}")

            else:
                st.error("Stok tidak cukup")

    if st.button("⬅ Kembali"):
        go("Menu")


# =====================
# DATA BARANG
# =====================

elif st.session_state.page == "Barang":

    st.title("📦 DATA BARANG")

    st.dataframe(barang, use_container_width=True)

    st.subheader("Tambah Barang")

    kode = st.text_input("Kode")
    nama = st.text_input("Nama")
    modal = st.number_input("Harga Modal",0)
    jual = st.number_input("Harga Jual",0)
    stok = st.number_input("Stok",0)
    expired = st.date_input("Expired")

    if st.button("SIMPAN", use_container_width=True):

        new = pd.DataFrame([{
            "kode":kode,
            "nama":nama,
            "modal":modal,
            "jual":jual,
            "stok":stok,
            "expired":expired
        }])

        barang2 = pd.concat([barang,new],ignore_index=True)
        barang2.to_csv(DATA_BARANG,index=False)

        st.success("Tersimpan")
        st.rerun()

    if st.button("⬅ Kembali"):
        go("Menu")


# =====================
# GRAFIK
# =====================

elif st.session_state.page == "Grafik":

    st.title("📊 PROFIT PER BULAN")

    if transaksi.empty:
        st.warning("Belum ada transaksi")

    else:

        transaksi["tanggal"] = pd.to_datetime(transaksi["tanggal"])
        transaksi["bulan"] = transaksi["tanggal"].dt.strftime("%Y-%m")

        data = transaksi.groupby("bulan")["profit"].sum()

        st.bar_chart(data)

    if st.button("⬅ Kembali"):
        go("Menu")


# =====================
# RIWAYAT
# =====================

elif st.session_state.page == "Riwayat":

    st.title("📜 RIWAYAT TRANSAKSI")

    st.dataframe(transaksi, use_container_width=True)

    if st.button("⬅ Kembali"):
        go("Menu")
