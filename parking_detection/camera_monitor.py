import cv2
import pickle
import requests
import numpy as np
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PARKING_THRESHOLD = int(os.getenv('PARKING_THRESHOLD', 900))
PARKING_UPDATE_URL = os.getenv('PARKING_UPDATE_URL', 'http://localhost:5000/update_spaces')
PARKING_POSITIONS_FILE = os.getenv('PARKING_POSITIONS_FILE', 'CarParkPos')
FRAME_WIDTH, FRAME_HEIGHT = 107, 48

def load_parking_positions(file_path):
    """Load parking positions from the specified file."""
    try:
        with open(file_path, 'rb') as f:
            logger.info(f"Loaded parking positions from {file_path}.")
            return pickle.load(f)
    except FileNotFoundError:
        logger.error(f"Error: '{file_path}' file not found. Exiting...")
        exit()

def check_parking_space(img_pro, positions):
    """Check the status of parking spaces and return their statuses."""
    spaces = []
    for i, pos in enumerate(positions):
        x, y = pos
        img_crop = img_pro[y:y + FRAME_HEIGHT, x:x + FRAME_WIDTH]
        non_zero_count = cv2.countNonZero(img_crop)

        # Determine if the parking space is free or occupied
        status = "free" if non_zero_count < PARKING_THRESHOLD else "occupied"
        spaces.append({"id": i, "status": status})
    return spaces

def process_frame(frame, positions):
    """Process a single frame to detect parking spaces."""
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_threshold = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
    )
    img_median = cv2.medianBlur(img_threshold, 5)
    img_dilate = cv2.dilate(img_median, np.ones((3, 3), np.uint8), iterations=1)
    return img_dilate

def send_status_updates(spaces):
    """Send parking space status updates to the server."""
    try:
        response = requests.post(PARKING_UPDATE_URL, json={'spaces': spaces})
        if response.status_code != 200:
            logger.error(f"Error: Unable to update spaces on server. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {e}")

def process_video_feed():
    """Process the video feed to monitor parking spaces."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.error("Error: Unable to access the camera.")
        return

    positions = load_parking_positions(PARKING_POSITIONS_FILE)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                logger.error("Error: Unable to read camera frame.")
                break

            # Process the frame
            img_processed = process_frame(frame, positions)
            spaces = check_parking_space(img_processed, positions)

            # Send status updates
            send_status_updates(spaces)

            # Draw rectangles for parking spaces
            for pos in positions:
                x, y = pos
                cv2.rectangle(frame, (x, y), (x + FRAME_WIDTH, y + FRAME_HEIGHT), (0, 255, 0), 2)

            # Show the frame
            cv2.imshow("Parking Monitor", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Exiting monitoring...")
                break
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera and resources released.")

if __name__ == "__main__":
    process_video_feed()