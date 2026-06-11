import serial
import time
import numpy as np
from scipy.signal import find_peaks
import joblib
import warnings
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation

warnings.filterwarnings('ignore')

print("=== SISTEM DETEKSI INSOMNIA REAL-TIME ===")
print("1. Memuat Model AI (KNN & Scaler)...")

# Load Model AI
try:
    knn_model = joblib.load('model_knn_insomnia.pkl')
    scaler = joblib.load('scaler_insomnia.pkl')
    print("   -> Model berhasil dimuat!\n")
except Exception as e:
    print(f"Error memuat model: {e}")
    exit()

# =======================================================
# INPUT IDENTITAS
# =======================================================
print("--- IDENTITAS PENGUJIAN SAAT INI ---")
nama_subjek = input("Masukkan Nama Kelompok Subjek (misal: Pasien_Uji) : ")
label_input = input("Masukkan Kondisi Sebenarnya (0 = Normal, 1 = Insomnia) : ")

try:
    label_sebenarnya = int(label_input)
    str_label_sebenarnya = "Insomnia" if label_sebenarnya == 1 else "Normal"
except ValueError:
    print("Input salah! Default diatur ke 0 (Normal).")
    label_sebenarnya = 0
    str_label_sebenarnya = "Normal"

print(f"\n[Sistem menguji kelompok '{nama_subjek}' dengan Ground Truth: {str_label_sebenarnya}]")

# =======================================================
# KONFIGURASI HARDWARE & WAKTU
# =======================================================
PORT_ARDUINO = 'COM13'  # Sesuaikan dengan Port COM Arduino Anda
BAUD_RATE = 115200     
SAMPLING_RATE = 100    
WAKTU_REKAM = 60       # Waktu inferensi ML (60 detik)
WAKTU_VISUAL = 3       # Menampilkan 3 detik terakhir di grafik agar terlihat detail

print(f"\n2. Membuka koneksi ke port {PORT_ARDUINO}...")
try:
    ser = serial.Serial(PORT_ARDUINO, BAUD_RATE, timeout=1)
    time.sleep(2) 
    print("   -> Koneksi Berhasil! Silakan tempelkan elektroda ke tubuh pasien.")
except Exception as e:
    print(f"GAGAL: Pastikan mikrokontroler tertancap dan PORT benar. Error: {e}")
    exit()

# Penampung Data
buffer_sinyal_ml = []
target_sampel_ml = SAMPLING_RATE * WAKTU_REKAM 
target_sampel_visual = SAMPLING_RATE * WAKTU_VISUAL
buffer_visual = [0] * target_sampel_visual # Diisi 0 di awal agar grafik siap

history_pengujian = []

print(f"\nMulai merekam detak jantung...")
print("!!! Membuka Jendela Monitor EKG. TUTUP JENDELA GRAFIK JIKA INGIN BERHENTI !!!\n")

# =======================================================
# DESAIN TAMPILAN MONITOR RUMAH SAKIT (GUI)
# =======================================================
plt.style.use('dark_background') # Tema Gelap
fig, ax = plt.subplots(figsize=(10, 5))
fig.canvas.manager.set_window_title('Monitor EKG Pasien - IoMT')

ax.set_title(f"Live ECG Monitor - Pasien: {nama_subjek}", color='lime', fontsize=14, fontweight='bold')
ax.set_xlabel("Waktu (Sampel)", color='white')
ax.set_ylabel("Amplitudo Kelistrikan (ADC)", color='white')

# Garis grafik berwarna Hijau Neon (Khas EKG)
line, = ax.plot(range(target_sampel_visual), buffer_visual, lw=2, color='#00ff00')
ax.set_xlim(0, target_sampel_visual)
ax.set_ylim(0, 1023) # Rentang ADC standar Arduino Uno
ax.grid(True, linestyle=':', alpha=0.3, color='green')

# =======================================================
# FUNGSI ANIMASI & PEMROSESAN REAL-TIME
# =======================================================
def update_plot(frame):
    global buffer_sinyal_ml, buffer_visual
    
    # Membaca SEMUA data yang menumpuk di kabel USB secepat mungkin
    while ser.in_waiting > 0:
        try:
            data_masuk = ser.readline().decode('utf-8').strip()
            if data_masuk == '!' or not data_masuk.replace('.','',1).replace('-','',1).isdigit():
                continue
                
            nilai = float(data_masuk)
            
            # Masukkan ke penampung visual (geser data terlama)
            buffer_visual.append(nilai)
            buffer_visual.pop(0)
            
            # Masukkan ke penampung Machine Learning
            buffer_sinyal_ml.append(nilai)
            
            # JIKA SUDAH 60 DETIK -> PROSES ML DI LATAR BELAKANG
            if len(buffer_sinyal_ml) >= target_sampel_ml:
                print(f"\n[Memproses Data {WAKTU_REKAM} Detik Terakhir...]")
                sinyal_array = np.array(buffer_sinyal_ml)
                
                puncak_r, _ = find_peaks(sinyal_array, distance=60, prominence=50) 
                
                if len(puncak_r) > 1:
                    rr_intervals_detik = np.diff(puncak_r) / SAMPLING_RATE
                    mean_rr = np.mean(rr_intervals_detik)
                    sdnn = np.std(rr_intervals_detik)
                    bpm = 60 / mean_rr if mean_rr > 0 else 0
                    
                    fitur_pasien = np.array([[mean_rr, sdnn]])
                    fitur_skala = scaler.transform(fitur_pasien)
                    prediksi = knn_model.predict(fitur_skala)[0]
                    
                    str_prediksi = "Insomnia" if prediksi == 1 else "Normal"
                    status_tebakan = "BENAR" if prediksi == label_sebenarnya else "SALAH"
                    
                    print(f"Fitur Klinis -> BPM: {bpm:.0f} bpm | Mean RR: {mean_rr:.4f} s | SDNN: {sdnn:.4f} s")
                    if prediksi == 1:
                        print("🚨 DIAGNOSIS SISTEM: TERINDIKASI INSOMNIA 🚨")
                    else:
                        print("✅ DIAGNOSIS SISTEM: DETAK JANTUNG NORMAL ✅")
                    print("-" * 45)

                    history_pengujian.append({
                        "Subject": nama_subjek,
                        "BPM": f"{bpm:.0f}",
                        "Mean RR (s)": f"{mean_rr:.4f}",
                        "SDNN (s)": f"{sdnn:.4f}",
                        "Sebenarnya": str_label_sebenarnya,
                        "Prediksi Sistem": str_prediksi,
                        "Evaluasi": status_tebakan
                    })
                else:
                    print("⚠ Gagal mendeteksi detak jantung. Elektoda mungkin lepas.")
                
                # Kosongkan wadah ML untuk 1 menit berikutnya, grafik visual TIDAK dikosongkan agar tetap mulus
                buffer_sinyal_ml = []
                
        except Exception:
            pass

    # Perbarui gambar garis di layar
    line.set_data(range(target_sampel_visual), buffer_visual)
    
    # (Opsional) Auto-Scale Sumbu Y agar grafik tidak terlalu kecil
    min_val, max_val = min(buffer_visual), max(buffer_visual)
    if max_val - min_val > 50:
        ax.set_ylim(min_val - 50, max_val + 50)
        
    return line,

# Menjalankan fungsi animasi setiap 20 milidetik
ani = animation.FuncAnimation(fig, update_plot, interval=20, blit=False, cache_frame_data=False)

# Memunculkan Jendela. (Program akan tertahan/looping di baris ini sampai Anda mengklik X)
plt.show() 

# =======================================================
# SETELAH JENDELA GRAFIK DITUTUP (EVALUASI)
# =======================================================
ser.close()
print("\n\n========================================================")
print("Jendela Ditutup. Perekaman dihentikan. Memproses Tabel...")
print("========================================================\n")

if len(history_pengujian) > 0:
    df_hasil = pd.DataFrame(history_pengujian)
    print(df_hasil.to_string(index=True))
    
    jumlah_benar = len(df_hasil[df_hasil["Evaluasi"] == "BENAR"])
    total_data = len(df_hasil)
    akurasi = (jumlah_benar / total_data) * 100
    
    print("\n--------------------------------------------------------")
    print(f"Total Sesi Uji ({WAKTU_REKAM} detik) : {total_data} kali")
    print(f"Prediksi Sistem Benar     : {jumlah_benar} kali")
    print(f"AKURASI REAL-TIME         : {akurasi:.2f} %")
    print("--------------------------------------------------------")

    i = 1
    while True:
        nama_file_eksport = f"Hasil_Uji_{nama_subjek}_{i:02d}.csv"
        if not os.path.exists(nama_file_eksport):
            break
        i += 1

    df_hasil.to_csv(nama_file_eksport, index=False)
    print(f"✅ Data tabel telah otomatis disimpan ke file: {nama_file_eksport}")
else:
    print(f"Belum ada data pengujian {WAKTU_REKAM} detik yang berhasil diekstraksi.")