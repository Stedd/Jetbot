# Imports
import cv2
import numpy as np

print("init camera control")
#Size of image
im_height = 540
im_width = 720


# Load color calibration
gainmatrix = np.load('/home/jetbot/state_of_art_Software/calibration_files/colorcalib.npy')
results = np.zeros((im_height, im_width, 3), float)

# Load calibration values fpr bending
data = np.load('/home/jetbot/state_of_art_Software/calibration_files/calib_params_from_matlab.npz')
mtx = data["mtx"]
dist = data["dist"]
rvecs = data["rvecs"]
tvecs = data["tvecs"]



def gstreamer_pipeline(
    capture_width=im_width,
    capture_height=im_height,
    display_width=im_width,
    display_height=im_height,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def opencam(freq):
    # Using default values in gstreamer_pipeline to capture video
    cap = cv2.VideoCapture(gstreamer_pipeline(framerate=freq), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        return cap
    else:
        print("Unable to open camera")
        #return False

def closecam(cap):  
    cap.release()  # Release the camera input

def calibrateColor(img, gainmatrix):
    results[:] = img*gainmatrix
    I = results < 0
    results[I] = 0
    I = results > 255
    results[I] = 255
    img[:] = results

def get_calibrated_img(cam):
    if cam.isOpened():  
            ret_val, img = cam.read()
            #calibrate color
            calibrateColor(img, gainmatrix)
            
            # Calibrate distortion
            img = cv2.undistort(img, mtx, dist, None, mtx)

            return img
    else:
        print("open camera first")