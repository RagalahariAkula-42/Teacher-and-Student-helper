import os
import numpy as np
import math
import cv2
import mediapipe as mp
import HandTrackingModule as htm

color = "White"
drawColor = (255, 255, 255)

l, c, r, t = 0, 0, 0, 0
brushThickness = 10
eraserThickness = 30
shape = "Draw"

def load_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Load image with alpha channel if present
    if img is None:
        print(f"Error: Unable to load image from path '{image_path}'")
    return img

# Load images and handle potential errors
bin = load_image("./src/virtualpainter/images/Bin.png")
colors = load_image("./src/virtualpainter/images/Colors.png")
shapes = load_image("./src/virtualpainter/images/Shapes.png")

mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

drawColor = (255, 255, 255)
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
(xq, yq) = (0, 0)
(xp, yp) = (0, 0)
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)

    results = selfie_segmentation.process(img)
    condition = results.segmentation_mask > 0.5
    bg_image = np.zeros(img.shape, dtype=np.uint8)
    bg_image[:] = (0, 0, 0)  # Background color
    output_image = np.where(condition[..., None], img, bg_image)

    if len(lmlist[0]) != 0:
        lmlist_new = lmlist[0]
        x1, y1 = lmlist_new[8][1:]
        x2, y2 = lmlist_new[12][1:]
        x0, y0 = lmlist_new[4][1:]
        x4, y4 = lmlist_new[20][1:]

        fingers = detector.fingersUp()

        if fingers[1] and fingers[2]:  # Selection Mode
            (xp, yp) = (0, 0)
            (xq, yq) = (0, 0)
            if y1 < 60:
                if 0 <= x1 < 100:
                    drawColor = (0, 0, 255)
                    color = "Red"
                elif 100 <= x1 < 200:
                    drawColor = (255, 0, 0)
                    color = "Blue"
                elif 200 <= x1 < 300:
                    drawColor = (0, 255, 0)
                    color = "Green"
                elif 300 <= x1 < 400:
                    drawColor = (0, 255, 255)
                    color = "Yellow"
                elif 400 <= x1 < 500:
                    drawColor = (255, 255, 255)
                    color = "White"
                elif 500 <= x1 < 600:
                    shape = "Draw"
                elif 600 <= x1 < 700:
                    shape = "Line"
                    l = 0
                elif 700 <= x1 < 800:
                    shape = "Circle"
                    c = 0
                elif 800 <= x1 < 900:
                    shape = "Rectangle"
                    r = 0
                elif 900 <= x1 < 1000:
                    shape = "Triangle"
                    t = 0
                elif 1000 <= x1 < 1100:
                    shape = "Erase"
                    drawColor = (0, 0, 0)
                elif 1000 <= x1 < 1100:
                    shape = "Erase"
                    drawColor = (0, 0, 0)
                elif 1100 <= x1 < 1200:
                    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
            cv2.rectangle(output_image, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
        

        if fingers[1] and fingers[2] == False and fingers[0] == False:  # Drawing Mode
            cv2.circle(output_image, (x1, y1), 15, drawColor, cv2.FILLED)
            if xp == 0 and yp == 0:
                xp, yp = x1, y1
                
            if drawColor == (0, 0, 0):  # Erasing
                cv2.line(output_image, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)

            elif shape == "Draw":  # Drawing
                cv2.line(output_image, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1
        
        if fingers[0] and fingers[1] and fingers[2] == False:  # Shape Mode
            cv2.rectangle(output_image, (x0, y0), (x1, y1), drawColor, thickness=10)

            if fingers[4]:
                xq, yq = x0, y0
                if shape == "Line":
                    if l == 0:
                        cv2.line(output_image, (xq, yq), (x1, y1), drawColor, brushThickness)
                        cv2.line(imgCanvas, (xq, yq), (x1, y1), drawColor, brushThickness)

                    l = 1
                elif shape == "Circle":
                    if c == 0:
                        radius = int(math.sqrt((x1 - xq)**2 + (y1 - yq)**2))
                        cv2.circle(output_image, (xq, yq), radius, drawColor, brushThickness)
                        cv2.circle(imgCanvas, (xq, yq), radius, drawColor, brushThickness)

                    c = 1
                elif shape == "Rectangle":
                    if r == 0:
                        cv2.rectangle(output_image, (xq, yq), (x1, y1), drawColor, brushThickness)
                        cv2.rectangle(imgCanvas, (xq, yq), (x1, y1), drawColor, brushThickness)

                    r = 1
                elif shape == "Triangle":
                    if t == 0:
                        pts = np.array([[x0, y0], [x1, y1], [x1, y0]], np.int32)
                        cv2.polylines(output_image, [pts], isClosed=True, color=drawColor, thickness=brushThickness)
                        cv2.polylines(imgCanvas, [pts], isClosed=True, color=drawColor, thickness=brushThickness)
                    t = 1

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(output_image, imgInv)
    img = cv2.bitwise_or(output_image, imgCanvas)

    img[0:60, 0:500] = colors
    img[0:60, 500:1100] = shapes
    img[0:60, 1100:1200] = bin
    
    cv2.imshow("Virtual Painter", img)
    #cv2.imshow("Canvas", imgCanvas)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()