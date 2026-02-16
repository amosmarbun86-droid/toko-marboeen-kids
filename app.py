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
            padding: 15px;
        }}

        .card {{
            background-color: rgba(255,255,255,0.95);
            padding:15px;
            border-radius:15px;
            box-shadow:0px 4px 10px rgba(0,0,0,0.2);
        }}

        .title {{
            background: linear-gradient(90deg,#ff0000,#ff9900);
            padding:15px;
            border-radius:10px;
            color:white;
            text-align:center;
            font-size:28px;
            font-weight:bold;
        }}

        </style>
        """, unsafe_allow_html=True)

set_bg()

# ================= FILE =================

DATA_BARANG="data_barang.csv"
DATA_TRANSAKSI="transaksi.csv"

if not os.path.exists("backup"):
    os.mkdir("backup")

if os.path.exists(DATA_BARANG):
    shutil.copy(DATA_BARANG,"backup/data_barang_backup.csv")

if os.path.exists(DATA_TRANSAKSI):
    shutil.copy(DATA_TRANSAKSI,"backup/transaksi_backup.csv")

if not os.path.exists(DATA_BARANG):
    pd.DataFrame(columns=["kode","nama","modal","jual","stok","expired"]).to_csv(DATA_BARANG,index=False)

if not os.path.exists(DATA_TRANSAKSI):
    pd.DataFrame(columns=["tanggal","kode","nama","jumlah","total","profit"]).to_csv(DATA_TRANSAKSI,index=False)

# ================= LOGIN =================

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:

    st.markdown('<div class="title">🔐 LOGIN ADMIN</div>', unsafe_allow_html=True)

    user=st.text_input("Username")
    pw=st.text_input("Password",type="password")

    if st.button("Login"):
        if user=="admin" and pw=="1234":
            st.session_state.login=True
            st.rerun()
        else:
            st.error("Login salah")

    st.stop()

# ================= LOAD =================

barang=pd.read_csv(DATA_BARANG)
transaksi=pd.read_csv(DATA_TRANSAKSI)

# ================= HEADER =================

st.markdown('<div class="title">🛒 TOKO MARBOEEN KIDS</div>', unsafe_allow_html=True)

menu=st.sidebar.selectbox("MENU",[
    "Dashboard",
    "Tambah Barang",
    "Kasir",
    "Barang Expired",
    "Grafik Profit",
    "Export Excel"
])

# ================= DASHBOARD =================

if menu=="Dashboard":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    total_barang=len(barang)
    total_stok=barang["stok"].sum() if not barang.empty else 0
    total_profit=transaksi["profit"].sum() if not transaksi.empty else 0

    col1,col2,col3=st.columns(3)
    col1.metric("Jumlah Barang",total_barang)
    col2.metric("Total Stok",total_stok)
    col3.metric("Total Profit",total_profit)

    st.dataframe(barang,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAMBAH =================

elif menu=="Tambah Barang":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    kode=st.text_input("Kode")
    nama=st.text_input("Nama")
    modal=st.number_input("Modal",0)
    jual=st.number_input("Jual",0)
    stok=st.number_input("Stok",0)
    expired=st.date_input("Expired")

    if st.button("Simpan"):
        new=pd.DataFrame([{
            "kode":kode,"nama":nama,"modal":modal,
            "jual":jual,"stok":stok,"expired":expired
        }])
        barang=pd.concat([barang,new],ignore_index=True)
        barang.to_csv(DATA_BARANG,index=False)
        st.success("Berhasil")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= KASIR =================

elif menu=="Kasir":

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

# ================= EXPIRED =================

elif menu=="Barang Expired":

    if not barang.empty:
        barang["expired"]=pd.to_datetime(barang["expired"])
        expired=barang[barang["expired"]<datetime.now()]
        st.dataframe(expired)

# ================= GRAFIK =================

elif menu=="Grafik Profit":

    if not transaksi.empty:
        transaksi["tanggal"]=pd.to_datetime(transaksi["tanggal"])
        transaksi["bulan"]=transaksi["tanggal"].dt.strftime("%Y-%m")
        data=transaksi.groupby("bulan")["profit"].sum()
        st.bar_chart(data)

# ================= EXPORT =================

elif menu=="Export Excel":

    file="laporan.xlsx"
    transaksi.to_excel(file,index=False)

    with open(file,"rb") as f:
        st.download_button("Download Excel",f,file_name=file)
