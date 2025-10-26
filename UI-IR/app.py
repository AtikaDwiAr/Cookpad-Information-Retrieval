import streamlit as st
import pandas as pd
from pyserini.search.lucene import LuceneSearcher
import re

# LOAD DATA & SEARCHER

# Data dengan URL dan hasil preprocressing
df_final = pd.read_csv("resep_final.csv")

# Data hasil scraping asli
df_raw = pd.read_csv("resep.csv")

# Inisialisasi Lucene Searcher
searcher = LuceneSearcher("indexes/index_resep")
searcher.set_bm25(k1=0.9, b=0.4)

# STREAMLIT UI

st.set_page_config(page_title="Temu Kembali Resep Masakan", layout="wide")

# Styling
st.markdown(
    """
    <style>
    body {
        background-color: #FEEAE6;
    }
    .stApp {
        background-color: #FEEAE6;
    }
    h1, h3, p {
        color: #442C2E;
        font-family: "Open-sans", sans-serif;
    }
    label[data-testid="stWidgetLabel"] > div > p {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #5D4037 !important;
        font-family: "Open Sans", sans-serif !important;
    }
    .stTextInput > div > div > input {
        color: #442C2E;
        font-family: "Open Sans", sans-serif;
        background-color: #FAF6F5;
        border-radius: 10px;
        border: 3px solid #8D6E63;
        padding: 10px 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Judul
st.markdown(
    """
    <h1 style="text-align: center; color: #442C2E; font-family: 'Open Sans', sans-serif; font-size: 44px;">
        Temu Kembali Resep Masakan
    </h1>
    """,
    unsafe_allow_html=True
)

query = st.text_input("Cari Resep Berdasarkan Kata Kunci")

if query:
    st.write(f"Hasil pencarian untuk **'{query}'**:")

    # Lakukan pencarian
    hits = searcher.search(query, k=20)

    if len(hits) == 0:
        st.warning("Tidak ditemukan hasil untuk kata kunci tersebut")
    else:
        hasil_ditampilkan = 0

        for hit in hits:
            docid = hit.docid
            doc = searcher.doc(docid)
            raw_text = doc.raw()

            # Ekstrak judul dari teks mentah hasil indexing
            match = re.search(r"Judul: (.*?) \|", raw_text)
            judul = match.group(1).strip() if match else None

            if not judul:
                continue  # skip jika tidak ada judul

            # Kapitalisasi setiap huruf awal kata
            judul_capital = judul.title()

            # Ambil URL dari df_final
            matched_url = df_final[df_final['judul'].str.lower() == judul.lower()]
            url = None
            if not matched_url.empty:
                raw_url = matched_url.iloc[0]['url']
                if isinstance(raw_url, str) and pd.notna(raw_url):
                    raw_url = raw_url.strip()
                    if not raw_url.startswith("http"):
                        raw_url = "https://" + raw_url.lstrip('/')
                    url = raw_url

            # Jika tidak ada URL valid, skip hasil ini
            if not url or not url.startswith("http"):
                continue

            # Ambil bahan dari df_raw
            matched_bahan = df_raw[df_raw['judul'].str.lower() == judul.lower()]
            bahan = matched_bahan.iloc[0]['bahan'] if not matched_bahan.empty else None

            # Ambil hanya 2 bahan pertama
            bahan_preview = []
            if pd.notna(bahan):
                bahan_list = re.split(r',|\n|•|-', str(bahan))
                bahan_list = [b.strip() for b in bahan_list if b.strip()]
                bahan_preview = bahan_list[:2]

            # Tampilkan hasil
            st.markdown(f"### [{judul_capital}]({url})")

            if bahan_preview:
                st.markdown("**Bahan:**")
                for b in bahan_preview:
                    st.markdown(f"- {b}")

            st.markdown("___")  # pemisah antar hasil
            hasil_ditampilkan += 1

        if hasil_ditampilkan == 0:
            st.warning("Tidak ada hasil ditemukan.")
