# Bot Automator (macOS)

Bot ini merekam aksi mouse/keyboard lalu memutarnya kembali. Dokumentasi ini khusus untuk macOS, termasuk setup Accessibility.

## 1) Prasyarat

- macOS
- Python 3.9+ (disarankan 3.10+)
- Akses ke terminal (Terminal, iTerm, atau VS Code)

## 2) Instalasi Dependensi

Jalankan dari folder project:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Jika belum ada `requirements.txt`, install manual:

```bash
pip install pynput pyautogui numpy
```

## 3) Izin Accessibility (WAJIB)

Tanpa izin ini, mouse/keyboard tidak bisa digerakkan oleh script.

1. Buka **System Settings** → **Privacy & Security** → **Accessibility**.
2. Aktifkan aplikasi yang kamu pakai untuk menjalankan script:
   - Terminal / iTerm, dan/atau
   - VS Code (jika menjalankan dari integrated terminal).
3. Tutup lalu buka lagi terminal/VS Code.

Opsional (jika mouse tetap tidak bergerak):
- **Privacy & Security** → **Input Monitoring** → aktifkan juga untuk Terminal/VS Code.

## 4) Rekam Aksi

```bash
python recorder.py
```

- Masukkan tujuan rekaman (contoh: `login`, `farming`, `test`).
- Lakukan gerakan mouse, klik, ketik, dan scroll 2 jari.
- Tekan `ESC` untuk berhenti.
- Tekan `Ctrl+C` untuk batal/berhenti paksa (tetap menyimpan jika sudah mulai).
- File rekaman tersimpan di `recordings/<tujuan>.json` (fallback ke `recordings/rekaman_bot.json` jika kosong).

## 5) Playback Aksi

```bash
python player.py
```

Tips:
- Untuk stop paksa, arahkan kursor ke pojok kiri atas (Fail-safe PyAutoGUI).
- Saat start, pilih file rekaman (nomor atau nama file).
- Masukkan `SPEED_MULT` saat diminta untuk mengatur kecepatan.
- Pilih mode loop `y/N` untuk mengulang playback atau sekali jalan.

## 6) Pengaturan Kecepatan

Saat playback, masukkan nilai `SPEED_MULT`:
- `1.0` normal
- `1.5` lebih cepat
- `2.0` sangat cepat

## 7) Troubleshooting

**Mouse/kursor tidak bergerak**
- Pastikan Accessibility sudah diaktifkan untuk app terminal.
- Restart terminal/VS Code setelah mengubah izin.

**Playback patah-patah**
- Ini normal jika rekaman terlalu rapat.
- Coba naikkan `SPEED_MULT` atau rekam ulang dengan gerakan lebih stabil.

**File rekaman tidak ditemukan**
- Pastikan menjalankan dari folder project.
- Cek file `recordings/rekaman_bot.json`.

---

Kalau mau, aku bisa tambahkan:
- log ke file,
- filter gerakan kecil agar lebih halus,
- atau GUI sederhana untuk start/stop. 
