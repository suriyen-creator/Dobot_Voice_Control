# voice_control.py (V4: High Accuracy + 3-Tier Matching)
import time
import wave
import numpy as np
import sounddevice as sd
from pydobot import Dobot
from difflib import SequenceMatcher
import re # <--- เพิ่มไลบรารีจัดการข้อความ

# เรียกใช้ฟังก์ชันถอดเสียง
from NLP import transcribe_wav 

# --- การตั้งค่า ---
PORT = "COM3"
STEP = 20
MEMORY_POINTS = []

# ==========================================
# 🧠 1. Core Commands (เพิ่มคำทับศัพท์ที่คนไทยชอบพูด)
# ==========================================
# 🧠 แผนที่คำสั่งหลัก (เหลือแค่อย่างละคำ ไทย-อังกฤษ เพื่อเชื่อมเข้าฟังก์ชันหุ่นยนต์)
CORE_COMMANDS = {
    "left":    ["left", "ซ้าย"],
    "right":   ["right", "ขวา"],
    "up":      ["up", "ขึ้น"],
    "down":    ["down", "ลง"],
    "front":   ["front", "หน้า"],
    "back":    ["back", "หลัง"],
    "suck":    ["suck", "ดูด"],
    "release": ["release", "ปล่อย"],
    "save":    ["save", "บันทึก"],
    "play":    ["play", "เล่น"],
    "clear":   ["clear", "ล้าง"]
}
# ==============================
# 🧠 2. ฟังก์ชันสมองกล (3-Tier Accuracy)
# ==============================
def clean_text(text: str) -> list:
    """ทำความสะอาดข้อความ ลบอักขระพิเศษ และแยกคำ"""
    # อนุญาตเฉพาะตัวอักษรไทย อังกฤษ และช่องว่าง (ลบพวกเครื่องหมายวรรคตอน)
    cleaned = re.sub(r'[^\w\sก-๙]', '', text.lower())
    return cleaned.split()

def get_intent(text: str, threshold: float = 0.75):
    """
    วิเคราะห์คำสั่งแบบ 3 ลำดับขั้น เพื่อความแม่นยำสูงสุด
    """
    if not text: return None
    
    words = clean_text(text)
    if not words: return None

    print(f"🔍 วิเคราะห์คำที่ผ่านการคลีน: {words}")
    
    best_cmd = None
    max_score = 0.0

    for word in words:
        for cmd, keywords in CORE_COMMANDS.items():
            for kw in keywords:
                # 🎯 ขั้นที่ 1: ตรงเป๊ะ (Exact Match) -> ให้ความมั่นใจ 100%
                if word == kw:
                    print(f"🎯 เจอคำตรงเป๊ะ: '{kw}'")
                    return cmd
                
                # 🔍 ขั้นที่ 2: ซ่อนอยู่ในคำ (Substring Match) เช่น 'เลี้ยวซ้าย' มีคำว่า 'ซ้าย'
                # เช็คความยาวด้วย เพื่อป้องกันตัวอักษรเดียวไปซ้อนในคำอื่น (เช่น 'อ' ไปซ้อนใน 'ลง')
                if kw in word and len(kw) >= 3: 
                    score = 0.90
                else:
                    # 🧮 ขั้นที่ 3: คำเพี้ยน (Fuzzy Match)
                    score = SequenceMatcher(None, word, kw).ratio()
                    # Bonus Rule: ตัวอักษรนำหน้าตรงกัน และความยาวคำไม่ต่างกันมาก
                    if len(word) > 0 and len(kw) > 0 and word[0] == kw[0]:
                        score += 0.1
                    if abs(len(word) - len(kw)) <= 1:
                        score += 0.05

                # เก็บค่าคะแนนสูงสุดไว้
                if score > max_score:
                    max_score = score
                    best_cmd = cmd

    # สรุปผลลัพธ์
    if max_score >= threshold:
        print(f"✨ สรุปเจตนา: '{best_cmd}' (ความมั่นใจ: {max_score*100:.1f}%)")
        return best_cmd

    print(f"❌ ความมั่นใจต่ำเกินไป ({max_score*100:.1f}%) ยกเลิกคำสั่งเพื่อความปลอดภัย")
    return None

# ==============================
# 3) ส่วนควบคุม Dobot
# ==============================
def get_xyzr(device):
    pose = device.pose()
    return pose[:4]

def move_relative(device, direction, step=STEP):
    vec = {
        "left":  (0, -1,  0, 0), "right": (0,  1,  0, 0),
        "front": (1,  0,  0, 0), "back":  (-1, 0,  0, 0),
        "up":    (0,  0,  1, 0), "down":  (0,  0, -1, 0),
    }.get(direction)

    if vec:
        dx, dy, dz, dr = vec
        x, y, z, r = get_xyzr(device)
        device.move_to(x + dx*step, y + dy*step, z + dz*step, r + dr*step)
        print(f"✅ ขยับ {direction}")

def connect_dobot(port=PORT):
    print(f"🚀 เชื่อมต่อ {port}...")
    try:
        device = Dobot(port=port, verbose=False)
        time.sleep(1)
        try:
            device.ser.reset_input_buffer()
            device.ser.reset_output_buffer()
        except: pass
        print("✅ Ready!")
        return device
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ==============================
# 4) ฟังก์ชันอัดเสียง
# ==============================
def record_until_enter(filename: str = "record.wav", samplerate: int = 16000, channels: int = 1) -> str:
    print("\n" + "="*40)
    input("🎤 กด Enter เพื่ออัดเสียง... (แล้วพูดคำสั่ง)")
    print("⏺️  กำลังรับฟัง... (พูดจบแล้วกด Enter)")
    frames = []

    def callback(indata, frames_count, time_info, status):
        if status: print(status)
        frames.append(indata.copy())

    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback)
    stream.start()
    input()
    stream.stop()
    stream.close()

    audio_data = np.concatenate(frames, axis=0) if frames else np.zeros((1, channels), dtype=np.float32)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
    
    return filename

# ==============================
# 5) Main Loop
# ==============================
def main():
    device = connect_dobot(PORT)
    if not device: return

    print("\n🎧 Voice V4 (High Accuracy Mode)")
    print("ระบบพร้อม! กรองคำแม่นยำขึ้น ป้องกันหุ่นขยับมั่ว")

    try:
        while True:
            wav = record_until_enter()
            text = transcribe_wav(wav)
            
            if not text: 
                print("🤷‍♂️ ไม่ได้ยินเสียงพูดเลย...")
                continue

            print(f"🗣️  ถอดเสียงได้: '{text}'")
            cmd = get_intent(text) # <--- เรียกใช้ระบบวิเคราะห์ตัวใหม่

            if not cmd:
                print("🤔 ไม่แน่ใจว่าสั่งอะไร (ลองพูดให้ชัดขึ้นอีกนิด)")
                continue

            print(f"🤖 ปฏิบัติการ: {cmd.upper()}")

            if cmd in ["left", "right", "up", "down", "front", "back"]:
                move_relative(device, cmd, STEP)
            elif cmd == "suck":
                device.suck(True)
                print("💨 ดูดจ๊วบ!")
            elif cmd == "release":
                device.suck(False)
                print("🍃 ปล่อยของ")
            elif cmd == "save":
                pos = get_xyzr(device)
                MEMORY_POINTS.append(pos)
                print(f"💾 จำจุดที่ {len(MEMORY_POINTS)}")
            elif cmd == "clear":
                MEMORY_POINTS.clear()
                print("🗑️ ล้างความจำทั้งหมดแล้ว")
            elif cmd == "play":
                if not MEMORY_POINTS:
                    print("⚠️ ไม่มีข้อมูลจุดที่บันทึกไว้")
                else:
                    print(f"▶️ เริ่มทำงานตามจุด {len(MEMORY_POINTS)} จุด...")
                    for i, pos in enumerate(MEMORY_POINTS):
                        print(f"   -> ไปยังจุดที่ {i+1}")
                        device.move_to(pos[0], pos[1], pos[2], pos[3], wait=True)
                    print("✅ ทำงานเสร็จสิ้น")

    except KeyboardInterrupt:
        print("\n👋 ยกเลิกการทำงาน")
    finally:
        if device: device.close()

if __name__ == "__main__":
    main()