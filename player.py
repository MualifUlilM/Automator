import json
import time
import random
import os
import math
import numpy as np
import pyautogui
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# Konfigurasi
FOLDER_NAME = "recordings"
FILE_NAME = "rekaman_bot.json"
PATH = os.path.join(FOLDER_NAME, FILE_NAME)
VERBOSE = True
SPEED_MULT = 2  # >1 lebih cepat, <1 lebih lambat

mouse_ctrl = MouseController()
kb_ctrl = KeyboardController()
pyautogui.FAILSAFE = True 

def coalesce_mouse_moves(aksi_list):
    """Gabungkan mouse_move beruntun agar playback lebih halus."""
    hasil = []
    for aksi in aksi_list:
        if aksi.get("jenis") == "mouse_move" and hasil and hasil[-1].get("jenis") == "mouse_move":
            hasil[-1] = aksi
        else:
            hasil.append(aksi)
    return hasil

def bezier_move(target_x, target_y, duration):
    """Simulasi gerakan melengkung yang natural"""
    start_x, start_y = pyautogui.position()
    
    # Titik kontrol acak untuk menciptakan lengkungan unik tiap gerakan
    cp1x = start_x + (target_x - start_x) * random.uniform(0.1, 0.4)
    cp1y = start_y + (target_y - start_y) * random.uniform(0.6, 0.9)
    
    # Menentukan jumlah langkah berdasarkan durasi (120 fps) agar lebih halus
    steps = max(3, int(duration * 120))
    t = np.linspace(0, 1, num=steps)
    
    for i in t:
        # Rumus Quadratic Bezier Curve
        qx = (1-i)**2 * start_x + 2*(1-i)*i * cp1x + i**2 * target_x
        qy = (1-i)**2 * start_y + 2*(1-i)*i * cp1y + i**2 * target_y
        
        pyautogui.moveTo(qx, qy)
        # Delay mikro agar gerakan smooth
        time.sleep(duration / steps if steps > 0 else 0)

def play_action(speed_mult, path):
    # Cek apakah file rekaman ada
    if not os.path.exists(path):
        print(f"❌ Error: File '{path}' tidak ditemukan!")
        return

    with open(path, "r") as f:
        aksi_list = json.load(f)
    aksi_list = coalesce_mouse_moves(aksi_list)

    print("▶️ MEMULAI PLAYBACK DALAM 3 DETIK...")
    print("💡 Tips: Arahkan kursor ke pojok kiri atas untuk STOP paksa.")
    time.sleep(3)

    waktu_terakhir = 0
    total = len(aksi_list)
    
    for idx, aksi in enumerate(aksi_list, start=1):
        # Hitung jeda antar aksi (tambahkan sedikit variasi waktu agar natural)
        jeda = (aksi["waktu"] - waktu_terakhir) * random.uniform(0.98, 1.02)
        jeda = jeda / speed_mult if speed_mult > 0 else jeda
        if jeda > 0:
            time.sleep(jeda)
        
        waktu_terakhir = aksi["waktu"]

        # 1. Gerakan Mouse
        if aksi["jenis"] == "mouse_move":
            target_x, target_y = aksi["detail"]["pos"]
            if VERBOSE:
                print(f"[{idx}/{total}] mouse_move -> ({target_x:.0f}, {target_y:.0f})")
            # Durasi mengikuti jeda + jarak agar gerakan tidak patah-patah
            cur_x, cur_y = pyautogui.position()
            dist = math.hypot(target_x - cur_x, target_y - cur_y)
            durasi_gerak = max(0.01, min(0.18, jeda + dist / 3000.0))
            bezier_move(target_x, target_y, duration=durasi_gerak)
        
        # 2. Klik Mouse
        elif aksi["jenis"] == "mouse_click":
            btn = Button.left if "left" in aksi["detail"]["button"] else Button.right
            if VERBOSE:
                state = "down" if aksi["detail"]["pressed"] else "up"
                pos_x, pos_y = aksi["detail"]["pos"]
                print(f"[{idx}/{total}] mouse_click {state} -> ({pos_x:.0f}, {pos_y:.0f}) {btn}")
            if aksi["detail"]["pressed"]:
                mouse_ctrl.press(btn)
            else:
                # Tambahkan sedikit variasi waktu penekanan tombol
                time.sleep(random.uniform(0.01, 0.03))
                mouse_ctrl.release(btn)
                
        # 3. Input Keyboard
        elif aksi["jenis"] == "key_press":
            k = aksi["detail"]["key"]
            if VERBOSE:
                print(f"[{idx}/{total}] key_press -> {k}")
            try:
                # Cek apakah itu tombol spesial (misal: Key.enter) atau karakter biasa
                if "Key." in k:
                    key_name = k.split(".")[1]
                    key_obj = getattr(Key, key_name)
                    kb_ctrl.press(key_obj)
                    kb_ctrl.release(key_obj)
                else:
                    # Menangani karakter string biasa
                    kb_ctrl.press(k)
                    kb_ctrl.release(k)
            except Exception as e:
                print(f"Gagal menekan tombol {k}: {e}")
        
        # 4. Scroll Mouse (trackpad 2 jari akan terekam sebagai scroll)
        elif aksi["jenis"] == "mouse_scroll":
            dx = aksi["detail"].get("dx", 0)
            dy = aksi["detail"].get("dy", 0)
            if VERBOSE:
                pos_x, pos_y = aksi["detail"].get("pos", (0, 0))
                print(f"[{idx}/{total}] mouse_scroll -> ({pos_x:.0f}, {pos_y:.0f}) dx={dx} dy={dy}")
            mouse_ctrl.scroll(dx, dy)

if __name__ == "__main__":
    try:
        json_files = []
        if os.path.exists(FOLDER_NAME):
            json_files = sorted(
                f for f in os.listdir(FOLDER_NAME) if f.lower().endswith(".json")
            )
        if json_files:
            print("File rekaman tersedia:")
            for i, fname in enumerate(json_files, start=1):
                print(f"  {i}. {fname}")
        file_input = input(
            f"Pilih file rekaman (nomor atau nama, default {FILE_NAME}): "
        ).strip()
        if file_input:
            if file_input.isdigit() and json_files:
                idx = int(file_input)
                if 1 <= idx <= len(json_files):
                    PATH = os.path.join(FOLDER_NAME, json_files[idx - 1])
                else:
                    print("Nomor file tidak valid, gunakan default.")
            else:
                PATH = os.path.join(FOLDER_NAME, file_input)

        speed_input = input(
            f"Masukkan SPEED_MULT (default {SPEED_MULT}, contoh 1.0/1.5/2.0): "
        ).strip()
        if speed_input:
            SPEED_MULT = float(speed_input)
        loop_input = input("Loop playback? (y/N): ").strip().lower()
        is_loop = loop_input == "y"

        while True:
            play_action(SPEED_MULT, PATH)
            print("✅ Playback Selesai!")
            if not is_loop:
                break
    except pyautogui.FailSafeException:
        print("\n🛑 Program dihentikan paksa (Fail-safe dipicu).")
    except KeyboardInterrupt:
        print("\n🛑 Program dihentikan oleh pengguna.")
