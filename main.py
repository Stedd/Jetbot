#!/usr/bin/python3
import cv2
import time
import camera as cam
import motor as motor
import findberry as find
import pickberry_old as pick
import vel_control as vel_control
import findaruco as ID

#Settings
turningtime = 0.3
Size_threshhold = 100

#developersettings
framerate = 5 #hz


def end(cap):    
    motor.drive(0)
    pick.armdown()
    cam.closecam(cap)
    cv2.destroyAllWindows()  # Close all windows

def right():
    motor.drive_l(-50)
    motor.drive_r(-100)
    time.sleep(turningtime)

def left():
    motor.drive_l(-100)
    motor.drive_r(-50)
    time.sleep(turningtime)

def driveback():
    motor.drive_l(-100)
    motor.drive_r(-100)
    time.sleep(0.2)
    right()
    motor.drive(0)


def findandpickberry(cap,framerate):
    #Settings
    drivingspeed = 60 #60 or 85 # in %        
    pickingspeed = 20000 # speed of the arm 
    agg = 4 #4 #aggressitivity for picking # the safer the lower
    supersavedrivingspeed = 5 # in %
    supersave_agg = 0
    #testedsetting: 
    # 80,200,5 works
    # 90.2500,3 works
    # 100,3000, 15 works but with overshoots
    # 90,3500,15 works better than 100
    
    #developersettings
    devmode = 1 #1 for output of stream and more information

    if devmode == 1:
        drivingspeed = drivingspeed/4

    y_old = int(540-100)
    x_old = int(720/2) 
    reachedberry = False
    secondtry =False
    tic = time.time()
    while True:
        berry_far_away = False
        img = cam.get_calibrated_img(cap)

        if x_old == int(720/2) and y_old == int(540-100):
            x_old,area,y_old = find.firstImage(img)
        
        x,area,y = find.berry(img,x_old,y_old)
        #x,area,y = find.berryAI(img)
        #x,area,y = find.berry_old(img)

        if area > 0:
            berry_far_away = True

        area = int(area/10000)

        if area == 0 and berry_far_away == True:
            area = 1
        berry_far_away = False
        
        if area > 600:
            area = 600
        if area == 0:   #nothing found
            speedl = 0  #don't move
            speedr = 0
        else:
            speedl, speedr = vel_control.followstrawberry(x,area,x_old)

        if devmode == 1:
            #output image
            cv2.circle(img, (x, y), 5, (255, 255, 255), -1)
            cv2.putText(img, "centroid", (x-25, y-25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.imshow('Calibrated camera',img)

        print("area: ",area, " x: ",x, " Y: ", y, "  | {:1.0f} %% vel left | {:2.0f} %% vel right " .format(speedl, speedr))

        if secondtry == False:
            speedl = speedl*(drivingspeed/100)
            speedr = speedr*(drivingspeed/100)
        else:
            speedl = speedl*(supersavedrivingspeed/100)
            speedr = speedr*(supersavedrivingspeed/100)

        x_old = x
        y_old = y

        motor.drive_l(speedl)
        motor.drive_r(speedr)
        
        if  (abs(speedl) <= agg and abs(speedr) <= agg and reachedberry == True and area != 0 and secondtry == False) or (abs(speedl) == supersave_agg and abs(speedr) == supersave_agg and reachedberry == True and area != 0):
            #pick.dummy()
            motor.drive(0)
            pick.berry(pickingspeed)    #safe mode
            time.sleep(0.2) #waitng before capturing the next image as this shows if the berry is still there or not
            y_old = int(540-100)
            x_old = int(720/2)
            reachedberry = False
            #doublecheck
            x_old,area,y_old = find.firstImage(cam.get_calibrated_img(cap))
            if area/10000 > 200: #Berrypicking failed
                secondtry = True   
                # till next picking: 
                # agg = supersave_agg
                # speed = supersavespeed
                print("FAILED picking, trying again")
            else:
                secondtry = False
                return True
            #end(cap)
        elif (abs(speedl) <= agg and abs(speedr) <= agg and area != 0 and secondtry == False) or (abs(speedl) == supersave_agg and abs(speedr) == supersave_agg and area != 0):
            #berry.pick()   #fast mode
            reachedberry = True
        else:
            reachedberry = False
        # Get keyboard commands from the window
        keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key OR close the CSI camera window
        if keyCode == 27:
            print("Escape key is pressed")
            end(cap)
            break  # Breaks out of the while loop
                #forcing to framerate
        toc= time.time()
        while((toc - tic)<(1/(framerate+1))):
            time.sleep(0.01)
            print("framerate can be higher")
            toc = time.time()
        if devmode==1:
            print((toc - tic)*1000, ' ms')
        tic = time.time()

def drivetomarker(cap,id,desired_distance):
    #Settings
    drivingspeed = 80 

    x_old = int(720/2)
    speedl,speedr,distance,x = ID.vel_to_marker(cap,id,desired_distance,x_old)
    while distance > desired_distance + 0.01 or distance < desired_distance - 0.01:
        speedl = speedl*(drivingspeed/100)
        speedr = speedr*(drivingspeed/100)
        motor.drive_l(speedl)
        motor.drive_r(speedr)
        speedl,speedr,distance,x = ID.vel_to_marker(cap,id,desired_distance,x_old)
        print(distance)
        if x == int(720/2): #nothing found
            pass
        else:
            x_old = x
    return True

##Testfunctions
def testarucopositioning(cap):
    i = 1.49 #setpoint
    while i > 0.26:
        if drivetomarker(cap,1,i) == True:
            #left()
            print("Done")
            motor.drive(0)
            time.sleep(1)
            i = i-0.27


#################################################################################################
########################### BEGIN OF PROGRAM ######################################################
#################################################################################################





collectedberrys = 0
motor.drive(0)
pick.armdown()

cap = cam.opencam(framerate)
if cap.isOpened():
    try:
        while True:
            findandpickberry(cap,framerate)
            time.sleep(3)
        ## MAIN Program is here ##
        #while collectedberrys<8:
            #if findandpickberry(cap,framerate) == True:
            #    collectedberrys = collectedberrys+1    
            #driveback()

            #x,area,y = find.firstImage(cam.get_calibrated_img(cap))
            #    if area/10000 > Size_threshhold: # red berry on this bush
            #        if findandpickberry(cap,framerate) == True:
            #            collectedberrys = collectedberrys+1  
            #    else: # green berry on this bush
            #            right()

    except KeyboardInterrupt:
        end(cap)
        pass
end(cap)