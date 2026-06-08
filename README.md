# 🎙️ Smart AI Voice Control System for Dobot Robotic Arm (V4 - High Accuracy)

A lightweight, robust, and offline voice-controlled automation pipeline for the **Dobot** robotic arm. This system bypasses bloated, hardcoded dictionary mappings by combining local state-of-the-art neural speech recognition (**Faster-Whisper**) with a dynamic **3-Tier Intent Matching** algorithm.

---

## 🚀 Key Features

* **Offline Neural Speech-to-Text:** Powered by `faster-whisper`, running locally on your CPU using quantized `int8` weights for fast, low-latency, and internet-free transcriptions.
* **3-Tier Intent Resolver:** A multi-layered text matching algorithm that filters noise and ensures the robot never acts on ambiguous audio cues:
1. *Exact Match:* Instantaneous execution for clear commands.
2. *Substring Match:* Extracts core intent out of natural conversational sentences (e.g., "Please move **left** a bit").
3. *Fuzzy Scoring:* Uses string similarity metrics with custom first-letter prefix boosting to elegantly catch and correct speech-to-text spelling slips without needing hardcoded typo lists.


* **Macro Waypoint Memory:** Record spatial coordinates (`save`), clear them out (`clear`), and playback complex automated trajectories (`play`) dynamically via voice.

---

## 📂 Project Architecture

The repository is organized into distinct functional modules:

| File Name | Description |
| --- | --- |
| `voice_control.py` | The main execution engine. It manages the audio recording loop, applies the 3-Tier intent processing logic, and streams serial coordinates directly to the Dobot hardware. |
| `NLP.py` | The speech processing hub. It initializes the Whisper model globally into memory upon launch to eliminate recurring runtime reload delays. |
| `test_faster_whisper.py` | A diagnostic testing script used to isolate and verify local Whisper model loading and microphone sound-stage capture. |
| `requirements.txt` | Centralized python dependency manifest for reproducible environments. |

---

## 🛠️ Installation & Setup

### 1. Prerequisites

Ensure you have Python (version 3.8 to 3.11 recommended) installed alongside working serial ports for the Dobot connection.

### 2. Clone and Install Dependencies

Install the required packages using the centralized package manifest:

```bash
pip install -r requirements.txt

```

> ⚠️ **Note for Windows Users:** If `sounddevice` or `pydobot` throws serial communication blockages, ensure your hardware COM port matches the config variable (`PORT = "COM3"`) defined in `voice_control.py`.

---

## 🤖 Command Registry Matrix

The system dynamically condenses speech down to its structural roots. The table below represents the core dictionary footprint mapped directly into robotic actions:

| Core Intent | English Anchor | Thai Anchor | Executed Robot Action |
| --- | --- | --- | --- |
| **`left`** | `left` | `ซ้าย` | Translates relative step along the negative Y-axis. |
| **`right`** | `right` | `ขวา` | Translates relative step along the positive Y-axis. |
| **`up`** | `up` | `ขึ้น` | Adjusts height upward along the Z-axis. |
| **`down`** | `down` | `ลง` | Adjusts height downward along the Z-axis. |
| **`front`** | `front` / `forward` | `หน้า` | Extends the arm forward along the X-axis. |
| **`back`** | `back` | `หลัง` / `ถอย` | Retracts the arm backward along the X-axis. |
| **`suck`** | `suck` / `grab` | `ดูด` / `จับ` | Actuates the air pump end-effector (Suction ON). |
| **`release`** | `release` / `drop` | `ปล่อย` / `วาง` | Disengages the air pump end-effector (Suction OFF). |
| **`save`** | `save` / `keep` | `บันทึก` / `จำ` | Appends current `(X, Y, Z, R)` coordinates to volatile memory array. |
| **`play`** | `play` | `เล่น` / `วน` | Iterates and moves sequentially through all stored coordinates. |
| **`clear`** | `clear` / `clean` | `ล้าง` / `ลบ` | Purges the volatile waypoint memory array. |

---

## 💻 How to Run

### Step 1: Run Diagnostics (Optional)

To verify your local hardware and AI model configuration are sound, run the standalone diagnostic tool:

```bash
python test_ai.py

```

### Step 2: Start the Main Control Loop

Connect the Dobot to your machine via USB, verify its port designation, and boot the primary control environment:

```bash
python voice_control.py

```

### Step 3: Operating the Pipeline

1. The terminal will prompt you to press `Enter`.
2. Press `Enter`, speak your command clearly into your default microphone input (e.g., *"Move Left"*, *"ดูด"*, or *"Can you please go back"*).
3. Press `Enter` a second time to stop recording.
4. The backend pipeline will output transcription details, calculate your exact intention, display confidence scoring metrics, and safely guide the physical Dobot arm.

---

## 🧠 Algorithmic Insight: Intent Parsing Pipeline

```
[Voice Input] -> (Captured WAV) -> [Whisper Neural Model] -> (Raw Text String)
                                                                    │
   ┌────────────────────────────────────────────────────────────────┘
   ▼
[Clean Text Engine] -> Strips punctuation & symbols, tokenizes words
   │
   ├─► 1. Exact Match Check    ──> (Found) ──► [Execute Robotic Directive]
   │
   ├─► 2. Substring Sub-Check  ──> (Found) ──► [Execute Robotic Directive]
   │
   └─► 3. Fuzzy Ratio Scoring  ──> (Confidence Score >= 75%) ──► [Execute]
                                 ──> (Confidence Score < 75%)  ──► [Reject & Alert User]

```

> 💡 **Why this is resilient:** If the Whisper model accidentally transcribes the word `"right"` as `"write"`, the **Fuzzy Ratio Layer** will evaluate the proximity between the characters, note that the prefix length matches, calculate a high confidence match score, and flawlessly map it to the **`right`** movement block anyway—all without needing manual mapping bloat.
