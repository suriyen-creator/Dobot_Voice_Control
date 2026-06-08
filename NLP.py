# NLP.py (ฉบับ Faster-Whisper: แม่นยำสูง + Offline)
import os
from faster_whisper import WhisperModel

# ==========================================
# 🚀 1. โหลดโมเดล AI (ทำแค่ครั้งเดียวตอนเริ่มรัน)
# ==========================================
print("⏳ [NLP] กำลังปลุกสมองกล Whisper (อาจใช้เวลาไม่กี่วินาที)...")
try:
    # ใช้ "tiny" เพื่อความรวดเร็วสูงสุด (ถ้าอยากให้ฉลาดขึ้นอีกให้เปลี่ยนเป็น "base" หรือ "small")
    # device="cpu", compute_type="int8" ช่วยให้รันบนคอมพิวเตอร์ทั่วไปได้โดยไม่กินสเปค
    MODEL_SIZE = "tiny" 
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    print(f"✅ [NLP] โหลดโมเดล Whisper ({MODEL_SIZE}) สำเร็จ! หูทิพย์พร้อมทำงาน")
except Exception as e:
    print(f"❌ [NLP] ปลุกสมองกลไม่สำเร็จ: {e}")
    model = None

# ==========================================
# 🎧 2. ฟังก์ชันถอดเสียง (เรียกใช้ซ้ำได้รวดเร็ว)
# ==========================================
def transcribe_wav(filename="record.wav"):
    """
    รับไฟล์เสียงและแปลงเป็นข้อความด้วย AI
    """
    if model is None:
        print("⚠️ [NLP] โมเดล AI พังอยู่ ไม่สามารถแปลเสียงได้")
        return ""

    if not os.path.exists(filename):
        print(f"❌ [NLP] หาไฟล์เสียง '{filename}' ไม่เจอ")
        return ""

    print("🧠 [NLP] AI กำลังประมวลผลเสียง...")
    
    try:
        # beam_size=5 ช่วยให้ AI ลองสร้างประโยคหลายๆ แบบแล้วเลือกอันที่สมเหตุสมผลที่สุด
        segments, info = model.transcribe(filename, beam_size=5)
        
        # รวบรวมข้อความจากทุกท่อนเสียง (เผื่อพูดประโยคยาว)
        text_parts = [segment.text for segment in segments]
        result_text = " ".join(text_parts).strip()
        
        if result_text:
            print(f"🎯 [NLP] AI ได้ยินว่า: '{result_text}' (ภาษา: {info.language}, ความมั่นใจ: {info.language_probability*100:.1f}%)")
        
        return result_text
        
    except Exception as e:
        print(f"❌ [NLP] เกิดข้อผิดพลาดขณะแปลเสียง: {e}")
        return ""