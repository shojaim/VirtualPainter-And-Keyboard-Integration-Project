import cvzone
import cv2
import numpy as np
from time import sleep
import os
import HandTrackingModule as htm
from cvzone.HandTrackingModule import HandDetector as cvzoneHandDetector
from pynput.keyboard import Controller


PAINTER_MODE = 0
KEYBOARD_MODE = 1
current_mode = PAINTER_MODE  # Initial mode: Painter


# Your Virtual Painter code
def run_painter():
    global current_mode
    # Virtual Painter code here
    #######################
    brushThickness = 25
    eraserThickness = 100
    ########################

    folderPath = "Header"
    myList = os.listdir(folderPath)
    print(myList)
    overlayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
    print(len(overlayList))

    header = overlayList[0]
    drawColor = (153, 51, 255)

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = htm.handDetector(detectionCon=int(0.90))
    xp, yp = 0, 0
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    while True:
        # 1. Import image
        success, img = cap.read()
        img = cv2.flip(img, 1)

        # 2. Find Hand Landmarks
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            # print(lmList)

            # tip of index and middle fingers
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]

            # 3. Check which fingers are up
            fingers = detector.fingersUp()

            # 4. If Selection mode - Two fingers are up
            if fingers[1] and fingers[2]:
                xp, yp = 0, 0
                print("Selection Mode")
                #  Checking for the click
                if y1 < 125:
                    if 250 < x1 < 450:
                        header = overlayList[0]
                        drawColor = (153, 51, 255)
                    elif 550 < x1 < 750:
                        header = overlayList[1]
                        drawColor = (255, 153, 51)
                    elif 800 < x1 < 950:
                        header = overlayList[2]
                        drawColor = (102, 204, 0)
                    elif 1050 < x1 < 1200:
                        header = overlayList[3]
                        drawColor = (0, 0, 0)
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

                cv2.rectangle(img, (1000, 500), (1200, 600), (51, 153, 255), cv2.FILLED)
                cv2.putText(img, 'Keyboard', (1026, 559), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Check if two fingers are inside the keyboard rectangle
                if 1000 < x1 < 1200 and 500 < y1 < 600:
                    switch_mode()  # Switch to the Keyboard mode

            # 5. If Drawing Mode - Index finger is up
            if fingers[1] and fingers[2] == False:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                print("Drawing Mode")
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)

                if drawColor == (0, 0, 0):
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)

                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

                xp, yp = x1, y1

            # Clear Canvas when all fingers are up
            #if all(x >= 1 for x in fingers):
                #imgCanvas = np.zeros((720, 1280, 3), np.uint8)

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        # Setting the header image
        img[0:125, 0:1280] = header
        # img = cv2.addWeighted(img,0.5,imgCanvas,0.5,0)
        cv2.imshow('Image', img)
        # cv2.imshow('Canvas', imgCanvas)
        cv2.imshow("Inv", imgInv)

        cv2.waitKey(1)


#  Virtual Keyboard code
def run_keyboard():
    # Virtual Keyboard code here
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = cvzoneHandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.8, minTrackCon=0.5)  # cvzone hand tracking module instance

    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

    finalText = ""
    keyboard = Controller()

    def drawAll(img, buttonList):

        imgNew = np.zeros_like(img, np.uint8)
        for button in buttonList:
            x, y = button.pos
            cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                              20, rt=0)
            cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]),
                          (255, 0, 255), cv2.FILLED)
            cv2.putText(imgNew, button.text, (x + 40, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        print(mask.shape)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out

    class Button():
        def __init__(self, pos, text, size=[85, 85]):
            self.pos = pos
            self.size = size
            self.text = text

    buttonList = []

    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        img = drawAll(img, buttonList)

        # Define the painter rectangle at the bottom right
        cv2.rectangle(img, (1000, 500), (1200, 600), (76, 0, 153), cv2.FILLED)
        cv2.putText(img, 'Painter', (1045, 558), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if hands:
            # Hand 1
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            bbox1 = hand1["bbox"]
            centerPoint1 = hand1["center"]
            handType1 = hand1["type"]

            if lmList1:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    if x < lmList1[8][0] < x + w and y < lmList1[8][1] < y + h:
                        cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img,
                                                                  color=(255, 0, 255),
                                                                  scale=10)
                        ## when clicked
                        if length < 12:
                            keyboard.press(button.text)
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            finalText += button.text
                            sleep(0.15)

            if 1000 < centerPoint1[0] < 1200 and 500 < centerPoint1[1] < 600:
                switch_mode()  # Switch to the Painter mode

        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 430),
                    cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


# Function to switch between modes
def switch_mode():
    global current_mode

    if current_mode == PAINTER_MODE:
        current_mode = KEYBOARD_MODE
        run_keyboard()  # Switch to Keyboard mode
    elif current_mode == KEYBOARD_MODE:
        current_mode = PAINTER_MODE
        run_painter()  # Switch to Painter mode


if __name__ == "__main__":
    run_painter()  # Run the painter mode by default

