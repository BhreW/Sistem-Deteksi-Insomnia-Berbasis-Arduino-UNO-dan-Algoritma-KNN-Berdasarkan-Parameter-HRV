const int pinSensor = A0; 

float k = 0.5;             
float nilai_filter = 0;

void setup() {
  
  Serial.begin(115200);
  pinMode(pinSensor, INPUT);
}

void loop() {
  // 1. Membaca data mentah dari sensor
  int nilai_mentah = analogRead(pinSensor);
  
  // 2. Menghaluskan sinyal dengan algoritma Exponential Filter
  nilai_filter = (k * nilai_mentah) + ((1 - k) * nilai_filter);
  
  // 3. Mengirimkan HANYA nilai yang sudah dihaluskan ke Python (Uncomment jika butuh nilai mentah yang belum di filter)
  Serial.println(nilai_filter);
  // Serial.println(nilai_mentah); 
  
  // 4. Pengaturan waktu (Sampling Rate 100 Hz)
  delay(10); 
}