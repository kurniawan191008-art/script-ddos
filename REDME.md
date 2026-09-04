# LocalStorm

LocalStorm adalah utilitas HTTP load-testing yang ringan, dirancang untuk pengujian resmi terhadap localhost dan jaringan privat.

Dioptimalkan untuk lingkungan seperti Termux/Android, LocalStorm berguna untuk menguji server web lokal, lingkungan pengembangan, jaringan lab, dan sistem lain yang Anda miliki atau memiliki izin eksplisit untuk mengujinya.

## Features

- 🚀 Ringan dan cocok untuk Termux/Android
- 🌐 Mendukung localhost dan alamat IPv4 privat
- ⚡ Konfigurasi request rate (RPS)
- 🧵 Konfigurasi jumlah worker konkuren
- ⏱️ Konfigurasi durasi test dan timeout request
- 📊 Statistik performa secara real-time
- 📈 Latensi rata-rata, P95, dan maksimum
- 📦 Total data yang ditransfer
- ❌ Klasifikasi error:
  - Timeout
  - Connection errors
  - HTTP errors
  - Other errors
- 🔄 Sesi HTTP persisten untuk connection reuse
- 🛑 Graceful shutdown dengan Ctrl+C

## Requirements

- Python 3.8+
- `requests`

Install dependency dengan:

```bash
pip install requests
```

### Termux

```bash
pkg update
pkg install python
pip install requests
```

## Usage

Contoh dasar:

```bash
python localstorm.py http://127.0.0.1:8080
```

Menentukan durasi test:

```bash
python localstorm.py http://192.168.1.100:8080 --duration 30
```

Mengatur jumlah worker dan request rate:

```bash
python localstorm.py http://192.168.1.100:8080 \
  --workers 4 \
  --rps 20 \
  --duration 30
```

Mengatur timeout request:

```bash
python localstorm.py http://192.168.1.100:8080 \
  --timeout 10
```

## Command-Line Options

| Option | Default | Description |
|---|---|---|
| `url` | — | Target HTTP/HTTPS URL |
| `--duration` | `10` | Durasi test dalam detik |
| `--workers` | `4` | Jumlah worker konkuren |
| `--rps` | `10` | Maksimum total request per detik |
| `--timeout` | `5.0` | Timeout request dalam detik |

## Example Output

```
[+] Target allowed: http://192.168.1.100:8080 (private IP (192.168.1.100))
[+] Starting load test: duration=10s, workers=4, rps=20, timeout=5.0s
[+] Press Ctrl+C to stop early.

[Stats] Total: 180 | OK: 178 | Fail: 2 | RPS: 18.0 | Latency (ms) Avg: 24.3 P95: 41.7 Max: 87.2 | Bytes: 512.4KB

==================================================
LOAD TEST COMPLETED
==================================================
Total Duration        : 10.02s
Total Requests         : 200
Successful             : 198
Failed                 : 2
Requests/sec (avg)     : 19.96
Total Data Transferred : 570.21 KB

Latency (ms):
  Average : 24.71
  P95     : 43.12
  Maximum : 91.53

Error Breakdown:
  Connection: 2
==================================================
```

## Target Restrictions

LocalStorm secara sengaja membatasi target hanya untuk:

- `localhost`
- `127.0.0.1`
- Alamat IPv4 privat

Alamat IP publik dan hostname sembarang akan ditolak.

Pembatasan ini dimaksudkan untuk mengurangi risiko pengujian tidak sengaja terhadap sistem di luar lingkungan pengujian yang sah.

## Use Cases

LocalStorm dapat berguna untuk:

- Menguji aplikasi web lokal
- Mengukur latensi server HTTP
- Menguji server pengembangan (development server)
- Mengevaluasi perilaku server di bawah beban terkontrol
- Latihan laboratorium jaringan dan keamanan siber
- Lingkungan penetration-testing yang sah/berizin
- Menguji layanan yang berjalan di LAN privat

## Responsible Use

- Gunakan LocalStorm hanya terhadap sistem yang Anda miliki atau memiliki izin eksplisit untuk diuji.
- Jangan gunakan untuk mengganggu, menurunkan performa, atau membebani sistem milik orang lain atau organisasi lain.
- Pembatasan target adalah bagian dari desain keamanan tool ini dan tidak boleh dihapus saat digunakan di lingkungan yang izinnya tidak jelas.

## Project Status

LocalStorm adalah proyek eksperimental kecil yang berfokus pada pengujian performa HTTP sederhana di lingkungan terbatas seperti Android/Termux.

Kontribusi, laporan bug, dan perbaikan sangat diterima.

## License

Proyek ini dilisensikan di bawah MIT License. Lihat file `LICENSE` untuk detailnya.
