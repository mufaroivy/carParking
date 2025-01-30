import cv2
import pickle
import cvzone
import numpy as np
from datetime import datetime

# Constants
WIDTH, HEIGHT = 107, 48  # Dimensions of parking spots
THRESHOLD = 900  # Pixel count threshold to determine occupancy

# Initialize video capture
cap = cv2.VideoCapture(0)  # Default camera (webcam)

# Load parking positions from file
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
    print("Loaded parking positions:", posList)
except FileNotFoundError:
    print("Error: 'CarParkPos' file not found. Ensure the file exists and contains parking positions.")
    exit()

def preprocess_frame(frame):
    """
    Preprocess the input frame for parking space detection.
    - Convert to grayscale
    - Apply Gaussian blur
    - Perform adaptive thresholding
    - Apply median blur and dilation
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 1)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    median = cv2.medianBlur(thresh, 5)
    return cv2.dilate(median, np.ones((3, 3), np.uint8), iterations=1)

def check_parking_space(imgPro, frame):
    """
    Check the status of parking spaces (free or occupied) and overlay visual indicators.
    """
    space_counter = 0

    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y + HEIGHT, x:x + WIDTH]
        pixel_count = cv2.countNonZero(imgCrop)

        # Determine parking space status
        if pixel_count < THRESHOLD:
            color, status = (0, 255, 0), "Free"
            space_counter += 1
        else:
            color, status = (0, 0, 255), "Occupied"

        # Draw rectangle and status text for each parking spot
        cv2.rectangle(frame, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, 2)
        cvzone.putTextRect(frame, status, (x, y + 9), scale=0.5, thickness=1, offset=0, colorR=color)

    # Overlay free space count
    cvzone.putTextRect(
        frame,
        f'Free: {space_counter}/{len(posList)}',
        (100, 50),
        scale=3,
        thickness=5,
        offset=20,
        colorR=(0, 200, 0),
    )
    return space_counter

def display_current_time(frame):
    """
    Display the current time on the frame.
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    cvzone.putTextRect(frame, current_time, (500, 50), scale=1.5, thickness=2, offset=10, colorR=(255, 255, 255))

try:
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Unable to read camera frame.")
            break

        # Process frame and check parking spaces
        imgPro = preprocess_frame(frame)
        free_spaces = check_parking_space(imgPro, frame)

        # Display current time
        display_current_time(frame)

        # Show the frame
        cv2.imshow("Parking Lot", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting program.")
            break
finally:
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    print("Camera and resources released.")
