import cv2
import mediapipe as mp
import numpy as np
import time
import os

# Try to import pyautogui, fallback to demo mode if it fails
try:
    import pyautogui
    DEMO_MODE = False
    print("PyAutoGUI loaded successfully - Full functionality available")
except Exception as e:
    DEMO_MODE = True
    print(f"PyAutoGUI failed to load: {e}")
    print("Running in DEMO MODE - Hand tracking only, no screen control")

class GestureController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Screen dimensions
        if not DEMO_MODE:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = 1920, 1080  # Default screen size for demo
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Gesture states
        self.prev_x, self.prev_y = 0, 0
        self.click_debounce = 0
        self.scroll_debounce = 0
        self.gesture_debounce = 0
        
        # Smoothing parameters
        self.smoothing_factor = 0.7
        
        # Gesture zones (based on camera frame)
        self.camera_width = 640
        self.camera_height = 480
        
        print("Gesture Controller initialized!")
        if DEMO_MODE:
            print("DEMO MODE: Hand tracking visualization only")
            print("To use full functionality, run this on a local machine with display access")
        else:
            print("FULL MODE: Screen control enabled")
        print("Controls:")
        print("- Move your hand to control the cursor")
        print("- Make a fist to left click")
        print("- Show your palm to right click")
        print("- Use two fingers (peace sign) to scroll")
        print("- Point up/down with index finger for media controls")
        print("- Press 'q' to quit")
        
    def get_hand_landmarks(self, frame):
        """Extract hand landmarks from frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results
    
    def calculate_distance(self, point1, point2):
        """Calculate distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_fist(self, landmarks):
        """Detect if hand is making a fist"""
        # Check if all fingertips are below their respective PIP joints
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        finger_pips = [3, 6, 10, 14, 18]  # PIP joints
        
        fingers_down = 0
        
        # Check thumb (different logic due to orientation)
        if landmarks[4].x < landmarks[3].x:  # Thumb tip left of thumb IP
            fingers_down += 1
            
        # Check other fingers
        for tip, pip in zip(finger_tips[1:], finger_pips[1:]):
            if landmarks[tip].y > landmarks[pip].y:  # Tip below PIP
                fingers_down += 1
        
        return fingers_down >= 4
    
    def is_open_palm(self, landmarks):
        """Detect if hand is showing open palm"""
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        fingers_up = 0
        
        # Check thumb
        if landmarks[4].x > landmarks[3].x:  # Thumb tip right of thumb IP
            fingers_up += 1
            
        # Check other fingers
        for tip, pip in zip(finger_tips[1:], finger_pips[1:]):
            if landmarks[tip].y < landmarks[pip].y:  # Tip above PIP
                fingers_up += 1
        
        return fingers_up >= 4
    
    def is_peace_sign(self, landmarks):
        """Detect peace sign (two fingers up)"""
        # Index and middle finger up, others down
        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y
        
        return index_up and middle_up and ring_down and pinky_down
    
    def is_pointing_up(self, landmarks):
        """Detect index finger pointing up"""
        index_up = landmarks[8].y < landmarks[6].y
        middle_down = landmarks[12].y > landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y
        
        return index_up and middle_down and ring_down and pinky_down
    
    def is_pointing_down(self, landmarks):
        """Detect index finger pointing down"""
        # This is more complex - we need to check the angle
        index_tip = landmarks[8]
        index_mcp = landmarks[5]
        
        # If index tip is significantly below MCP, it's pointing down
        pointing_down = (index_tip.y - index_mcp.y) > 0.1
        
        # Other fingers should be down
        middle_down = landmarks[12].y > landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y
        
        return pointing_down and middle_down and ring_down and pinky_down
    
    def control_cursor(self, landmarks, frame_shape):
        """Control cursor based on hand position"""
        # Use wrist position for cursor control
        wrist = landmarks[0]
        
        # Convert hand coordinates to screen coordinates
        x = int(wrist.x * self.screen_width)
        y = int(wrist.y * self.screen_height)
        
        # Apply smoothing
        if hasattr(self, 'smooth_x') and hasattr(self, 'smooth_y'):
            self.smooth_x = int(self.smoothing_factor * self.smooth_x + (1 - self.smoothing_factor) * x)
            self.smooth_y = int(self.smoothing_factor * self.smooth_y + (1 - self.smoothing_factor) * y)
        else:
            self.smooth_x, self.smooth_y = x, y
        
        # Move cursor (only in full mode)
        if not DEMO_MODE:
            pyautogui.moveTo(self.smooth_x, self.smooth_y)
        return self.smooth_x, self.smooth_y
    
    def handle_gestures(self, landmarks):
        """Handle different gesture commands"""
        current_time = time.time()
        
        # Left click - Fist gesture
        if self.is_fist(landmarks) and current_time - self.click_debounce > 1.0:
            if not DEMO_MODE:
                pyautogui.click()
            self.click_debounce = current_time
            return "Left Click" + (" (DEMO)" if DEMO_MODE else "")
        
        # Right click - Open palm
        elif self.is_open_palm(landmarks) and current_time - self.click_debounce > 1.0:
            if not DEMO_MODE:
                pyautogui.rightClick()
            self.click_debounce = current_time
            return "Right Click" + (" (DEMO)" if DEMO_MODE else "")
        
        # Scroll - Peace sign
        elif self.is_peace_sign(landmarks) and current_time - self.scroll_debounce > 0.3:
            # Use hand movement for scroll direction
            wrist = landmarks[0]
            y = wrist.y
            
            if hasattr(self, 'prev_scroll_y'):
                if y < self.prev_scroll_y - 0.05:  # Hand moved up
                    if not DEMO_MODE:
                        pyautogui.scroll(3)
                    self.scroll_debounce = current_time
                elif y > self.prev_scroll_y + 0.05:  # Hand moved down
                    if not DEMO_MODE:
                        pyautogui.scroll(-3)
                    self.scroll_debounce = current_time
            
            self.prev_scroll_y = y
            return "Scroll Mode" + (" (DEMO)" if DEMO_MODE else "")
        
        # Media controls
        elif self.is_pointing_up(landmarks) and current_time - self.gesture_debounce > 2.0:
            if not DEMO_MODE:
                pyautogui.press('space')  # Play/Pause
            self.gesture_debounce = current_time
            return "Play/Pause" + (" (DEMO)" if DEMO_MODE else "")
        
        elif self.is_pointing_down(landmarks) and current_time - self.gesture_debounce > 2.0:
            if not DEMO_MODE:
                pyautogui.press('right')  # Next
            self.gesture_debounce = current_time
            return "Next Track" + (" (DEMO)" if DEMO_MODE else "")
        
        return "Tracking"
    
    def run(self):
        """Main control loop"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Get hand landmarks
                results = self.get_hand_landmarks(frame)
                
                gesture_status = "No Hand Detected"
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                        
                        # Control cursor
                        cursor_x, cursor_y = self.control_cursor(hand_landmarks.landmark, frame.shape)
                        
                        # Show cursor position in demo mode
                        if DEMO_MODE:
                            cv2.putText(frame, f"Cursor: ({cursor_x}, {cursor_y})", (10, 70), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        
                        # Handle gestures
                        gesture_status = self.handle_gestures(hand_landmarks.landmark)
                
                # Display status
                cv2.putText(frame, f"Status: {gesture_status}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show instructions
                instructions = [
                    "Fist: Left Click | Palm: Right Click",
                    "Peace Sign: Scroll | Point Up: Play/Pause",
                    "Point Down: Next | Press 'q' to quit"
                ]
                
                for i, instruction in enumerate(instructions):
                    cv2.putText(frame, instruction, (10, frame.shape[0] - 90 + i*30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Gesture Controller', frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("Gesture Controller stopped.")

if __name__ == "__main__":
    # Initialize and run the gesture controller
    controller = GestureController()
    controller.run()