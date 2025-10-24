import os
import json
import pandas as pd

# Buat folder collection
os.makedirs("collection", exist_ok=True)

# Baca file preprocessed (hasil teks bersih)
df = pd.read_csv("resep_preprocessed.csv")

# Simpan tiap dokumen sebagai JSON (format Pyserini)
for i, row in df.iterrows():
    doc = {
        "id": str(i),
        "contents": f"{row['judul']} {row['bahan']} {row['langkah']}"
    }
    with open(f"collection/{i}.json", "w") as f:
        json.dump(doc, f)

print("Koleksi JSON untuk indexing berhasil dibuat di folder 'collection/'")

# Bangun index BM25
os.system(
    "python -m pyserini.index.lucene "
    "--collection JsonCollection "
    "--input collection "
    "--index index "
    "--generator DefaultLuceneDocumentGenerator "
    "--threads 2 "
    "--storePositions --storeDocvectors --storeRaw"
)
