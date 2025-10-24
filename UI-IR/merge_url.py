import pandas as pd

# === BACA DATA ASLI & PREPROCESSED ===
df_raw = pd.read_csv("resep.csv")
df_clean = pd.read_csv("resep_preprocessed.csv", sep="\t", encoding="latin1")

# Pastikan format judul sama (biar bisa di-merge)
df_raw['judul'] = df_raw['judul'].str.strip().str.lower()
df_clean['judul'] = df_clean['judul'].str.strip().str.lower()

# === GABUNGKAN BERDASARKAN 'judul' ===
df_merged = df_clean.merge(
    df_raw[['judul', 'url']],
    on='judul',
    how='left'
)

# === SIMPAN KE FILE BARU ===
df_merged.to_csv("resep_final.csv", index=False)

print("File 'resep_final.csv' berhasil dibuat!")
print(df_merged.head())
