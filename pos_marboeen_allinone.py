import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ======================
# FILE DATA
# ======================

DATA_BARANG = "data_barang.csv"
DATA_TRANSAKSI = "transaksi.csv"

# ======================
# LOAD DATA
# ======================

def load_barang():
    if os.path.exists(DATA_BARANG):
        return pd.read_csv(DATA_BARANG)
    df = pd.DataFrame(columns=["kode","nama","modal","jual","stok","expired"])
    df.to_csv(DATA_BARANG, index=False)
    return df

def load_transaksi():
    if os.path.exists(DATA_TRANSAKSI):
        return pd.read_csv(DATA_TRANSAKSI)
    df = pd.DataFrame(columns=["tanggal","kode","nama","jumlah","total","profit"])
    df.to_csv(DATA_TRANSAKSI, index=False)
    return df

barang = load_barang()
transaksi = load_transaksi()

# ======================
# SESSION
# ======================

if "page" not in st.session_state:
    st.session_state.page = "Menu"

if "cart" not in st.session_state:
    st.session_state.cart = []

def go(p):
    st.session_state.page = p
    st.rerun()

# ======================
# MENU UTAMA
# ======================

if st.session_state.page == "Menu":

    st.title("🏪 POS MARBOEEN KIDS PRO")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("🧾 KASIR", use_container_width=True):
            go("Kasir")

        if st.button("📦 DATA BARANG", use_container_width=True):
            go("Barang")

    with col2:
        if st.button("📊 GRAFIK", use_container_width=True):
            go("Grafik")

        if st.button("📜 TRANSAKSI", use_container_width=True):
            go("Riwayat")

        if st.button("⚙️ FITUR TAMBAHAN", use_container_width=True):
            go("Fitur")

# ======================
# KASIR + KERANJANG
# ======================

elif st.session_state.page == "Kasir":

    st.title("🧾 KASIR")

    if barang.empty:
        st.warning("Belum ada barang")
    else:
        pilih = st.selectbox("Pilih Barang", barang["nama"])
        data = barang[barang["nama"] == pilih].iloc[0]

        jumlah = st.number_input("Jumlah",1,int(data["stok"]),1)

        if st.button("➕ Tambah ke Keranjang"):
            st.session_state.cart.append({
                "kode": data["kode"],
                "nama": data["nama"],
                "modal": data["modal"],
                "jual": data["jual"],
                "jumlah": jumlah
            })

    # ===== Keranjang =====
    st.subheader("🛒 Keranjang")

    total = 0

    for i,item in enumerate(st.session_state.cart):
        subtotal = item["jual"] * item["jumlah"]
        total += subtotal

        col1,col2 = st.columns([4,1])
        col1.write(f"{item['nama']} x {item['jumlah']} = Rp {subtotal}")

        if col2.button("❌", key=i):
            st.session_state.cart.pop(i)
            st.rerun()

    st.markdown(f"# TOTAL : Rp {total}")

    # ===== BAYAR =====
    if st.button("💰 BAYAR"):

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

            transaksi = pd.concat([transaksi,new],ignore_index=True)

        barang.to_csv(DATA_BARANG,index=False)
        transaksi.to_csv(DATA_TRANSAKSI,index=False)

        st.session_state.cart = []

        st.success("Transaksi berhasil ✅")

        # ===== CETAK BLUETOOTH REAL =====
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

    if st.button("⬅ Kembali"):
        go("Menu")

# ======================
# DATA BARANG
# ======================

elif st.session_state.page == "Barang":

    st.title("📦 DATA BARANG")

    st.dataframe(barang)

    kode = st.text_input("Kode")
    nama = st.text_input("Nama")
    modal = st.number_input("Modal",0)
    jual = st.number_input("Jual",0)
    stok = st.number_input("Stok",0)
    expired = st.date_input("Expired")

    if st.button("SIMPAN"):

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

    if st.button("⬅ Kembali"):
        go("Menu")

# ======================
# GRAFIK
# ======================

elif st.session_state.page == "Grafik":

    st.title("📊 PROFIT")

    if not transaksi.empty:
        transaksi["tanggal"] = pd.to_datetime(transaksi["tanggal"])
        transaksi["bulan"] = transaksi["tanggal"].dt.strftime("%Y-%m")
        data = transaksi.groupby("bulan")["profit"].sum()
        st.bar_chart(data)

    if st.button("⬅ Kembali"):
        go("Menu")

# ======================
# RIWAYAT
# ======================

elif st.session_state.page == "Riwayat":

    st.title("📜 RIWAYAT")

    st.dataframe(transaksi)

    if st.button("⬅ Kembali"):
        go("Menu")

# ======================
# FITUR TAMBAHAN
# ======================

elif st.session_state.page == "Fitur":

    st.title("⚙️ FITUR TAMBAHAN")

    # 🔔 NOTIFIKASI STOK
    habis = barang[barang["stok"] <= 0]
    menipis = barang[(barang["stok"] > 0) & (barang["stok"] <= 5)]

    if not habis.empty:
        st.error("⚠️ STOK HABIS!")
        st.dataframe(habis[["nama","stok"]])

    if not menipis.empty:
        st.warning("⚠️ Stok hampir habis")

    st.divider()

    # ✏️ EDIT & HAPUS
    st.subheader("Edit / Hapus Barang")

    if not barang.empty:
        pilih = st.selectbox("Pilih barang", barang["nama"])
        data = barang[barang["nama"] == pilih].iloc[0]
        idx = barang[barang["nama"] == pilih].index[0]

        kode = st.text_input("Kode", data["kode"])
        nama = st.text_input("Nama", data["nama"])
        modal = st.number_input("Modal", value=int(data["modal"]))
        jual = st.number_input("Jual", value=int(data["jual"]))
        stok = st.number_input("Stok", value=int(data["stok"]))

        col1,col2 = st.columns(2)

        if col1.button("💾 Update"):
            barang.loc[idx] = [kode,nama,modal,jual,stok,data["expired"]]
            barang.to_csv(DATA_BARANG,index=False)
            st.success("Barang diperbarui")

        if col2.button("🗑️ Hapus"):
            barang = barang.drop(idx)
            barang.to_csv(DATA_BARANG,index=False)
            st.warning("Barang dihapus")

    st.divider()

    # 📷 SCAN BARCODE
    st.subheader("Scan Barcode")
    st.camera_input("Arahkan ke barcode")

    if st.button("⬅ Kembali"):
        go("Menu")
