import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="TOKO MARBOEEN KIDS", layout="wide")

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"

# Buat file jika belum ada
if not os.path.exists(DATA_BARANG):
    pd.DataFrame(columns=["kode","nama","modal","jual","stok"]).to_csv(DATA_BARANG,index=False)

if not os.path.exists(DATA_TRANSAKSI):
    pd.DataFrame(columns=["tanggal","nama","jumlah","total","profit"]).to_csv(DATA_TRANSAKSI,index=False)

# LOGIN
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Login Admin")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user=="admin" and pw=="1234":
            st.session_state.login=True
            st.rerun()
        else:
            st.error("Login salah")

    st.stop()

# LOAD DATA
barang = pd.read_csv(DATA_BARANG)
transaksi = pd.read_csv(DATA_TRANSAKSI)

st.title("🛒 TOKO MARBOEEN KIDS")

menu = st.sidebar.selectbox("Menu",[
    "Dashboard",
    "Tambah Barang",
    "Kasir",
    "Grafik Profit",
    "Export Excel"
])

# DASHBOARD
if menu=="Dashboard":
    st.dataframe(barang)
    st.metric("Total Profit", transaksi["profit"].sum())

# TAMBAH BARANG
elif menu=="Tambah Barang":
    kode = st.text_input("Kode")
    nama = st.text_input("Nama")
    modal = st.number_input("Harga Modal")
    jual = st.number_input("Harga Jual")
    stok = st.number_input("Stok")

    if st.button("Simpan"):
        new = pd.DataFrame([{
            "kode":kode,
            "nama":nama,
            "modal":modal,
            "jual":jual,
            "stok":stok
        }])
        barang = pd.concat([barang,new])
        barang.to_csv(DATA_BARANG,index=False)
        st.success("Barang ditambahkan")

# KASIR
elif menu=="Kasir":
    pilih = st.selectbox("Pilih Barang", barang["nama"])
    jumlah = st.number_input("Jumlah",1)

    if st.button("Bayar"):
        idx = barang.index[barang.nama==pilih][0]
        jual = barang.loc[idx,"jual"]
        modal = barang.loc[idx,"modal"]
        total = jual*jumlah
        profit = (jual-modal)*jumlah

        barang.loc[idx,"stok"] -= jumlah
        barang.to_csv(DATA_BARANG,index=False)

        new = pd.DataFrame([{
            "tanggal":datetime.now(),
            "nama":pilih,
            "jumlah":jumlah,
            "total":total,
            "profit":profit
        }])

        transaksi = pd.concat([transaksi,new])
        transaksi.to_csv(DATA_TRANSAKSI,index=False)

        st.success("Transaksi berhasil")

# GRAFIK
elif menu=="Grafik Profit":
    transaksi["tanggal"]=pd.to_datetime(transaksi["tanggal"])
    transaksi["bulan"]=transaksi["tanggal"].dt.month
    data = transaksi.groupby("bulan")["profit"].sum()
    st.bar_chart(data)

# EXPORT
elif menu=="Export Excel":
    file="transaksi.xlsx"
    transaksi.to_excel(file,index=False)
    with open(file,"rb") as f:
        st.download_button("Download Excel",f,file_name=file)
