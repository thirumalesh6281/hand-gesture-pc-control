import cv2
import numpy as np
import time
import os
import math

# Try to import mediapipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True  
    print("✅ MediaPipe loaded successfully")
except (ImportError, OSError) as e:
    MEDIAPIAPE_AVAILABLE = False
    print(f"❌ MediaPipe failed to load: {e}")
    exit(1)

# Try to import pyautogui
try:
    import pyautogui
    DEMO_MODE = False
    print("✅ PyAutoGUI loaded successfully - Full functionality available")
except Exception as e:
    DEMO_MODE = True
    print(f"⚠️ PyAutoGUI failed to load: {e}")
    print("Running in DEMO MODE - Hand tracking only")

# Extra dependencies
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    import screen_brightness_control as sbc

    # Volume setup
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_interface = interface.QueryInterface(IAudioEndpointVolume)
    EXTRA_FEATURES = True
    print("✅ Volume & Brightness control available")
except Exception as e:
    volume_interface = None
    EXTRA_FEATURES = False
    print(f"⚠️ Extra features disabled: {e}")


class GestureController:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Screen setup
        if not DEMO_MODE:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = 1920, 1080

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Debounce timers
        self.click_debounce = 0
        self.scroll_debounce = 0
        self.gesture_debounce = 0
        self.volume_debounce = 0
        self.brightness_debounce = 0

        # Smoothing
        self.smoothing_factor = 0.7
        self.smooth_x, self.smooth_y = 0, 0

        print("\n🎮 Controls:")
        print("👊 Fist: Left Click")
        print("🖐️ Open Palm: Right Click")
        print("✌️ Peace Sign: Scroll")
        print("☝️ Point Up: Play/Pause")
        print("👇 Point Down: Next Track")
        if EXTRA_FEATURES:
            print("🤏 Pinch (Thumb+Index): Volume Control")
            print("✋ Palm Height: Brightness Control")
        print("Press 'q' to quit\n")

    def get_hand_landmarks(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def calculate_distance(self, point1, point2):
        return math.hypot(point1[0] - point2[0], point1[1] - point2[1])

    def is_fist(self, lm):  
        return (lm[8].y > lm[6].y and lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and lm[20].y > lm[18].y)

    def is_open_palm(self, lm):
        return (lm[8].y < lm[6].y and lm[12].y < lm[10].y and
                lm[16].y < lm[14].y and lm[20].y < lm[18].y)

    def is_peace_sign(self, lm):
        return (lm[8].y < lm[6].y and lm[12].y < lm[10].y and
                lm[16].y > lm[14].y and lm[20].y > lm[18].y)

    def is_pointing_up(self, lm):
        return (lm[8].y < lm[6].y and lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and lm[20].y > lm[18].y)

    def is_pointing_down(self, lm):
        return (lm[8].y > lm[6].y and lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and lm[20].y > lm[18].y)

    def control_cursor(self, landmarks):
        wrist = landmarks[0]
        x = int(wrist.x * self.screen_width)
        y = int(wrist.y * self.screen_height)

        self.smooth_x = int(self.smoothing_factor * self.smooth_x + (1 - self.smoothing_factor) * x)
        self.smooth_y = int(self.smoothing_factor * self.smooth_y + (1 - self.smoothing_factor) * y)

        if not DEMO_MODE:
            pyautogui.moveTo(self.smooth_x, self.smooth_y)

        return self.smooth_x, self.smooth_y

    def handle_gestures(self, lm):
        current_time = time.time()
        
        # Media controls
        if self.is_pointing_up(lm) and current_time - self.gesture_debounce > 2.0:
            if not DEMO_MODE: pyautogui.press('space')
            self.gesture_debounce = current_time
            return "Play/Pause"
        
        elif self.is_pointing_down(lm) and current_time - self.gesture_debounce > 2.0:
            if not DEMO_MODE: pyautogui.press('right')
            self.gesture_debounce = current_time
            return "Next Track"
        
        # Mouse clicks
        elif self.is_fist(lm) and current_time - self.click_debounce > 1.0:
            if not DEMO_MODE: pyautogui.click()
            self.click_debounce = current_time
            return "Left Click"
        
        elif self.is_open_palm(lm) and current_time - self.click_debounce > 1.0:
            if not DEMO_MODE: pyautogui.rightClick()
            self.click_debounce = current_time
            return "Right Click"
        
        # Scroll
        elif self.is_peace_sign(lm) and current_time - self.scroll_debounce > 0.3:
            y = lm[0].y
            if hasattr(self, 'prev_scroll_y'):
                if y < self.prev_scroll_y - 0.05:
                    if not DEMO_MODE: pyautogui.scroll(3)
                elif y > self.prev_scroll_y + 0.05:
                    if not DEMO_MODE: pyautogui.scroll(-3)
            self.prev_scroll_y = y
            self.scroll_debounce = current_time
            return "Scroll"
        
        # Continuous controls
        if EXTRA_FEATURES:
            # Pinch for volume
            thumb = (lm[4].x, lm[4].y)
            index = (lm[8].x, lm[8].y)
            dist = self.calculate_distance(thumb, index)
            
            if dist < 0.15: 
                vol_level = min(max(dist * 5, 0.0), 1.0)
                volume_interface.SetMasterVolumeLevelScalar(vol_level, None)
                return f"Volume: {int(vol_level * 100)}%"
            
        # Palm height for brightness
        if current_time - self.brightness_debounce > 0.2:
            palm_y = lm[0].y  # wrist landmark
            # Higher hand = more brightness, lower hand = less brightness
            brightness = int(np.interp(palm_y, [0.0, 1.0], [100, 10]))
            try:
                sbc.set_brightness(brightness)
                self.brightness_debounce = current_time
                return f"Brightness: {brightness}%"
            except Exception as e:
                return f"⚠️ Brightness error: {e}"

        
        return "Tracking"

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                results = self.get_hand_landmarks(frame)
                gesture_status = "No Hand Detected"

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        self.control_cursor(hand_landmarks.landmark)
                        gesture_status = self.handle_gestures(hand_landmarks.landmark)

                cv2.putText(frame, f"Status: {gesture_status}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Gesture Controller', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print("🛑 Stopped Gesture Controller")


if __name__ == "__main__":
    GestureController().run()
