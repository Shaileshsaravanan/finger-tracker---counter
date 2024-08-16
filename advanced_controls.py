import cv2
import mediapipe as mp
import pyautogui
import pygame
import pygetwindow as gw
import time

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables for gesture detection
pinch_start_time = None
is_dragging = False
last_position = None
screen_width, screen_height = pyautogui.size()
hand_in_frame = False
palm_open = False
palm_position = None
direction = None

# Constants
PINCH_THRESHOLD = 0.05  # Threshold to consider it a pinch
DRAG_THRESHOLD_TIME = 0.5  # Time in seconds to consider a long press
SMOOTHING_FACTOR = 0.2  # Smoothing factor for cursor movement
OPEN_PALM_THRESHOLD = 0.1  # Threshold to consider it an open palm
MOVEMENT_THRESHOLD = 0.05  # Movement threshold to detect direction change
CHECK_INTERVAL = 1.0  # Interval to check for palm movement (seconds)

# Initialize time tracking for palm movement
last_check_time = time.time()
last_palm_x = None

def show_app_switcher():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Size of the switcher window
    pygame.display.set_caption("Application Switcher")
    clock = pygame.time.Clock()
    
    # Get list of open windows
    try:
        open_windows = gw.getWindowsWithTitle('')
        if not open_windows:
            print("No open windows found.")
            pygame.quit()
            return
    except Exception as e:
        print(f"Error retrieving windows: {e}")
        pygame.quit()
        return

    font = pygame.font.Font(None, 36)
    app_labels = []
    for i, window in enumerate(open_windows):
        label = font.render(window.title, True, (255, 255, 255))
        app_labels.append((label, window))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for label, window in app_labels:
                    rect = label.get_rect(topleft=(20, 40 + 50 * app_labels.index((label, window))))
                    if rect.collidepoint(pos):
                        switch_to_window(window)
                        running = False
        
        screen.fill((0, 0, 0))  # Black background
        y = 40
        for label, _ in app_labels:
            screen.blit(label, (20, y))
            y += 50
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

def switch_to_window(window):
    try:
        window.activate()
        pyautogui.moveTo(screen_width / 2, screen_height / 2)  # Move the cursor to the center of the screen for better interaction
    except Exception as e:
        print(f"Error switching to window: {e}")

with mp_hands.Hands(
        max_num_hands=1,
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
            hand_in_frame = True
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get landmarks for palm base (wrist) and finger tips
            palm_base = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            finger_tips = [hand_landmarks.landmark[i] for i in [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                                               mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]]
            
            # Check if the palm is open
            finger_distances = [((palm_base.x - tip.x) ** 2 + (palm_base.y - tip.y) ** 2) ** 0.5 for tip in finger_tips]
            palm_open = all(dist > OPEN_PALM_THRESHOLD for dist in finger_distances)
            
            # Track palm position
            palm_x = int(palm_base.x * screen_width)
            palm_y = int(palm_base.y * screen_height)
            
            # Detect movement direction
            if palm_open:
                if time.time() - last_check_time > CHECK_INTERVAL:
                    if last_palm_x is not None:
                        movement = palm_x - last_palm_x
                        if abs(movement) > MOVEMENT_THRESHOLD:
                            direction = "right" if movement > 0 else "left"
                            if direction == "right":
                                pyautogui.hotkey('command', 'tab')  # For macOS
                                show_app_switcher()
                            elif direction == "left":
                                pyautogui.hotkey('command', 'shift', 'tab')  # For macOS
                                show_app_switcher()
                    last_palm_x = palm_x
                    last_check_time = time.time()
            else:
                last_palm_x = None
                direction = None

            # Convert hand landmarks to screen coordinates for cursor control
            cursor_x = int(palm_base.x * screen_width)
            cursor_y = int(palm_base.y * screen_height)

            # Stabilize the cursor position with smoothing, if the hand is detected
            if last_position is not None and hand_in_frame:
                cursor_x = int(SMOOTHING_FACTOR * cursor_x + (1 - SMOOTHING_FACTOR) * last_position[0])
                cursor_y = int(SMOOTHING_FACTOR * cursor_y + (1 - SMOOTHING_FACTOR) * last_position[1])
            last_position = (cursor_x, cursor_y)
            
            # Handle pinch gestures
            pinch_distance = ((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x) ** 2 +
                              (hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y) ** 2) ** 0.5
            if pinch_distance < PINCH_THRESHOLD:
                if pinch_start_time is None:
                    pinch_start_time = time.time()
                else:
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
        
        else:
            # If the hand is not detected, reset tracking
            hand_in_frame = False
            last_palm_x = None
            direction = None
            if last_position is not None:
                pyautogui.moveTo(last_position[0], last_position[1])
        
        # Display the image with landmarks
        cv2.imshow('Gesture Mouse Control', image)
        
        # Exit loop when 'Esc' is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()