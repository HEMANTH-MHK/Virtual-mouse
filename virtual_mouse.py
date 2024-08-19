import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hand_detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils

# Get screen dimensions
screen_width, screen_height = pyautogui.size()

# Initialize variables
index_y = 0
smooth_factor = 5
previous_time = 0

# Start capturing video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Get frame dimensions
    frame_height, frame_width, _ = frame.shape

    # Convert the frame color to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            # Draw hand landmarks on the frame
            drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # Extract landmarks and map them to screen coordinates
            landmarks = hand.landmark
            index_x, index_y = None, None
            thumb_x, thumb_y = None, None
            middle_x, middle_y = None, None


            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                # Index finger tip
                if id == 8:
                    index_x = np.interp(x, (0, frame_width), (0, screen_width))
                    index_y = np.interp(y, (0, frame_height), (0, screen_height))
                    cv2.circle(frame, (x, y), 10, (0, 255, 255), cv2.FILLED)

                # Thumb tip
                if id == 4:
                    thumb_x = np.interp(x, (0, frame_width), (0, screen_width))
                    thumb_y = np.interp(y, (0, frame_height), (0, screen_height))
                    cv2.circle(frame, (x, y), 10, (0, 255, 255), cv2.FILLED)
                    
                if id == 12:  # Middle finger tip
                    middle_x = np.interp(x, (0, frame_width), (0, screen_width))
                    middle_y = np.interp(y, (0, frame_height), (0, screen_height))
                    cv2.circle(frame, (x, y), 10, (0, 255, 255), cv2.FILLED)

                    
               

            if index_x is not None and thumb_x is not None:
                # Move the mouse cursor smoothly
                pyautogui.moveTo(index_x, index_y, duration=0.1)

                # Check if thumb and index finger are close enough for a click
                if abs(index_y - thumb_y) < 20:
                    pyautogui.click()
                    time.sleep(0.3)  # Add a slight delay to prevent multiple clicks
                    
                if abs(index_y - middle_y) < 20:
                    screenshot = pyautogui.screenshot()
                    screenshot.save('ss_virtual.png')
                    time.sleep(0.3)

    # Calculate and display FPS (frames per second)
    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Virtual Mouse', frame)

    # Break the loop if ESC is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

