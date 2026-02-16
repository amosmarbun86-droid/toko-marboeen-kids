    import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
import shutil

st.set_page_config(page_title="TOKO MARBOEEN KIDS", layout="wide")

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"

# ================= BACKUP OTOMATIS =================

if not os.path.exists("backup"):
    os.mkdir("backup")

if os.path.exists(DATA_BARANG):
    shutil.copy(DATA_BARANG,"backup/data_barang_backup.csv")

if os.path.exists(DATA_TRANSAKSI):
    shutil.copy(DATA_TRANSAKSI,"backup/transaksi_backup.csv")

# ================= BUAT FILE =================

if not os.path.exists(DATA_BARANG):
    pd.DataFrame(columns=["kode","nama","modal","jual","stok"]).to_csv(DATA_BARANG,index=False)

if not os.path.exists(DATA_TRANSAKSI):
    pd.DataFrame(columns=["tanggal","kode","nama","jumlah","total","profit"]).to_csv(DATA_TRANSAKSI,index=False)

# ================= LOGIN =================

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:

    st.title("🔐 LOGIN ADMIN TOKO MARBOEEN KIDS")

    user=st.text_input("Username")
    pw=st.text_input("Password", type="password")

    if st.button("Login"):

        if user=="admin" and pw=="1234":

            st.session_state.login=True
            st.rerun()

        else:
            st.error("Login salah")

    st.stop()

# ================= LOAD DATA =================

barang=pd.read_csv(DATA_BARANG)
transaksi=pd.read_csv(DATA_TRANSAKSI)

# ================= MENU =================

st.title("🛒 TOKO MARBOEEN KIDS")

menu=st.sidebar.selectbox("Menu",[
    "Dashboard",
    "Tambah Barang",
    "Kasir",
    "Grafik Profit",
    "Export Excel"
])

# ================= DASHBOARD =================

if menu=="Dashboard":

    st.subheader("Stok Barang")
    st.dataframe(barang)

    st.metric("Total Profit", transaksi["profit"].sum())

# ================= TAMBAH BARANG =================

elif menu=="Tambah Barang":

    kode=st.text_input("Kode Barcode / Kode Barang")
    nama=st.text_input("Nama Barang")
    modal=st.number_input("Harga Modal")
    jual=st.number_input("Harga Jual")
    stok=st.number_input("Stok")

    if st.button("Simpan"):

        new=pd.DataFrame([{
            "kode":kode,
            "nama":nama,
            "modal":modal,
            "jual":jual,
            "stok":stok
        }])

        barang=pd.concat([barang,new])
        barang.to_csv(DATA_BARANG,index=False)

        st.success("Barang berhasil ditambahkan")

# ================= KASIR =================

elif menu=="Kasir":

    kode=st.text_input("Scan / Input Kode Barang")

    hasil=barang[barang["kode"]==kode]

    if not hasil.empty:

        nama=hasil.iloc[0]["nama"]
        jual=hasil.iloc[0]["jual"]
        modal=hasil.iloc[0]["modal"]

        st.write("Nama:",nama)
        st.write("Harga:",jual)

        jumlah=st.number_input("Jumlah",1)

        if st.button("Bayar"):

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

            transaksi=pd.concat([transaksi,new])
            transaksi.to_csv(DATA_TRANSAKSI,index=False)

            st.success("Pembayaran berhasil")

            # ================= STRUK PDF =================

            if not os.path.exists("struk"):
                os.mkdir("struk")

            file="struk/struk.pdf"

            c=canvas.Canvas(file)

            c.drawString(100,750,"TOKO MARBOEEN KIDS")
            c.drawString(100,720,f"Tanggal: {datetime.now()}")
            c.drawString(100,690,f"Barang: {nama}")
            c.drawString(100,660,f"Jumlah: {jumlah}")
            c.drawString(100,630,f"Total: {total}")

            c.save()

            with open(file,"rb") as f:

                st.download_button(
                    "Download Struk PDF",
                    f,
                    file_name="struk.pdf"
                )

# ================= GRAFIK =================

elif menu=="Grafik Profit":

    transaksi["tanggal"]=pd.to_datetime(transaksi["tanggal"])

    transaksi["bulan"]=transaksi["tanggal"].dt.month

    data=transaksi.groupby("bulan")["profit"].sum()

    st.bar_chart(data)

# ================= EXPORT =================

elif menu=="Export Excel":

    file="transaksi.xlsx"

    transaksi.to_excel(file,index=False)

    with open(file,"rb") as f:

        st.download_button(
            "Download Excel",
            f,
            file_name=file
        )
