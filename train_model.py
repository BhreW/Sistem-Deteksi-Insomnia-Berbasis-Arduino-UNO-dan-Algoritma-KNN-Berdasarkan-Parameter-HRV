import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib
import warnings

warnings.filterwarnings('ignore')

print("=== SISTEM PELATIHAN AI DETEKSI INSOMNIA ===")

# 1. Memuat Dataset Aktual
nama_file_csv = 'dataset.csv'
df = pd.read_csv(nama_file_csv)

print(f"Total data mentah: {len(df)} baris")

# Membuang baris kosong (jika ada)
df = df.dropna()

# --- FILTER OUTLIER ---
def buang_outlier(data, kolom):
    Q1 = data[kolom].quantile(0.25)
    Q3 = data[kolom].quantile(0.75)
    IQR = Q3 - Q1
    batas_bawah = Q1 - 1.5 * IQR
    batas_atas = Q3 + 1.5 * IQR
    return data[(data[kolom] >= batas_bawah) & (data[kolom] <= batas_atas)]

# Menerapkan filter ke fitur MeanRR dan SDNN
df = buang_outlier(df, 'MeanRR')
df = buang_outlier(df, 'SDNN')

print(f"Total data bersih setelah filter outlier: {len(df)} baris")

# --- FITUR BARU 1: Menghitung Rata-rata HRV per Label ---
print("\n[INFO] Menghitung Statistik Dataset...")
try:
    rata_rata_hrv = df.groupby('Label')[['MeanRR', 'SDNN']].mean()
    print("-" * 50)
    print("RATA-RATA HRV BERDASARKAN KONDISI (SEBELUM SCALING):")
    # Asumsi Label 0 = Normal, Label 1 = Insomnia
    print(f"Normal (0)   -> Mean RR: {rata_rata_hrv.loc[0, 'MeanRR']:.4f} s | SDNN: {rata_rata_hrv.loc[0, 'SDNN']:.4f} s")
    print(f"Insomnia (1) -> Mean RR: {rata_rata_hrv.loc[1, 'MeanRR']:.4f} s | SDNN: {rata_rata_hrv.loc[1, 'SDNN']:.4f} s")
    print("-" * 50)
except Exception as e:
    print(f"Gagal menghitung rata-rata HRV: {e}")

# 2. Memisahkan Fitur dan Target
X = df[['MeanRR', 'SDNN']] 
y = df['Label']            

# 3. Membagi Data Training (80%) dan Testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. PROSES FEATURE SCALING
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

NILAI_K = 3   

print(f"\nMelatih model KNN dengan K={NILAI_K}...")
knn = KNeighborsClassifier(n_neighbors=NILAI_K)
knn.fit(X_train_scaled, y_train)

# 5. Evaluasi & Prediksi
y_pred = knn.predict(X_test_scaled)

# --- FITUR BARU 2 & 3: Akurasi dan Confusion Matrix Teks ---
akurasi = accuracy_score(y_test, y_pred) * 100
cm = confusion_matrix(y_test, y_pred)

# Ekstraksi nilai True Negative, False Positive, False Negative, True Positive
tn, fp, fn, tp = cm.ravel()

print("\n" + "=" * 45)
print(f"✅ AKURASI MODEL (K={NILAI_K}): {akurasi:.2f}%")
print("=" * 45)
print("DETAIL CONFUSION MATRIX (Berdasarkan 20% Data Testing):")
print(f" - True Negative  (Benar Prediksi Normal)   : {tn} sampel")
print(f" - True Positive  (Benar Prediksi Insomnia) : {tp} sampel")
print(f" - False Positive (Salah Prediksi Insomnia) : {fp} sampel (Error)")
print(f" - False Negative (Salah Prediksi Normal)   : {fn} sampel (Error/Kritis)")
print("=" * 45)

# 6. Menyimpan Model dan Scaler
joblib.dump(knn, 'model_knn_insomnia.pkl')
joblib.dump(scaler, 'scaler_insomnia.pkl') 

print("\nSUKSES! File otak AI 'model_knn_insomnia.pkl' & 'scaler' berhasil diperbarui.")

# --- FITUR BARU 4: Menampilkan Gambar Plot Confusion Matrix Saja ---
print("Memuat grafik visualisasi Confusion Matrix...\n")
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Normal', 'Insomnia'])
disp.plot(cmap='Blues', values_format='d')
plt.title(f'Confusion Matrix Evaluasi KNN (K={NILAI_K})')
plt.show()