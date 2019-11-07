print("init Aruco-management")
import cv2
import cv2.aruco as aruco 
import numpy as np
import camera as cam



devmode = 0

# Set up aruco dictionary for 4X4 arucos
arucoDict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters_create()
markerLength = 0.11 # size of marker in meters, side length

# Load calibration values fpr bending
data = np.load('/home/jetbot/state_of_art_Software/calibration_files/calib_params_from_matlab.npz')
mtx = data["mtx"]
dist = data["dist"]

def getarucoPosition(cap,aruco_id):
    distance = 0
    x = int(720/2)
    y = int(540-100)
    x_aruco = 0
    img = cam.get_calibrated_img(cap)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
    # Identify arucos
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, arucoDict, parameters=parameters)
    if devmode ==1:
        aruco.drawDetectedMarkers(img, corners, ids)
    # Estimate the position of aruco markers
    rvecs, tvecs, obj_points = aruco.estimatePoseSingleMarkers(corners, markerLength, mtx, dist)
    try:
        for i in range(0,len(rvecs)):
            if ids[i] == aruco_id:
                #calculate distance in meters
                distance = np.linalg.norm(tvecs[i])
                #calculate the Pixe of the middle of the bottom line of the marker
                y = (corners[i][0][3-1][2-1]+corners[i][0][4-1][2-1])/2
                x = ((corners[i][0][3-1][1-1]-corners[i][0][4-1][1-1])/2)+corners[i][0][3-1][1-1]
                x_aruco = tvecs[i][0][0] 
    except:
        print('No arucos found')

    if devmode ==1:
    # Draw axes on arucos and calculate the distance between the camera and code
        try:
            for i in range(0, len(rvecs)):
                    aruco.drawAxis(img, mtx, dist, rvecs[i], tvecs[i], markerLength)
                    print('Distance to marker ID {} is Norm: {}'.format(ids[i], np.linalg.norm(tvecs[i])))
        except:
            print('No arucos found')
        # Show arucos on image
        cv2.imshow('aruco Test', img)
    return x,y,distance,x_aruco

