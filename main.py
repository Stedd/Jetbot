#!/usr/bin/python3
#imports
import cv2 
import camera as cam
import motor as motor
import Tobi_test_findorangeball as ball
import findline as line
import vel_control as vel_control

x_old = 0

motor.drive(0)
cap = cam.opencam()
if cap.isOpened():
    window_handle1 = cv2.namedWindow("Calibrated camera", cv2.WINDOW_AUTOSIZE)
    try:
        while (
                cv2.getWindowProperty("Calibrated camera", 0) >= 0
        ):  # While window is opened
            ## MAIN Program is here ##
            img = cam.get_calibrated_img(cap)
            #cv2.imshow('Calibrated camera',img)     

            #ball
            #x,y = ball.find(img)
            #speedl, speedr = vel_control.followball(x,y,x_old)

            #line
            x,y = line.find(img)
            speedl, speedr = vel_control.followline(x,y,x_old)
            speedl = speedl*0.8
            speedr = speedr*0.8


            x_old = x
            print("x: ",x, " Y: ", y, "  | {:1.2f} %% vel left | {:2.2f} %% vel right " .format(speedl, speedr))

            motor.drive_l(speedl)
            motor.drive_r(speedr)

            # Get keyboard commands from the window
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key OR close the CSI camera window
            if keyCode == 27:
                motor.drive(0)
                print("Escape key is pressed")
                break  # Breaks out of the while loop
    except KeyboardInterrupt:
        pass
    motor.drive(0)
    cv2.destroyAllWindows()  # Close all windows
    cap.closecam()