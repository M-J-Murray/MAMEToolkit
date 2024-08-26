import cv2
import numpy as np

def get_pacman_coordinates(frame):
    # Get pacman's bounding box
    hsv_image = cv2.cvtColor(frame[:, :-15, :], cv2.COLOR_BGR2HSV) # Removes the bottom 15 pixels to remove "footer"
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    else:
        return None
    
def get_pacman_rect(frame, expand_by_pixels=7):
    # Returns the portion of the frame containing pacman plus the surrounding walls without
    # overflowing the frame.
    x, y, w, h = get_pacman_coordinates(frame)
    height, width, _ = frame.shape
    x_new = max(x - expand_by_pixels, 0)
    y_new = max(y - expand_by_pixels, 0)
    w_new = min(w + expand_by_pixels*2, width - x_new)
    h_new = min(h + expand_by_pixels*2, height - y_new)
    pacman_rect = frame[y_new:y_new+h_new, x_new:x_new+w_new]
    return pacman_rect

def detect_walls(frame):
    walls = {
        "right": False,
        "left": False,
        "top": False,
        "bottom": False
    }
    try:
        rect_area = get_pacman_rect(frame)
        hsv_image = cv2.cvtColor(rect_area, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, threshold=10, minLineLength=10, maxLineGap=10)
        if lines is not None:
            img = np.array(rect_area) # Make a new writable array.
            h, w, _ = img.shape
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Detect vertical walls
                if abs(x2 - x1) == 0:
                    if x1 > w/2:
                        walls["right"] = True
                    else:
                        walls["left"] = True
                # Detect horizontal walls
                if abs(y2 - y1) == 0:
                    if y2 > h/2:
                        walls["top"] = True
                    else:
                        walls["bottom"] = True
            return walls
    except TypeError:
        # Pacman wasn't found in the frame
        pass


def get_valid_moves(frame):
    walls = detect_walls(frame)
    valid_moves = [4]
    if walls:
        if not walls["top"]:
            valid_moves.append(0)
        if not walls["bottom"]:
            valid_moves.append(1)
        if not walls["right"]:
            valid_moves.append(2)
        if not walls["left"]:
            valid_moves.append(3)
    return tuple(valid_moves)
