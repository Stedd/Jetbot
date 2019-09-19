import cv2
import numpy as np
from matplotlib import pyplot as plt

X_max = 720 #imagesize
Y_max = 540
tolerance = 20
Y_cut = 300 # pixel where the upper part of the image gets used
Y_cut2 = 200 # part of the image for edge detection

def find(img):
    # read in image
    img_BGR = img

    #convert to gray
    im_gray = cv2.cvtColor(img_BGR,cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (3, 15), cv2.BORDER_DEFAULT)  #Blur more in X direction than in y
    im_gray_crop = im_gray[Y_cut:,:] #crop the lower part of the picture

    (thresh, im_bin) = cv2.threshold(im_gray_crop, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    #open the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
    im_bin= cv2.morphologyEx(im_bin, cv2.MORPH_OPEN, kernel)
    #close the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    im_bin = cv2.morphologyEx(im_bin,cv2.MORPH_CLOSE,kernel)

    # Setup SimpleBlobDetector parameters
    params = cv2.SimpleBlobDetector_Params()
    params.minDistBetweenBlobs = 100
    params.filterByColor = False
    #params.blobColor = 255
    params.filterByArea = True
    params.minArea = 80*100
    params.maxArea = 600*100 #can't be decreased ?
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
    params.maxInertiaRatio = 1
    detector = cv2.SimpleBlobDetector_create(params)

    #Creat Blob (red Circle)
    keypoints = detector.detect(cv2.bitwise_not(im_bin))
    if keypoints: #if keypoints is not empty
        X = int(keypoints[0].pt[0])
        Y = int(keypoints[0].pt[1]+Y_cut)
        S = keypoints[0].size
        a = keypoints[0].angle # -1 if not applicable 
        #print(X,Y,S,a)
    else:
        X = int(X_max/2)
        Y = Y_max-100



    ##Part 2 edge detection 
    #this part is actually not needed even though I like the visual outcomes
    # but as I said: nothing of it gets used
    '''
    im_gray_crop2 = im_gray[Y_cut2:,:]
    edges = cv2.Canny(im_gray_crop2, 200, 5, 3)

    #cheating as I dont understand canny
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,10))
    edges = cv2.morphologyEx(edges,cv2.MORPH_DILATE,kernel)

    #close the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,20))
    edges = cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel)

    lines = cv2.HoughLinesP(edges,1, 3.141/180, 150, 600, 10)

    sum_x = 0
    sum_y = 0
    if lines is not None:
        N = lines.shape[0]
        for i in range(N):
            x1 = lines[i][0][0]
            y1 = lines[i][0][1] + Y_cut2   
            x2 = lines[i][0][2]
            y2 = lines[i][0][3] + Y_cut2
            sum_x += (x1+x2)/2
            sum_y += (y1+y2)/2
            cv2.line(img_BGR,(x1,y1),(x2,y2),(0,0,255),1)
    else:
        N=1

    X2 = int(sum_x/N)
    Y2 = int(sum_y/N)

    #x = int((X+X2)/2)
    #y = int((Y+Y2)/2)
    '''
    x = X
    y = Y


    '''#Visualisation
    img_RGB = cv2.cvtColor(img_BGR,cv2.COLOR_BGR2RGB)
    cv2.circle(img_RGB, (X, Y), 5, (255, 0, 0), -1)
    cv2.putText(img_RGB, "target1", (X-25, Y-25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.circle(img_RGB, (X2, Y2), 5, (255, 0, 0), -1)
    cv2.putText(img_RGB, "target2", (X2-25, Y2-25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.circle(img_RGB, (x, y), 5, (255, 0, 0), -1)
    cv2.putText(img_RGB, "final target", (X2+25, Y2+25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.imshow('Calibrated camera',img_RGB) 
    '''
    return x,y