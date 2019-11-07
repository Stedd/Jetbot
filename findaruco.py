import cv2
import cv2.aruco as aruco 
import numpy as np
import camera as cam
import vel_control as vel_control
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

def vel_to_marker(cap,id,desired_distance,x_old):

    #Settings
    on_top = 10

    x,y,distance,x_aruco = getarucoPosition(cap,id)
    x = int(x)
    y = int(y)
    if x > 720:
        x = 720
    if y > 540:
        y = 540    
    if distance > desired_distance: #normal usage
            speedl,speedr = vel_control.followball(x,y,x_old)
    elif distance == 0 and x_old != int(720/2): #nothing found
        speedl,speedr = vel_control.followball(x,y,x_old)
        speedl = speedl/2
        speedr = speedr/2
    else:   #too close
        speedl = -20
        speedr = -20
    #small enhancement to get to the middle line faster
    if x_aruco > 0.05:
        speedr = speedr - on_top
        speedl = speedl + on_top
    elif x_aruco < -0.05:
        speedr = speedr + on_top
        speedl = speedl - on_top
    #reducing velocity at the last centimeters
    pass
    return speedl,speedr,distance,x



