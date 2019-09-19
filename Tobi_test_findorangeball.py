import cv2
import numpy as np

def find(img):
    img_BGR = img
    #convert to hsv
    img_HSV = cv2.cvtColor(img_BGR,cv2.COLOR_BGR2HSV)

    #filter out color : ornage ball is
    #(11,113,227), (10,75,213) (16,181,253)(15,196,229)
    lower_orange = np.array([10,120,150])  #(10,80,150)image1_4
    upper_orange = np.array([18,255,255])  #(20,255,255)image1_2
    mask_orange = cv2.inRange(img_HSV, lower_orange, upper_orange)

    #open the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    mask= cv2.morphologyEx(mask_orange, cv2.MORPH_OPEN, kernel)
    #close the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(6,6))
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)

    # calculate x,ycoordinate of center
    M =cv2.moments(mask)
    if M["m00"]!= 0:
        X=int(M["m10"] /M["m00"])
        Y=int(M["m01"] /M["m00"])
    else:
        M =cv2.moments(mask_orange)
        if M["m00"]!= 0:
            X=int(M["m10"] /M["m00"])
            Y=int(M["m01"] /M["m00"])
        else:
            X = int(720/2)
            Y = int(540-100)

    return X,Y

