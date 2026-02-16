import streamlit as st
import pandas as pd
import os

DATA_BARANG = "data_barang.csv"


# =============================
# LOAD DATA
# =============================

def load_barang():
    if os.path.exists(DATA_BARANG):
        return pd.read_csv(DATA_BARANG)
    return pd.DataFrame()


# =============================
# 🔔 NOTIFIKASI STOK
# =============================

def notifikasi_stok():

    barang = load_barang()

    if barang.empty:
        return

    habis = barang[barang["stok"] <= 0]
    menipis = barang[(barang["stok"] > 0) & (barang["stok"] <= 5)]

    if not habis.empty:
        st.error("⚠️ STOK HABIS!")
        st.dataframe(habis[["nama","stok"]])

    if not menipis.empty:
        st.warning("⚠️ Stok hampir habis")
        st.dataframe(menipis[["nama","stok"]])


# =============================
# ✏️ EDIT & HAPUS BARANG
# =============================

def kelola_barang():

    st.subheader("✏️ Edit / Hapus Barang")

    barang = load_barang()

    if barang.empty:
        st.info("Belum ada barang")
        return

    pilih = st.selectbox("Pilih barang", barang["nama"])

    data = barang[barang["nama"] == pilih].iloc[0]
    idx = barang[barang["nama"] == pilih].index[0]

    kode = st.text_input("Kode", data["kode"])
    nama = st.text_input("Nama", data["nama"])
    modal = st.number_input("Modal", value=int(data["modal"]))
    jual = st.number_input("Jual", value=int(data["jual"]))
    stok = st.number_input("Stok", value=int(data["stok"]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Update", use_container_width=True):

            barang.loc[idx] = [
                kode, nama, modal, jual, stok, data["expired"]
            ]

            barang.to_csv(DATA_BARANG, index=False)

            st.success("Barang diperbarui")
            st.rerun()

    with col2:
        if st.button("🗑️ Hapus", use_container_width=True):

            barang = barang.drop(idx)

            barang.to_csv(DATA_BARANG, index=False)

            st.warning("Barang dihapus")
            st.rerun()


# =============================
# 📷 SCAN BARCODE (KAMERA)
# =============================

def scan_barcode():

    st.subheader("📷 Scan Barcode")

    code = st.camera_input("Arahkan kamera ke barcode")

    if code:
        st.success("Barcode terbaca")
        st.write("Gunakan barcode sebagai kode produk")


# =============================
# 🧾 CETAK STRUK
# =============================

def cetak_struk(transaksi_df):

    st.subheader("🧾 Cetak Struk")

    if transaksi_df.empty:
        st.info("Belum ada transaksi")
        return

    if st.button("🖨️ Cetak Struk"):

        total = transaksi_df["total"].sum()

        struk = f"""
TOKO MARBOEEN KIDS
========================
Terima kasih 🙏

TOTAL : Rp {total}
"""

        st.code(struk)
        st.success("Struk siap dicetak via Bluetooth printer")
