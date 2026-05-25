import serial
import time
import numpy as np
from scipy.signal import find_peaks
import joblib
import warnings
import pandas as pd
import os 

warnings.filterwarnings('ignore')

print("=== SISTEM DETEKSI INSOMNIA REAL-TIME ===")
print("1. Memuat Model AI (KNN & Scaler)...")

# Load Model AI yang sudah dilatih
try:
    knn_model = joblib.load('model_knn_insomnia.pkl')
    scaler = joblib.load('scaler_insomnia.pkl')
    print("   -> Model berhasil dimuat!\n")
except Exception as e:
    print(f"Error memuat model: {e}")
    print("Pastikan file 'model_knn_insomnia.pkl' dan 'scaler_insomnia.pkl' ada di folder ini.")
    exit()

# =======================================================
# INPUT IDENTITAS PENGUJIAN
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

print(f"\n[Sistem akan menguji kelompok '{nama_subjek}' dengan Ground Truth: {str_label_sebenarnya}]")
# =======================================================

PORT_ARDUINO = 'COM13'  # Ganti dengan port Arduino/ESP32 Anda
BAUD_RATE = 115200     
SAMPLING_RATE = 100    
WAKTU_REKAM = 60       

print(f"\n2. Membuka koneksi ke port {PORT_ARDUINO}...")
try:
    ser = serial.Serial(PORT_ARDUINO, BAUD_RATE, timeout=1)
    time.sleep(2) 
    print("   -> Koneksi Berhasil! Silakan tempelkan elektroda ke dada pasien.\n")
except Exception as e:
    print(f"GAGAL: Pastikan mikrokontroler tertancap dan PORT sudah benar. Error: {e}")
    exit()

buffer_sinyal = []
target_sampel = SAMPLING_RATE * WAKTU_REKAM 

history_pengujian = []

print(f"Mulai merekam detak jantung selama {WAKTU_REKAM} detik...")
print("!!! Tekan tombol 'Ctrl + C' di terminal kapan saja untuk BERHENTI dan MELIHAT TABEL HASIL !!!\n")

try:
    while True:
        if ser.in_waiting > 0:
            data_masuk = ser.readline().decode('utf-8').strip()
            
            if data_masuk == '!' or not data_masuk.replace('.','',1).replace('-','',1).isdigit():
                continue
                
            buffer_sinyal.append(float(data_masuk))
            
            if len(buffer_sinyal) >= target_sampel:
                print(f"\n[Memproses Data {WAKTU_REKAM} Detik Terakhir...]")
                sinyal_array = np.array(buffer_sinyal)
                
                puncak_r, _ = find_peaks(sinyal_array, distance=60, prominence=50) 
                
                if len(puncak_r) > 1:
                    rr_intervals_detik = np.diff(puncak_r) / SAMPLING_RATE
                    mean_rr = np.mean(rr_intervals_detik)
                    sdnn = np.std(rr_intervals_detik)
                    
                    # =======================================================
                    # FITUR BARU: KALKULASI BPM (BEATS PER MINUTE)
                    # =======================================================
                    if mean_rr > 0:
                        bpm = 60 / mean_rr
                    else:
                        bpm = 0
                    
                    fitur_pasien = np.array([[mean_rr, sdnn]])
                    fitur_skala = scaler.transform(fitur_pasien)
                    prediksi = knn_model.predict(fitur_skala)[0]
                    
                    str_prediksi = "Insomnia" if prediksi == 1 else "Normal"
                    
                    # Format output diperbarui untuk menampilkan metrik BPM (pembulatan penuh)
                    print(f"Fitur Klinis -> BPM: {bpm:.0f} bpm | Mean RR: {mean_rr:.4f} s | SDNN: {sdnn:.4f} s")
                    print("=" * 45)
                    if prediksi == 1:
                        print("🚨 DIAGNOSIS SISTEM: TERINDIKASI INSOMNIA 🚨")
                    else:
                        print("✅ DIAGNOSIS SISTEM: DETAK JANTUNG NORMAL ✅")
                    print("=" * 45)

                    status_tebakan = "BENAR" if prediksi == label_sebenarnya else "SALAH"
                    
                    # Simpan data BPM ke memori tabel
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
                    print("⚠ Gagal mendeteksi detak jantung yang stabil.")
                    print("Pastikan elektroda menempel dengan baik dan pasien tidak banyak bergerak!")
                
                buffer_sinyal = []
                print("\nMelanjutkan perekaman...")

except KeyboardInterrupt:
    print("\n\n========================================================")
    print("Perekaman dihentikan. Memproses Tabel Hasil Pengujian...")
    print("========================================================\n")
    ser.close()

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