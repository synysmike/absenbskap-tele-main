# Bot Presensi BSKAP (Telegram)

Bot Telegram untuk melakukan absen [presensi.bskap.id](https://presensi.bskap.id) secara multi-user, dengan dukungan **absen langsung** dan **jadwal absen otomatis**.

## Fitur

- **Multi-user**: Setiap user punya kredensial sendiri (teguh, guntur, ayu, hisah, widhi, dll.).
- **Absen langsung**: Kirim perintah (mis. `teguh_in_now`) + foto selfie → absen langsung masuk/keluar.
- **Jadwal absen**: Kirim format `nama_status;tanggal;jam` + foto selfie → jadwal disimpan di Excel, absen dijalankan otomatis pada waktu yang dijadwalkan.
- **Lokasi**: Jika `lokasi_cabang` berupa koordinat, lokasi absen diacak dalam radius 2–6 m dari cabang.

## Persyaratan

- Python 3.10+
- Akun presensi.bskap.id (id_user & password per user)
- Token Bot Telegram dari [@BotFather](https://t.me/BotFather)

## Instalasi

1. Clone repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/absenbskap-tele.git
   cd absenbskap-tele
   ```

2. Buat environment (opsional tapi disarankan):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
   Atau pakai Conda:
   ```bash
   conda activate my_python12_env
   ```

3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurasi environment:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   - `API_TOKEN` — token bot dari BotFather
   - Untuk tiap user (mis. TEGUH): `TEGUH_USER_ID`, `TEGUH_PASSWORD`, `TEGUH_LOKASI`, `TEGUH_LOKASI_CABANG`

## Penggunaan

Jalankan bot:

```bash
python telegram_presensi.py
```

Atau dengan interpreter tertentu:

```bash
.venv/bin/python telegram_presensi.py
# atau
conda run -n my_python12_env python telegram_presensi.py
```

### Perintah di Telegram

| Perintah | Keterangan |
|----------|------------|
| `/start` | Panduan singkat |
| `/help`  | Bantuan lengkap |

**Absen langsung**

- `teguh_in` / `teguh_in_now` → absen **masuk**, lalu kirim foto selfie.
- `teguh_out` / `teguh_out_now` → absen **keluar**, lalu kirim foto selfie.

(Ganti `teguh` dengan nama user yang dikonfigurasi.)

**Jadwal absen**

- Format: `nama_status;tanggal;jam`
- Contoh: `teguh_in;09mar2026;07:17`
- Tanggal: `DDmonYYYY` (mis. `09mar2026`)
- Jam: `HH:MM` (mis. `07:17`)
- Setelah kirim perintah, kirim foto selfie. Jadwal disimpan; absen otomatis di waktu yang dijadwalkan.

## Konfigurasi (.env)

| Variabel | Contoh | Keterangan |
|----------|--------|------------|
| `API_TOKEN` | `123:ABC...` | Token bot Telegram |
| `TEGUH_USER_ID` | `260200098` | ID user presensi.bskap.id |
| `TEGUH_PASSWORD` | `***` | Password presensi |
| `TEGUH_LOKASI` | `Jakarta` | Nama lokasi (bisa teks) |
| `TEGUH_LOKASI_CABANG` | `-7.316514,112.724501` | Koordinat cabang (lat,lon); jika diisi, lokasi absen diacak 2–6 m |

Ulangi pola yang sama untuk user lain (GUNTUR_, AYU_, HISAH_, WIDHI_, dll.).

## Data jadwal & foto

- **Excel**: `schedules.xlsx` — menyimpan jadwal (username, status, date, time, path foto, done, chat_id).
- **Foto**: Disimpan per user di `images/<username>/`, nama file `DDmonYYYY_HHMM.png`.

## Struktur proyek

```
.
├── telegram_presensi.py   # Bot Telegram + scheduler
├── test.py                # PresensiClient (login + submit presensi)
├── requirements.txt
├── .env.example
├── schedules.xlsx         # (dibuat otomatis)
├── images/                # Foto per user (dibuat otomatis)
│   └── teguh/
└── docs/
    └── BOT_HELP_TEXT.md   # Teks bantuan untuk response /help
```

## Lisensi

MIT (atau sesuaikan dengan kebijakan Anda.)
