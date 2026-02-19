import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ======================
# KONFIGURASI UI MODERN
# ======================

st.set_page_config(
    page_title="Moka POS — Marboeen",
    layout="wide"
)

# ===== CSS MODERN =====
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
button {height:60px;font-size:18px;}
[data-testid="stSidebar"] {background:#111;color:white;}
</style>
""", unsafe_allow_html=True)


# ======================
# FILE DATA (PAKAI FILE LAMA)
# ======================

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"


def load_barang():
    if os.path.exists(DATA_BARANG):
        return pd.read_csv(DATA_BARANG)
    return pd.DataFrame(columns=["kode","nama","modal","jual","stok","expired"])


def load_transaksi():
    if os.path.exists(DATA_TRANSAKSI):
        return pd.read_csv(DATA_TRANSAKSI)
    return pd.DataFrame(columns=["tanggal","kode","nama","jumlah","total","profit"])


barang = load_barang()
transaksi = load_transaksi()


# ======================
# SESSION
# ======================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "page" not in st.session_state:
    st.session_state.page = "Kasir"


# ======================
# SIDEBAR MENU (MOKA STYLE)
# ======================

st.sidebar.title("🏪 MARBOEEN POS")

menu = st.sidebar.radio(
    "Menu",
    ["Kasir","Barang","Riwayat","Grafik","Pengaturan"]
)

st.session_state.page = menu


# ======================
# 🧾 HALAMAN KASIR
# ======================

if menu == "Kasir":

    st.title("🧾 KASIR")

    if barang.empty:
        st.warning("Belum ada barang")
        st.stop()

    col1, col2 = st.columns([2,1])

    # ===== PILIH BARANG =====
    with col1:

        pilih = st.selectbox("Pilih Produk", barang["nama"])
        data = barang[barang["nama"] == pilih].iloc[0]

        jumlah = st.number_input(
            "Jumlah",
            1,
            int(data["stok"]) if data["stok"] > 0 else 1,
            1
        )

        if st.button("➕ Tambah ke Keranjang", use_container_width=True):

            st.session_state.cart.append({
                "kode": data["kode"],
                "nama": data["nama"],
                "modal": data["modal"],
                "jual": data["jual"],
                "jumlah": jumlah
            })

            st.success("Ditambahkan")

    # ===== KERANJANG =====
    with col2:

        st.subheader("🛒 Keranjang")

        total = 0

        if st.session_state.cart:

            for i,item in enumerate(st.session_state.cart):

                subtotal = item["jual"] * item["jumlah"]
                total += subtotal

                c1,c2 = st.columns([3,1])

                c1.write(f"{item['nama']} x {item['jumlah']}")
                if c2.button("❌", key=i):
                    st.session_state.cart.pop(i)
                    st.rerun()

            st.markdown(f"# Rp {total:,}")

            if st.button("💰 BAYAR", use_container_width=True):

                for item in st.session_state.cart:

                    idx = barang.index[barang.kode == item["kode"]][0]
                    barang.loc[idx,"stok"] -= item["jumlah"]

                    new = pd.DataFrame([{
                        "tanggal": datetime.now(),
                        "kode": item["kode"],
                        "nama": item["nama"],
                        "jumlah": item["jumlah"],
                        "total": item["jual"] * item["jumlah"],
                        "profit": (item["jual"] - item["modal"]) * item["jumlah"]
                    }])

                    transaksi = pd.concat([transaksi,new],ignore_index=True)

                barang.to_csv(DATA_BARANG,index=False)
                transaksi.to_csv(DATA_TRANSAKSI,index=False)

                st.session_state.cart = []

                st.success("Transaksi berhasil ✅")

                struk = f"""
TOKO MARBOEEN
================
TOTAL : Rp {total}
Terima kasih 🙏
"""

                encoded = urllib.parse.quote(struk)
                url = f"rawbt://print?text={encoded}"

                st.markdown(
                    f'<a href="{url}">🖨️ CETAK STRUK</a>',
                    unsafe_allow_html=True
                )

        else:
            st.info("Keranjang kosong")


# ======================
# 📦 DATA BARANG
# ======================

elif menu == "Barang":

    st.title("📦 DATA BARANG")

    st.dataframe(barang, use_container_width=True)

    st.subheader("Tambah Barang")

    kode = st.text_input("Kode")
    nama = st.text_input("Nama")
    modal = st.number_input("Modal",0)
    jual = st.number_input("Harga Jual",0)
    stok = st.number_input("Stok",0)
    expired = st.date_input("Expired")

    if st.button("💾 Simpan"):

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

        st.success("Barang tersimpan")


# ======================
# 📜 RIWAYAT
# ======================

elif menu == "Riwayat":

    st.title("📜 Riwayat Transaksi")
    st.dataframe(transaksi, use_container_width=True)


# ======================
# 📊 GRAFIK
# ======================

elif menu == "Grafik":

    st.title("📊 Grafik Profit")

    if not transaksi.empty:

        transaksi["tanggal"] = pd.to_datetime(transaksi["tanggal"])
        transaksi["bulan"] = transaksi["tanggal"].dt.strftime("%Y-%m")

        data = transaksi.groupby("bulan")["profit"].sum()

        st.bar_chart(data)


# ======================
# ⚙️ PENGATURAN / NOTIFIKASI
# ======================

elif menu == "Pengaturan":

    st.title("⚙️ Pengaturan")

    habis = barang[barang["stok"] <= 0]
    menipis = barang[(barang["stok"] > 0) & (barang["stok"] <= 5)]

    if not habis.empty:
        st.error("⚠️ STOK HABIS")
        st.dataframe(habis[["nama","stok"]])

    if not menipis.empty:
        st.warning("⚠️ Stok hampir habis")
