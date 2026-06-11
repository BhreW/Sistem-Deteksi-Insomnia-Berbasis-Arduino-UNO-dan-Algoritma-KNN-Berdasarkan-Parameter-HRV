# 🩺 Sistem Deteksi Insomnia Real-Time Berbasis Internet of Medical Things (IoMT) Menggunakan Arduino UNO dan Algoritma K-Nearest Neighbor (KNN) Berdasarkan Parameter Heart Rate Variability (HRV)

## 📌 Project Overview

Proyek ini merupakan pengembangan sistem instrumen medis pintar berbasis **Internet of Medical Things (IoMT)** untuk mendeteksi indikasi gangguan tidur (*insomnia*) secara **real-time** menggunakan sinyal **Elektrokardiogram (EKG)**.

Berbeda dengan metode diagnosis konvensional seperti *Polysomnography (PSG)* yang mahal dan kompleks, sistem ini menawarkan solusi yang lebih:

- Portable
- Low-cost
- Real-time
- Mudah digunakan

Sistem memanfaatkan kombinasi:

- **Embedded System** → Akuisisi dan filtering sinyal biologis
- **Machine Learning** → Analisis HRV dan klasifikasi insomnia

---

## 🧠 Konsep Dasar Sistem

Deteksi insomnia dilakukan berdasarkan analisis **Heart Rate Variability (HRV)**, khususnya parameter:

- **Mean RR**
- **SDNN**

Penderita insomnia cenderung mengalami kondisi **hyperarousal**, yaitu peningkatan aktivitas sistem saraf simpatis yang menyebabkan:

- Variabilitas detak jantung lebih tinggi
- Fluktuasi interval RR lebih tidak stabil
- Nilai SDNN lebih besar dibanding individu normal

---

# 🛠️ Hardware Setup

## 🔩 Komponen Utama

| Komponen | Fungsi |
|---|---|
| Arduino UNO | Mikrokontroler utama dan ADC 10-bit |
| AD8232 ECG Sensor | Penguat dan filter sinyal EKG |
| Disposable ECG Electrode | Akuisisi sinyal bio-listrik jantung |
| Kabel USB | Komunikasi serial ke PC |

---

## 🔌 Pinout Arduino UNO

| Pin AD8232 | Pin Arduino UNO | Fungsi |
|---|---|---|
| GND | GND | Ground sistem |
| 3.3V | 3.3V | Supply tegangan sensor |
| OUTPUT | A0 | Input analog EKG |
| LO- | 11 | Leads-Off Detection negatif |
| LO+ | 10 | Leads-Off Detection positif |

> ⚠️ **Penting:** Jangan menggunakan pin 5V untuk AD8232 karena dapat merusak modul sensor.

---

# 📂 Project Structure

```text
📦 insomnia-detection-iomt
├── Arduino.ino
├── train_model.py
├── realtime_diagnosis.py
├── realtime_plotter.py
├── dataset.csv
├── model_knn_insomnia.pkl
├── scaler_insomnia.pkl
└── README.md
```

---

# 📄 Penjelasan File

| File | Deskripsi |
|---|---|
| `Arduino.ino` | Firmware Arduino untuk pembacaan sinyal EKG dan filtering EMA |
| `train_model.py` | Pelatihan model KNN menggunakan dataset HRV |
| `realtime_diagnosis.py` | Diagnosis insomnia secara real-time berbasis HRV |
| `realtime_plotter.py` | Monitoring EKG real-time dengan visualisasi grafik, ekstraksi HRV, klasifikasi KNN, evaluasi akurasi, dan penyimpanan hasil pengujian |
| `dataset.csv` | Dataset HRV dari PhysioNet CAP Sleep Database |
| `model_knn_insomnia.pkl` | Model KNN hasil training |
| `scaler_insomnia.pkl` | StandardScaler hasil training |

---

# ⚙️ System Workflow

```text
[Tubuh Pasien]
       ↓
[Elektroda EKG]
       ↓
[Sensor AD8232]
       ↓
[Arduino UNO]
       ↓
[Filtering EMA]
       ↓
[USB Serial]
       ↓
[Python Processing]
       ↓
[HRV Feature Extraction]
       ↓
[KNN Classification]
       ↓
[Diagnosis Result]
```

---

# 🔬 Detail Alur Sistem

## 1️⃣ Akuisisi Sinyal EKG

Elektroda menangkap aktivitas bio-listrik jantung dan mengirimkannya ke sensor AD8232 untuk:

- Penguatan sinyal
- Filtering noise dasar

---

## 2️⃣ Filtering Digital pada Arduino

Arduino melakukan:

- Pembacaan ADC 10-bit
- Filtering menggunakan **Exponential Moving Average (EMA)**

Persamaan filter:

```math
EMA = k \times data\_baru + (1-k) \times data\_lama
```

Dengan:

```math
k = 0.5
```

Sampling rate sistem:

```text
100 Hz (10 ms)
```

---

## 3️⃣ Windowing Data

Python menerima data serial dari Arduino dan menyimpannya selama:

```text
60 detik = 6000 sampel
```

---

## 4️⃣ Ekstraksi Fitur HRV

Sinyal EKG diproses menggunakan:

```python
scipy.signal.find_peaks()
```

Parameter:

| Parameter | Nilai | Fungsi |
|---|---|---|
| prominence | 50 | Deteksi gelombang R |
| distance | 60 | Membatasi BPM maksimum |

---

## 5️⃣ Perhitungan HRV

### BPM

```math
BPM = \frac{60}{MeanRR}
```

### Mean RR

Rata-rata interval antar detak jantung.

### SDNN

Standar deviasi interval RR sebagai indikator HRV.

---

## 6️⃣ Machine Learning Inference

Fitur:

```text
[Mean RR, SDNN]
```

diproses menggunakan:

- StandardScaler
- K-Nearest Neighbor (KNN)

Konfigurasi model:

```text
K = 3
```

Output:

| Label | Kondisi |
|---|---|
| 0 | Normal |
| 1 | Insomnia |

---

## 7️⃣ Temporal Consistency Check

Untuk mengurangi false detection akibat:

- Motion artifact
- Noise sinyal
- Gerakan tubuh

Sistem menerapkan:

```text
Diagnosis valid jika hasil sama muncul 3–5 kali berturut-turut
```

---

# 📊 Dataset

Dataset berasal dari:

```text
PhysioNet CAP Sleep Database
```

Isi dataset:

| Kolom | Deskripsi |
|---|---|
| MeanRR | Rata-rata interval RR |
| SDNN | Standar deviasi RR |
| Label | 0 = Normal, 1 = Insomnia |

Total data:

```text
14.016 data HRV
```

---

# 🧪 Cara Menjalankan Project

# 1️⃣ Install Dependency

```bash
pip install pyserial numpy scipy pandas scikit-learn joblib matplotlib
```

---

# 2️⃣ Training Model AI

Jalankan:

```bash
python train_model.py
```

Output:

- `model_knn_insomnia.pkl`
- `scaler_insomnia.pkl`

---

# 3️⃣ Upload Firmware Arduino

1. Hubungkan Arduino UNO ke PC
2. Buka `Arduino.ino`
3. Pilih:
   - Board → Arduino UNO
   - COM Port yang sesuai
4. Klik **Upload**

> ⚠️ Setelah upload selesai, tutup Serial Monitor Arduino IDE agar port serial tidak terkunci.

---

# 4️⃣ Pemasangan Elektroda

## Posisi Elektroda

| Elektroda | Posisi |
|---|---|
| Merah (RA) | Dada kanan atas |
| Kuning (LA) | Dada kiri atas |
| Hijau (RL) | Perut kiri bawah / ground |

---

## Rekomendasi Pengambilan Data

- Gunakan laptop tanpa charger
- Hindari gerakan tubuh
- Duduk rileks
- Bersihkan kulit sebelum pemasangan elektroda

---

# 5️⃣ Menjalankan Diagnosis Real-Time

Jalankan:

```bash
python realtime_diagnosis.py
```

---

## Input Program

### Nama Subjek

```text
Masukkan Nama Kelompok Subjek:
```

### Ground Truth

```text
Masukkan Kondisi Sebenarnya
(0 = Normal, 1 = Insomnia):
```

---

## Output Sistem

Setiap 60 detik sistem akan menampilkan:

- BPM
- Mean RR
- SDNN
- Hasil diagnosis AI

Contoh:

```text
BPM        : 74
Mean RR    : 0.81
SDNN       : 0.13
Diagnosis  : INSOMNIA
```

---

# 💾 Penyimpanan Hasil

Data hasil pengujian otomatis disimpan sebagai file CSV:

```text
Hasil_Uji_Pasien_A_01.csv
```

Jika pengujian diulang:

```text
Hasil_Uji_Pasien_A_02.csv
Hasil_Uji_Pasien_A_03.csv
```

---

# 📈 Hasil dan Analisis

Berdasarkan pengujian:

| Kondisi | SDNN |
|---|---|
| Normal | ~0.08 detik |
| Insomnia | ~0.13 detik |

Hal ini menunjukkan bahwa penderita insomnia memiliki:

- Variabilitas detak jantung lebih tinggi
- Aktivitas saraf simpatis berlebih
- HRV lebih tidak stabil

---

---

# 🖥️ Penjelasan realtime_plotter.py

File `realtime_plotter.py` merupakan modul monitoring dan diagnosis insomnia real-time yang mengintegrasikan akuisisi sinyal EKG dari Arduino, visualisasi gelombang EKG secara langsung, ekstraksi fitur Heart Rate Variability (HRV), klasifikasi menggunakan model K-Nearest Neighbor (KNN), evaluasi hasil prediksi, serta penyimpanan hasil pengujian ke dalam file CSV.

## Workflow realtime_plotter.py

```text
Sensor AD8232
      ↓
Arduino UNO
      ↓
Serial USB
      ↓
Realtime Plotter (Python)
      ↓
Visualisasi ECG
      ↓
Deteksi R-Peak
      ↓
Perhitungan HRV
      ↓
KNN Classification
      ↓
Diagnosis Insomnia
      ↓
Evaluasi & Penyimpanan CSV
```

## Fitur Utama

### 1. Monitoring ECG Real-Time

Program menampilkan sinyal ECG secara langsung menggunakan Matplotlib dengan tampilan menyerupai monitor pasien rumah sakit.

Karakteristik visualisasi:

- Tema gelap (dark mode)
- Grafik berwarna hijau neon
- Update grafik setiap 20 ms
- Menampilkan 3 detik data ECG terakhir
- Auto-scaling sumbu amplitudo

Visualisasi ini memudahkan pengguna memantau kualitas sinyal dan memastikan elektroda terpasang dengan benar.

---

### 2. Akuisisi Data dari Arduino

Data ECG dibaca melalui komunikasi serial:

```python
PORT_ARDUINO = 'COM13'
BAUD_RATE = 115200
```

Arduino mengirimkan data hasil pembacaan sensor AD8232 secara kontinu dengan sampling rate:

```text
100 Hz
```

atau:

```text
100 sampel per detik
```

---

### 3. Buffer Data Real-Time

Program menggunakan dua buffer terpisah:

#### Buffer Visualisasi

Digunakan untuk menampilkan:

```text
3 detik data ECG terakhir
```

agar grafik tetap responsif.

#### Buffer Machine Learning

Digunakan untuk menyimpan:

```text
60 detik data ECG
```

yang akan digunakan untuk ekstraksi fitur HRV.

Jumlah sampel yang dikumpulkan:

```text
100 Hz × 60 detik = 6000 sampel
```

---

### 4. Deteksi Puncak R (R-Peak Detection)

Setelah 60 detik data terkumpul, sistem melakukan deteksi puncak R menggunakan:

```python
find_peaks()
```

dengan parameter:

```python
distance=60
prominence=50
```

Parameter tersebut digunakan untuk:

- Mengurangi deteksi noise
- Memastikan hanya puncak ECG yang signifikan terdeteksi
- Membatasi BPM maksimum sekitar 100 BPM

---

### 5. Ekstraksi Fitur HRV

Dari posisi puncak R yang berhasil dideteksi, sistem menghitung interval RR:

```math
RR = \frac{\Delta Sampel}{Sampling Rate}
```

Kemudian diekstraksi dua fitur utama:

#### Mean RR

Rata-rata interval antar detak jantung.

```math
MeanRR = \frac{\sum RR}{n}
```

#### SDNN

Standar deviasi interval RR sebagai indikator variabilitas detak jantung.

```math
SDNN = std(RR)
```

---

### 6. Perhitungan BPM

Heart Rate dihitung menggunakan:

```math
BPM = \frac{60}{MeanRR}
```

Contoh:

```text
MeanRR = 0.80 detik
```

maka:

```text
BPM = 75 bpm
```

---

### 7. Klasifikasi Menggunakan KNN

Fitur:

```text
[Mean RR, SDNN]
```

dilakukan normalisasi menggunakan:

```text
StandardScaler
```

kemudian diproses oleh model:

```text
K-Nearest Neighbor (KNN)
```

Output sistem:

| Label | Diagnosis |
|---|---|
| 0 | Normal |
| 1 | Insomnia |

---

### 8. Evaluasi Prediksi

Pengguna memasukkan kondisi sebenarnya (ground truth):

```text
0 = Normal
1 = Insomnia
```

Setiap hasil prediksi dibandingkan dengan label sebenarnya untuk menentukan:

```text
BENAR
atau
SALAH
```

---

### 9. Perhitungan Akurasi Real-Time

Setelah pengujian selesai, sistem menghitung:

```math
Accuracy = \frac{Jumlah Prediksi Benar}{Total Pengujian} \times 100\%
```

untuk mengevaluasi performa model selama proses pengujian berlangsung.

---

### 10. Penyimpanan Hasil Otomatis

Seluruh hasil pengujian disimpan dalam file CSV.

Contoh:

```text
Hasil_Uji_Pasien_A_01.csv
```

Isi file meliputi:

- Nama subjek
- BPM
- Mean RR
- SDNN
- Label sebenarnya
- Prediksi sistem
- Status evaluasi

Jika file sudah ada, sistem akan otomatis membuat file baru:

```text
Hasil_Uji_Pasien_A_02.csv
Hasil_Uji_Pasien_A_03.csv
```

dan seterusnya.

---

### Contoh Output Sistem

```text
Fitur Klinis -> BPM: 74 bpm
Mean RR      : 0.8100 s
SDNN         : 0.1300 s

🚨 DIAGNOSIS SISTEM:
TERINDIKASI INSOMNIA
```

atau

```text
Fitur Klinis -> BPM: 72 bpm
Mean RR      : 0.8300 s
SDNN         : 0.0800 s

✅ DIAGNOSIS SISTEM:
DETAK JANTUNG NORMAL
```

---

### Fungsi dalam Sistem IoMT

Pada arsitektur IoMT yang dikembangkan, `realtime_plotter.py` berperan sebagai pusat pemrosesan (*edge computing layer*) yang menerima data ECG dari perangkat akuisisi berbasis Arduino, melakukan analisis HRV secara real-time, menampilkan kondisi pasien melalui antarmuka visual, serta menghasilkan diagnosis otomatis menggunakan algoritma machine learning tanpa memerlukan pemrosesan cloud.

# ✅ Kesimpulan

Proyek ini berhasil merealisasikan sistem deteksi insomnia real-time berbasis IoMT menggunakan:

- Arduino UNO
- Sensor EKG AD8232
- Analisis HRV
- Algoritma KNN

Keunggulan sistem:

- Low-cost
- Portable
- Real-time
- Komputasi ringan
- Mudah dikembangkan

Sistem membuktikan bahwa analisis HRV sederhana menggunakan parameter:

- Mean RR
- SDNN

sudah cukup efektif untuk mendeteksi indikasi insomnia secara otomatis menggunakan pendekatan machine learning.

---

# 👨‍💻 Teknologi yang Digunakan

- Arduino UNO
- AD8232 ECG Sensor
- Python
- Scikit-learn
- NumPy
- SciPy
- Pandas
- Matplotlib

---

# 📚 Referensi

- PhysioNet CAP Sleep Database
- Heart Rate Variability (HRV) Analysis
- K-Nearest Neighbor (KNN)
- Internet of Medical Things (IoMT)

---

# 📜 License

Project ini dikembangkan untuk kebutuhan penelitian dan edukasi akademik.
