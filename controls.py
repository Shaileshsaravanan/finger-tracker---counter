import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables to track the pinch state
pinch_start_time = None
is_dragging = False
screen_width, screen_height = pyautogui.size()

# Constants
PINCH_THRESHOLD = 0.05  # Threshold to consider it as a pinch
DRAG_THRESHOLD_TIME = 0.5  # Time in seconds to consider a long press

with mp_hands.Hands(
        max_num_hands=1,  # We track one hand for simplicity
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:
    
    while True:
        success, image = cap.read()
        if not success:
            continue
        
        # Flip the image horizontally for a selfie-view display
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get landmarks for index finger tip and thumb tip
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            
            # Calculate the distance between index finger tip and thumb tip
            pinch_distance = ((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2) ** 0.5
            
            # Convert hand landmarks to screen coordinates
            cursor_x = int(index_tip.x * screen_width)
            cursor_y = int(index_tip.y * screen_height)
            
            if pinch_distance < PINCH_THRESHOLD:
                if pinch_start_time is None:
                    # Start timing the pinch
                    pinch_start_time = time.time()
                else:
                    # Calculate how long the pinch has been held
                    pinch_duration = time.time() - pinch_start_time
                    
                    if pinch_duration > DRAG_THRESHOLD_TIME:
                        if not is_dragging:
                            pyautogui.mouseDown(button='left')
                            is_dragging = True
                        pyautogui.moveTo(cursor_x, cursor_y)
                    else:
                        pyautogui.moveTo(cursor_x, cursor_y)
            else:
                if pinch_start_time is not None:
                    pinch_duration = time.time() - pinch_start_time
                    if pinch_duration < DRAG_THRESHOLD_TIME:
                        pyautogui.click(button='left')
                    elif is_dragging:
                        pyautogui.mouseUp(button='left')
                    pinch_start_time = None
                    is_dragging = False
                else:
                    pyautogui.moveTo(cursor_x, cursor_y)
        
        # Display the image with landmarks
        cv2.imshow('Gesture Mouse Control', image)
        
        # Exit loop when 'Esc' is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()