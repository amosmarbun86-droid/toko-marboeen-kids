import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
import shutil
import base64

# ================= CONFIG =================

st.set_page_config(
    page_title="TOKO MARBOEEN KIDS",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= BACKGROUND =================

def set_bg():
    if os.path.exists("bg.png"):
        with open("bg.png","rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        header {{visibility:hidden;}}
        footer {{visibility:hidden;}}

        .block-container {{
            padding:15px;
        }}

        .menu-btn {{
            background: linear-gradient(90deg,#ff0000,#ff9900);
            color:white;
            padding:15px;
            border-radius:12px;
            text-align:center;
            font-size:18px;
            font-weight:bold;
            margin-bottom:10px;
        }}

        </style>
        """, unsafe_allow_html=True)

set_bg()

# ================= FILE =================

DATA_BARANG="data_barang.csv"
DATA_TRANSAKSI="transaksi.csv"

if not os.path.exists(DATA_BARANG):
    pd.DataFrame(columns=["kode","nama","modal","jual","stok","expired"]).to_csv(DATA_BARANG,index=False)

if not os.path.exists(DATA_TRANSAKSI):
    pd.DataFrame(columns=["tanggal","kode","nama","jumlah","total","profit"]).to_csv(DATA_TRANSAKSI,index=False)

barang=pd.read_csv(DATA_BARANG)
transaksi=pd.read_csv(DATA_TRANSAKSI)

# ================= LOGIN =================

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:

    st.title("🔐 LOGIN ADMIN")
    user=st.text_input("Username")
    pw=st.text_input("Password",type="password")

    if st.button("Login"):
        if user=="admin" and pw=="1234":
            st.session_state.login=True
            st.rerun()
        else:
            st.error("Login salah")

    st.stop()

# ================= NAVIGATION =================

if "page" not in st.session_state:
    st.session_state.page="Menu"

def go(page):
    st.session_state.page=page

# ================= MENU UTAMA =================

if st.session_state.page=="Menu":

    st.markdown("## 🛒 TOKO MARBOEEN KIDS")

    if st.button("🛒 KASIR",use_container_width=True):
        go("Kasir")

    if st.button("📦 DATA BARANG",use_container_width=True):
        go("Barang")

    if st.button("📊 LAPORAN PROFIT",use_container_width=True):
        go("Grafik")

    if st.button("📥 EXPORT EXCEL",use_container_width=True):
        go("Export")

    if st.button("🚪 LOGOUT",use_container_width=True):
        st.session_state.login=False
        st.rerun()

# ================= DATA BARANG =================

elif st.session_state.page=="Barang":

    st.title("📦 DATA BARANG")

    st.dataframe(barang,use_container_width=True)

    if st.button("⬅ Kembali"):
        go("Menu")

# ================= KASIR =================

elif st.session_state.page=="Kasir":

    st.title("🧾 KASIR")

    kode=st.text_input("Scan / Input Kode")

    hasil=barang[barang["kode"]==kode]

    if not hasil.empty:

        nama=hasil.iloc[0]["nama"]
        jual=hasil.iloc[0]["jual"]
        modal=hasil.iloc[0]["modal"]
        stok=hasil.iloc[0]["stok"]

        st.info(f"{nama} | Harga: {jual} | Stok: {stok}")

        jumlah=st.number_input("Jumlah",1)

        if st.button("Bayar"):

            if jumlah>stok:
                st.error("Stok tidak cukup")
            else:
                total=jual*jumlah
                profit=(jual-modal)*jumlah

                idx=barang.index[barang.kode==kode][0]
                barang.loc[idx,"stok"]-=jumlah
                barang.to_csv(DATA_BARANG,index=False)

                new=pd.DataFrame([{
                    "tanggal":datetime.now(),
                    "kode":kode,
                    "nama":nama,
                    "jumlah":jumlah,
                    "total":total,
                    "profit":profit
                }])

                transaksi=pd.concat([transaksi,new],ignore_index=True)
                transaksi.to_csv(DATA_TRANSAKSI,index=False)

                st.success("Transaksi berhasil")

    if st.button("⬅ Kembali"):
        go("Menu")

# ================= GRAFIK =================

elif st.session_state.page=="Grafik":

    st.title("📊 PROFIT PER BULAN")

    if not transaksi.empty:
        transaksi["tanggal"]=pd.to_datetime(transaksi["tanggal"])
        transaksi["bulan"]=transaksi["tanggal"].dt.strftime("%Y-%m")
        data=transaksi.groupby("bulan")["profit"].sum()
        st.bar_chart(data)

    if st.button("⬅ Kembali"):
        go("Menu")

# ================= EXPORT =================

elif st.session_state.page=="Export":

    file="laporan.xlsx"
    transaksi.to_excel(file,index=False)

    with open(file,"rb") as f:
        st.download_button("Download Excel",f,file_name=file)

    if st.button("⬅ Kembali"):
        go("Menu")
