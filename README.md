
# Gesture Control System 🎮🖐️

A Python-based project that allows users to control their computer with **hand gestures** using **OpenCV** and **MediaPipe**.  
No need for a mouse or keyboard — just gestures!

---

## ✨ Features
- ✊ **Fist** → Left Click  
- 🖐️ **Open Palm** → Right Click  
- ✌️ **Peace Sign** → Scroll  
- ☝️ **Point Up** → Play / Pause media  
- 👇 **Point Down** → Next Track  
- 🤏 **Pinch (Thumb + Index)** → Adjust Volume  
- ✋ **Palm Up / Down** → Adjust Screen Brightness  

---

## 🛠️ Tech Stack
- Python 3.11  
- OpenCV  
- MediaPipe  
- PyAutoGUI  
- Pycaw (for volume control)  
- Screen Brightness Control  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/gesture-control-system.git
cd gesture-control-system
```

### 2️⃣ Create a Virtual Environment (venv)
```bash
python -m venv venv
```

Activate it:  
- **Windows (PowerShell):**
```bash
venv\Scripts\activate
```
- **Linux / macOS:**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, here’s the list of packages:
```bash
pip install opencv-python mediapipe pyautogui comtypes pycaw screen-brightness-control numpy
```

### 4️⃣ Run the Project
```bash
python gesture_control.py
```

Press **q** to quit the program.

---

## 📂 Project Structure
```
gesture-control-system/
│-- gesture_control.py      # Main program
│-- requirements.txt        # List of dependencies
│-- README.md               # Project documentation
```

---

## 🚀 Demo
🎥 Add your demo video or GIF here (you can upload to LinkedIn, YouTube, or add directly).

---

## 📌 Future Improvements
- Add multi-hand support  
- Improve gesture recognition accuracy  
- Add custom gesture mapping (user-defined actions)  

---

## 🙌 Author
Developed by **Kanike Thirumalesh**  
Feel free to connect with me on [LinkedIn](https://www.linkedin.com) 🚀  

