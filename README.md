# 🤖 Rogue Defense Auto-Player AI

An automated player system for **Rogue Defense** (a Rogue-like action game). It leverages **YOLO** for real-time computer vision and UI/card detection, **Ollama (Qwen2.5-Coder)** for LLM-driven decision-making, and **ADB (Android Debug Bridge)** for real-time device control.

---
[![Watch Video Project](./thumbnail.png)](./Video%20Project.mp4)
## 🌟 Key Features

- **Automated Detection (YOLO Detector):** Accurately detects system buttons (`StartButton`, `Back`, `Confirm`), special event cards (`ElitePick`), and available skill options on screen.
- **Auto Navigation & System Interaction:** Instantly taps navigation buttons as soon as they appear.
- **Special Event Handling (`ElitePick`):** Prioritizes selecting `ElitePick` whenever visible, followed by an immediate 1-second pause to handle screen transitions or confirm prompts.
- **Smart AI Skill Selection (Ollama LLM):**
  - Triggers decision-making **only when exactly 3 skills** are detected on screen.
  - Sorts skill cards vertically by their actual screen coordinates to ensure 100% accurate tap indexing.
  - Combines LLM reasoning with a **Python Validator fallback** to guarantee strict adherence to the skill priority list (preventing LLM hallucinations).
- **Noise Filtering:** Automatically filters out unwanted classes (e.g., class `X`).

---

## 🛠 Tech Stack & Architecture

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Vision** | YOLO (`best.pt`) + OpenCV | Real-time object detection for cards, buttons, and UI |
| **Stream** | Scrcpy Window Handler | Live mirror feed capture from Android device to PC |
| **Brain (AI)** | Ollama (`qwen2.5-coder`) | Analyzes available skills and outputs optimal card selection |
| **Control** | ADB Controller | Sends scaled `tap` commands to target device coordinates |

---

## 📋 Skill Priority Order

Skills are selected based on the following strict priority ranking (from highest to lowest):

1. 🥇 **Bullet**
2. 🥈 **Electro**
3. 🥉 **Laser**
4. **Traction**
5. **Thunder**
6. **FireWheel**
7. **Field**
8. **Mortar**

> ⚠️ **Note:** The system strictly avoids picking `EliteAd` under any circumstance.

---

## 📂 Project Structure

```text
.
├── agent.py          # AI logic handler (Ollama + Python Validator override)
├── controller.py     # ADB device controller (scaled coordinate tap commands)
├── detector.py       # Object detection module using YOLO (best.pt)
├── scrcpy_window.py # Frame grabber from the Scrcpy window
├── main.py           # Main application loop and execution flow
├── best.pt           # Trained YOLO model weights for Rogue Defense
└── README.md         # Project documentation
