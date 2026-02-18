import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ======================
# FILE DATA LAMA (TIDAK DIUBAH)
# ======================

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"


# ======================
# LOAD DATA
# ======================

def load_barang():
    if os.path.exists(DATA_BARANG):
        return pd.read_csv(DATA_BARANG)
    return pd.DataFrame()

def load_transaksi():
    if os.path.exists(DATA_TRANSAKSI):
        return pd.read_csv(DATA_TRANSAKSI)
    return pd.DataFrame()

barang = load_barang()
transaksi = load_transaksi()


# ======================
# SESSION
# ======================

if "cart" not in st.session_state:
    st.session_state.cart = []


# ======================
# HEADER
# ======================

st.title("🏪 POS MARBOEEN KIDS — PRO")

# ======================
# 🔔 NOTIFIKASI STOK
# ======================

if not barang.empty:

    habis = barang[barang["stok"] <= 0]
    menipis = barang[(barang["stok"] > 0) & (barang["stok"] <= 5)]

    if not habis.empty:
        st.error("⚠️ STOK HABIS!")
        st.dataframe(habis[["nama","stok"]])

    if not menipis.empty:
        st.warning("⚠️ Stok hampir habis")


# ======================
# 🧾 PILIH BARANG
# ======================

if barang.empty:
    st.warning("Belum ada barang")
    st.stop()

pilih = st.selectbox("Pilih Barang", barang["nama"])
data = barang[barang["nama"] == pilih].iloc[0]

st.info(f"Harga: {data['jual']} | Stok: {data['stok']}")

jumlah = st.number_input(
    "Jumlah",
    min_value=1,
    max_value=int(data["stok"]) if data["stok"] > 0 else 1,
    value=1
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


# ======================
# 🛒 KERANJANG
# ======================

st.divider()
st.subheader("🛒 Keranjang")

total = 0

if st.session_state.cart:

    for i, item in enumerate(st.session_state.cart):

        subtotal = item["jual"] * item["jumlah"]
        total += subtotal

        col1, col2 = st.columns([4,1])

        col1.write(f"{item['nama']} x {item['jumlah']} = Rp {subtotal}")

        if col2.button("❌", key=i):
            st.session_state.cart.pop(i)
            st.rerun()

    st.write("---")
    st.markdown(f"# TOTAL : Rp {total}")

    # ======================
    # 💰 BAYAR
    # ======================

    if st.button("💰 BAYAR SEKARANG", use_container_width=True):

        for item in st.session_state.cart:

            idx = barang.index[barang.kode == item["kode"]][0]
            barang.loc[idx, "stok"] -= item["jumlah"]

            new = pd.DataFrame([{
                "tanggal": datetime.now(),
                "kode": item["kode"],
                "nama": item["nama"],
                "jumlah": item["jumlah"],
                "total": item["jual"] * item["jumlah"],
                "profit": (item["jual"] - item["modal"]) * item["jumlah"]
            }])

            transaksi = pd.concat([transaksi, new], ignore_index=True)

        barang.to_csv(DATA_BARANG, index=False)
        transaksi.to_csv(DATA_TRANSAKSI, index=False)

        st.session_state.cart = []

        st.success("Transaksi berhasil ✅")

        # ======================
        # 🖨️ PRINT BLUETOOTH REAL
        # ======================

        struk = f"""
TOKO MARBOEEN KIDS
=====================
TOTAL : Rp {total}

Terima kasih 🙏
"""

        encoded = urllib.parse.quote(struk)
        url = f"rawbt://print?text={encoded}"

        st.markdown(
            f'<a href="{url}">🖨️ CETAK STRUK BLUETOOTH</a>',
            unsafe_allow_html=True
        )

else:
    st.info("Keranjang kosong")


# ======================
# 📜 RIWAYAT
# ======================

st.divider()
st.subheader("📜 Riwayat Transaksi")

st.dataframe(transaksi, use_container_width=True)
