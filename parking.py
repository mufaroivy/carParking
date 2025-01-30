import cv2
import pickle

# Parking spot dimensions
width, height = 26, 58

# Load existing parking positions or initialize an empty list if file doesn't exist
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
        print("Loaded parking positions from file.")
except FileNotFoundError:
    posList = []
    print("No existing positions found. Starting fresh.")

def save_positions():
    """
    Save the parking positions to a file.
    """
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)
    print("Parking positions saved.")

def mouseClick(events, x, y, flags, params):
    """
    Handle mouse click events to add or remove parking spots.

    - Left-click to add a new parking spot.
    - Right-click to remove an existing parking spot.
    """
    if events == cv2.EVENT_LBUTTONDOWN:  # Add a parking spot
        posList.append((x, y))
        print(f"Added spot at {x}, {y}")
        save_positions()  # Save changes

    elif events == cv2.EVENT_RBUTTONDOWN:  # Remove a parking spot
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:  # Check if click is within a spot
                posList.pop(i)
                print(f"Removed spot at {x1}, {y1}")
                save_positions()  # Save changes
                break

# Initialize video capture
cap = cv2.VideoCapture(0)  # Use the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

while True:
    success, img = cap.read()
    if not success:
        print("Error: Unable to read camera frame.")
        break

    # Draw rectangles for existing parking spots
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)

    # Display the video feed with parking spots
    cv2.imshow("Image", img)

    # Set up mouse click callback
    cv2.setMouseCallback("Image", mouseClick)

    # Press 'q' to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
