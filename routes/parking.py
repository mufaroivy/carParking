import cv2
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parking spot dimensions
WIDTH = 26
HEIGHT = 58

# File to store parking positions
PARKING_POSITIONS_FILE = 'CarParkPos'

def load_positions():
    """
    Load existing parking positions from a file.
    If the file doesn't exist, return an empty list.
    """
    try:
        with open(PARKING_POSITIONS_FILE, 'rb') as f:
            positions = pickle.load(f)
            logger.info("Loaded parking positions from file.")
            return positions
    except FileNotFoundError:
        logger.info("No existing positions found. Starting fresh.")
        return []

def save_positions(positions):
    """
    Save the parking positions to a file.
    """
    with open(PARKING_POSITIONS_FILE, 'wb') as f:
        pickle.dump(positions, f)
    logger.info("Parking positions saved.")

def add_spot(positions, x, y):
    """
    Add a new parking spot at the specified coordinates.
    """
    positions.append((x, y))
    logger.info(f"Added spot at {x}, {y}")
    save_positions(positions)

def remove_spot(positions, x, y):
    """
    Remove a parking spot at the specified coordinates.
    """
    for i, pos in enumerate(positions):
        x1, y1 = pos
        if x1 < x < x1 + WIDTH and y1 < y < y1 + HEIGHT:  # Check if click is within a spot
            positions.pop(i)
            logger.info(f"Removed spot at {x1}, {y1}")
            save_positions(positions)
            break

def mouseClick(events, x, y, flags, params):
    """
    Handle mouse click events to add or remove parking spots.

    - Left-click to add a new parking spot.
    - Right-click to remove an existing parking spot.
    """
    positions = params['positions']
    if events == cv2.EVENT_LBUTTONDOWN:  # Add a parking spot
        add_spot(positions, x, y)
    elif events == cv2.EVENT_RBUTTONDOWN:  # Remove a parking spot
        remove_spot(positions, x, y)

def main():
    """
    Main function to run the parking spot management application.
    """
    # Load existing parking positions
    posList = load_positions()

    # Initialize video capture
    cap = cv2.VideoCapture(0)  # Use the default camera

    if not cap.isOpened():
        logger.error("Error: Could not open video capture.")
        exit()

    try:
        while True:
            success, img = cap.read()
            if not success:
                logger.error("Error: Unable to read camera frame.")
                break

            # Draw rectangles for existing parking spots
            for pos in posList:
                cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), (255, 0, 255), 2)

            # Display the video feed with parking spots
            cv2.imshow("Parking Spot Manager", img)

            # Set up mouse click callback
            cv2.setMouseCallback("Parking Spot Manager", mouseClick, {'positions': posList})

            # Press 'q' to quit the application
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Exiting application.")
                break
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera and resources released.")

if __name__ == '__main__':
    main()