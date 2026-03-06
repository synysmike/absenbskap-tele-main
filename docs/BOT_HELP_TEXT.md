# Telegram Bot – Help (copy for help response)

Use this text in your bot’s **help** command or as the long description in BotFather.

---

**Bot Presensi BSKAP**

Bot untuk absen presensi.bskap.id lewat Telegram (multi-user, dengan jadwal).

---

**Perintah**

• `/start` — Panduan singkat dan daftar user  
• `/help` — Bantuan lengkap (pesan ini)

---

**1. Absen langsung (sekarang)**

Kirim salah satu (ganti nama user sesuai):

• `teguh_in` atau `teguh_in_now` → absen **masuk**  
• `teguh_out` atau `teguh_out_now` → absen **keluar**

Lalu kirim **foto selfie**. Absen akan diproses langsung.

User yang tersedia tergantung konfigurasi (misalnya: teguh, guntur, ayu, hisah, widhi).

---

**2. Jadwal absen (otomatis di waktu tertentu)**

Kirim dengan format:

`nama_status;tanggal;jam`

Contoh:

• `teguh_in;09mar2026;07:17` → jadwal absen masuk pada 9 Mar 2026 jam 07:17  
• `teguh_out;10mar2026;17:00` → jadwal absen keluar pada 10 Mar 2026 jam 17:00  

Format tanggal: **DDmonYYYY** (mis. 09mar2026)  
Format jam: **HH:MM** (mis. 07:17)

Setelah kirim perintah jadwal, kirim **foto selfie**. Jadwal akan disimpan; absen akan dijalankan otomatis saat waktunya (bot cek setiap 1 menit).

---

**Catatan**

• Foto selfie wajib untuk absen langsung dan untuk menyimpan jadwal.  
• Lokasi absen diacak 2–6 m dari titik cabang (jika cabang pakai koordinat).  
• Jika absen gagal, periksa koneksi dan data user di server presensi.bskap.id.

---

*Presensi BSKAP – Bot Absen via Telegram*
