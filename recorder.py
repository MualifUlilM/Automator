import time
import json
import os
from pynput import mouse, keyboard

# Konfigurasi Folder dan Nama File
FOLDER_NAME = "recordings"
DEFAULT_FILE_NAME = "rekaman_bot.json"

def sanitize_name(name):
    safe = []
    for ch in name.strip():
        if ch.isalnum() or ch in ("-", "_"):
            safe.append(ch)
        elif ch.isspace():
            safe.append("_")
    return "".join(safe).lower()

try:
    purpose = input("Mau record untuk apa? (contoh: login, farming, test) : ").strip()
except KeyboardInterrupt:
    print("\n🛑 Rekaman dibatalkan sebelum mulai.")
    raise SystemExit(1)

safe_name = sanitize_name(purpose) if purpose else ""
FILE_NAME = f"{safe_name}.json" if safe_name else DEFAULT_FILE_NAME
PATH = os.path.join(FOLDER_NAME, FILE_NAME)

# Buat folder jika belum ada
if not os.path.exists(FOLDER_NAME):
    os.makedirs(FOLDER_NAME)
    print(f"📁 Folder '{FOLDER_NAME}' berhasil dibuat.")

data_rekaman = []
waktu_mulai = time.time()
m_listener = None

def catat_aksi(jenis, detail):
    waktu_sekarang = time.time() - waktu_mulai
    data_rekaman.append({
        "waktu": waktu_sekarang,
        "jenis": jenis,
        "detail": detail
    })

def on_move(x, y):
    catat_aksi("mouse_move", {"pos": (x, y)})

def on_click(x, y, button, pressed):
    catat_aksi("mouse_click", {"pos": (x, y), "button": str(button), "pressed": pressed})

def on_scroll(x, y, dx, dy):
    catat_aksi("mouse_scroll", {"pos": (x, y), "dx": dx, "dy": dy})

def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)
    catat_aksi("key_press", {"key": k})

def on_release(key):
    if key == keyboard.Key.esc:
        if m_listener is not None:
            m_listener.stop()
        return False

print(f"🔴 MEREKAM... File akan disimpan di: {PATH}")
print("Tekan 'ESC' atau Ctrl+C untuk berhenti.")

try:
    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as m_listener, \
         keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener:
        m_listener.join()
        k_listener.join()
except KeyboardInterrupt:
    if m_listener is not None:
        m_listener.stop()
    print("\n🛑 Rekaman dihentikan (Ctrl+C).")

# Simpan ke folder recordings
with open(PATH, "w") as f:
    json.dump(data_rekaman, f, indent=4) # indent=4 agar file JSON mudah dibaca manusia

print(f"✅ Selesai! {len(data_rekaman)} aksi tersimpan di folder '{FOLDER_NAME}'.")
