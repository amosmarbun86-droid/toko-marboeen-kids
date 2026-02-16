import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
import shutil

st.set_page_config(
    page_title="TOKO MARBOEEN KIDS",
    page_icon="🛒",
    layout="wide"
)

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"

# ================= BACKUP =================

if not os.path.exists("backup"):
    os.mkdir("backup")

if os.path.exists(DATA_BARANG):
    shutil.copy(DATA_BARANG,"backup/data_barang_backup.csv")

if os.path.exists(DATA_TRANSAKSI):
    shutil.copy(DATA_TRANSAKSI,"backup/transaksi_backup.csv")

# ================= BUAT FILE =================

if not os.path.exists(DATA_BARANG):
    pd.DataFrame(columns=[
        "kode","nama","modal","jual","stok","expired"
    ]).to_csv(DATA_BARANG,index=False)

if not os.path.exists(DATA_TRANSAKSI):
    pd.DataFrame(columns=[
        "tanggal","kode","nama","jumlah","total","profit"
    ]).to_csv(DATA_TRANSAKSI,index=False)

# ================= LOGIN =================

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:

    st.title("🔐 LOGIN ADMIN")
    st.subheader("TOKO MARBOEEN KIDS")

    user=st.text_input("Username")
    pw=st.text_input("Password", type="password")

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

# ================= MENU =================

st.title("🛒 TOKO MARBOEEN KIDS")

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

    st.subheader("📊 Dashboard")

    total_barang=len(barang)

    total_stok=0
    if not barang.empty:
        total_stok=barang["stok"].sum()

    total_profit=0
    if not transaksi.empty:
        total_profit=transaksi["profit"].sum()

    col1,col2,col3=st.columns(3)

    col1.metric("Jumlah Barang",total_barang)
    col2.metric("Total Stok",total_stok)
    col3.metric("Total Profit",total_profit)

    st.subheader("Data Barang")
    st.dataframe(barang,use_container_width=True)

# ================= TAMBAH =================

elif menu=="Tambah Barang":

    st.subheader("Tambah Barang")

    kode=st.text_input("Kode Barang")
    nama=st.text_input("Nama Barang")
    modal=st.number_input("Harga Modal",0)
    jual=st.number_input("Harga Jual",0)
    stok=st.number_input("Stok",0)
    expired=st.date_input("Tanggal Expired")

    if st.button("Simpan"):

        new=pd.DataFrame([{
            "kode":kode,
            "nama":nama,
            "modal":modal,
            "jual":jual,
            "stok":stok,
            "expired":expired
        }])

        barang=pd.concat([barang,new],ignore_index=True)
        barang.to_csv(DATA_BARANG,index=False)

        st.success("Barang disimpan")

# ================= KASIR =================

elif menu=="Kasir":

    st.subheader("🧾 Kasir")

    kode=st.text_input("Scan / Input Kode")

    hasil=barang[barang["kode"]==kode]

    if not hasil.empty:

        nama=hasil.iloc[0]["nama"]
        jual=hasil.iloc[0]["jual"]
        modal=hasil.iloc[0]["modal"]
        stok=hasil.iloc[0]["stok"]

        st.info(f"Barang: {nama}")
        st.info(f"Harga: {jual}")
        st.info(f"Stok: {stok}")

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

                # STRUK PDF

                if not os.path.exists("struk"):
                    os.mkdir("struk")

                file=f"struk/struk_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

                c=canvas.Canvas(file)

                c.drawString(100,750,"TOKO MARBOEEN KIDS")
                c.drawString(100,720,str(datetime.now()))
                c.drawString(100,690,nama)
                c.drawString(100,660,f"Jumlah: {jumlah}")
                c.drawString(100,630,f"Total: {total}")

                c.save()

                with open(file,"rb") as f:

                    st.download_button(
                        "Download Struk",
                        f,
                        file_name="struk.pdf"
                    )

# ================= EXPIRED =================

elif menu=="Barang Expired":

    if not barang.empty:

        barang["expired"]=pd.to_datetime(barang["expired"])

        expired=barang[
            barang["expired"]<datetime.now()
        ]

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

        st.download_button(
            "Download Excel",
            f,
            file_name=file
        )
