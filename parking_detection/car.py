import os
import cv2
import pickle
import cvzone
import numpy as np
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
WIDTH = int(os.getenv('WIDTH', 107))
HEIGHT = int(os.getenv('HEIGHT', 48))
THRESHOLD = int(os.getenv('THRESHOLD', 900))
PARKING_POSITIONS_FILE = os.getenv('PARKING_POSITIONS_FILE', 'CarParkPos')

# Initialize video capture
cap = cv2.VideoCapture(0)  # Default camera (webcam)

# Load parking positions from file
try:
    with open(PARKING_POSITIONS_FILE, 'rb') as f:
        posList = pickle.load(f)
    logger.info(f"Loaded parking positions: {posList}")
except FileNotFoundError:
    logger.error(f"Error: '{PARKING_POSITIONS_FILE}' file not found. Ensure the file exists and contains parking positions.")
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

def draw_parking_space(frame, pos, color, status):
    """
    Draw a rectangle and status text for a parking space.
    """
    x, y = pos
    cv2.rectangle(frame, pos, (x + WIDTH, y + HEIGHT), color, 2)
    cvzone.putTextRect(frame, status, (x, y + 9), scale=0.5, thickness=1, offset=0, colorR=color)

def update_free_space_count(frame, free_spaces, total_spaces):
    """
    Update the free space count overlay on the frame.
    """
    cvzone.putTextRect(
        frame,
        f'Free: {free_spaces}/{total_spaces}',
        (100, 50),
        scale=3,
        thickness=5,
        offset=20,
        colorR=(0, 200, 0),
    )

def display_current_time(frame):
    """
    Display the current time on the frame.
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    cvzone.putTextRect(frame, current_time, (500, 50), scale=1.5, thickness=2, offset=10, colorR=(255, 255, 255))

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
        draw_parking_space(frame, pos, color, status)

    # Update free space count
    update_free_space_count(frame, space_counter, len(posList))
    return space_counter

try:
    while True:
        success, frame = cap.read()
        if not success:
            logger.error("Error: Unable to read camera frame.")
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
            logger.info("Exiting program.")
            break
finally:
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    logger.info("Camera and resources released.")