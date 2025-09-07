# samudra-ai
Paket Python untuk melakukan pengolahan koreksi bias model iklim global menggunakan arsitektur deep learning CNN-BiLSTM

# SamudraAI 🌊

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![PyPI version](https://badge.fury.io/py/samudra-ai.svg)](https://pypi.org/project/samudra-ai/)
[![Python](https://img.shields.io/pypi/pyversions/samudra-ai.svg)](https://pypi.org/project/samudra-ai/)

Paket Python untuk koreksi bias model iklim menggunakan arsitektur deep learning CNN-BiLSTM. 

**SamudraAI** memudahkan peneliti dan praktisi di bidang ilmu iklim untuk menerapkan metode koreksi bias yang canggih pada data GCM (General Circulation Model) menggunakan data observasi sebagai referensi.

## Fitur Utama

* 🧠 **Arsitektur CNN-BiLSTM**: Menggabungkan kemampuan ekstraksi fitur spasial dari CNN dengan pemahaman sekuens temporal dari LSTM.
* 📂 **Antarmuka Sederhana**: API yang bersih dan mudah digunakan, terinspirasi oleh `scikit-learn`.
* 🛠️ **Pra-pemrosesan Terintegrasi**: Fungsi bawaan untuk memuat, memotong, dan menormalisasi data iklim dalam format NetCDF.
* 💾 **Model Persistent**: Kemampuan untuk menyimpan model yang telah dilatih dan memuatnya kembali untuk inferensi di kemudian hari.

## Instalasi

Anda dapat menginstal SamudraAI langsung dari PyPI menggunakan pip:

```bash
pip install samudra-ai
```

## Cara Penggunaan Cepat (Quick Start)

Berikut adalah alur kerja dasar untuk menggunakan `SamudraAI`.

### 1. Siapkan Data Anda
Pastikan Anda memiliki data dalam format `xarray.DataArray`:
* `gcm_hist_data`: Data GCM historis (sebagai input `X`).
* `obs_data`: Data observasi/reanalysis (sebagai target `y`).
* `periode_training` : Samakan periode waktu antara `gcm_hist_data` dan `obs_data`
* `gcm_future_data`: Data GCM masa depan yang ingin dikoreksi
* `periode_future`: Tidak harus sama dengan `periode_training` (boleh lebih panjang)

```bash
### 2. import model
from samudra_ai import SamudraAI
from samudra_ai.data_loader import load_and_mask_dataset

### 3. Load GCM dan Observasi
gcm = load_and_mask_dataset("data_historical", "var_name_data_historical",
                            ("latitude_min", "latitude_max"), ("longitude_min", "longitude_max"),
                            ("periode awal (yyyy-mm-dd)", "periode akhir (yyyy-mm-dd)"))
obs = load_and_mask_dataset("data_observasi", "var_name_data_observasi",
                            ("latitude_min", "latitude_max"), ("longitude_min", "longitude_max"),
                            ("periode awal (yyyy-mm-dd)", "periode akhir (yyyy-mm-dd)"))

### 4. Inisialisasi dan Training Model
model = SamudraAI(time_seq="time_sequence") # time_sequence = periode temporal pembelajaran (bulanan)
model.fit(gcm, obs, epochs="epoch")    # epoch = jumlah pembelajaran model
model.plot_history(output_dir="local_path/")

### 5. Simpan dan/atau muat ulang model
model.save("nama_model")
model = SamudraAI.load("nama_model")

### 6. Evaluasi Historical dan Simpan Hasil Koreksi
eval_df, corrected_hist = model.evaluate_and_plot(
    raw_gcm_data=gcm,
    ref_data=obs,
    var_name_ref="sla",
    output_dir="local_path/",
    save_corrected_path="nama_hist_terkoreksi.nc"
)

### 6. Koreksi Proyeksi SSP
ssp = load_and_mask_dataset("data_proyeksi", "var_name_data_proyeksi",
                            ("latitude_min", "latitude_max"), ("longitude_min", "longitude_max"),
                            ("periode awal (yyyy-mm-dd)", "periode akhir (yyyy-mm-dd)"))
corrected_proj = model.correction(ssp, save_path="nama_proyeksi_terkoreksi.nc")
```

## Best Practice

* ✅ Disarankan menggunakan TensorFlow GPU untuk performa optimal
* ✅ Disarankan memiliki memory / RAM yang cukup untuk pengolahan data dengan resolusi tinggi dan luasan domain yang besar
* ✅ Jalankan pelatihan secara penuh di lingkungan lokal
* ⚠️ Hindari mencampur save/load model .keras antar environment yang berbeda
* ⚠️ Menggunakan Docker tetap bisa berjalan, namun proses save and load (penggunaan no.5) tidak bisa diproses karena perbedaan env
* 💡 Format .nc hasil koreksi bisa langsung digunakan untuk plotting dan analisis

## Lisensi

Proyek ini dilisensikan di bawah **MIT License**. Lihat file `LICENSE` untuk detailnya.
