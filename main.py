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
turningtime = 1
Size_threshhold = 50
turning_distance = 0.05 #m

#developersettings
framerate = 5 #hz


def end(cap):    
    motor.drive(0)
    pick.armdown()
    cam.closecam(cap)
    cv2.destroyAllWindows()  # Close all windows

def right():
    motor.drive_l(30)
    motor.drive_r(-100)
    time.sleep(turningtime)

def left():
    motor.drive_l(-30)
    motor.drive_r(100)
    time.sleep(turningtime)

def driveback():
    motor.drive_l(-100)
    motor.drive_r(-100)
    time.sleep(0.2)
    right()
    motor.drive(0)


def findandpickberry(cap):
    #Settings
    drivingspeed = 60 #60 or 85 # in %        
    pickingspeed = 20000 # speed of the arm 
    agg = 4 #4 #aggressitivity for picking # the safer the lower
    supersavedrivingspeed = 10 # in %
    supersave_agg = 0
    #testedsetting: 
    # 80,200,5 works
    # 90.2500,3 works
    # 100,3000, 15 works but with overshoots
    # 90,3500,15 works better than 100
    
    #developersettings
    devmode = 0 #always 0, 1 for output of stream and more information

    if devmode == 1:
        drivingspeed = drivingspeed/4

    y_old = int(540-100)
    x_old = int(720/2) 
    reachedberry = False
    secondtry =False
    #tic = time.time()
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
        if secondtry == True:
            print("second try:safe mode")
        
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
                print('PICKED berry')
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
        #toc= time.time()
        #while((toc - tic)<(1/(framerate+1))):
        #    time.sleep(0.01)
        #    print("framerate can be higher")
        #    toc = time.time()
        #if devmode==1:
        #    print((toc - tic)*1000, ' ms')
        #tic = time.time()

def checkthisbush(cap):
    left()
    x,area,y = find.firstImage(cam.get_calibrated_img(cap))
    if area/10000 > Size_threshhold: # red berry on this bush
        if findandpickberry(cap) == True: #pick it
            driveback()
            return True
    else: # green berry on this bush
        right()
        return False

def vel_to_marker(cap,id,desired_distance,x_old):
    #Settings
    on_top = 10
    distancetoline_Limit = 0.06 # in m
    x,y,distance,x_aruco = ID.getarucoPosition(cap,id)
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
        speedl = speedl/1.5
        speedr = speedr/1.5
    else:   #too close
        speedl = -30
        speedr = -30
    #small enhancement to get to the middle line faster
    #if speedl < 0 and speedl <0:
    #    on_top = -on_top 
    if x_aruco > distancetoline_Limit and x < 720-120:
        speedr = speedr - on_top
        speedl = speedl + on_top
        if x_aruco > distancetoline_Limit*2:
            speedr = speedr - on_top/2
            speedl = speedl + on_top/2
    elif x_aruco < -distancetoline_Limit and x > 120:
        speedr = speedr + on_top
        speedl = speedl - on_top
        if x_aruco < -distancetoline_Limit*2:
            speedr = speedr + on_top/2
            speedl = speedl - on_top/2
    #reducing velocity at the last centimeters
    pass
    #reduccing velocity at high distance to not loose the marker in the image
    if distance > 1 and abs(speedl-speedr) > 20:
        speedl = speedl * 0.6
        speedr = speedr * 0.6
    return speedl,speedr,distance,x

def drivetomarker(cap,id,desired_distance):
    #Settings
    drivingspeed = 80 

    x_old = int(720/2)
    speedl,speedr,distance,x = vel_to_marker(cap,id,desired_distance,x_old)
    while distance > desired_distance + 0.01 or distance < desired_distance - 0.01:
        speedl = speedl*(drivingspeed/100)
        speedr = speedr*(drivingspeed/100)
        motor.drive_l(speedl)
        motor.drive_r(speedr)
        speedl,speedr,distance,x = vel_to_marker(cap,id,desired_distance,x_old)
        print("distance to arucomarker:" + str(distance))
        if x == int(720/2): #nothing found
            pass
        else:
            x_old = x
    return True

def pick_all_in_line(cap,ID,point):

    ## Settings
    distance_to_next_bush = 0.27


    picked_berrys = 0
    while point > 0.26:
        if drivetomarker(cap,ID,point) == True:
             if checkthisbush(cap) == True:
                picked_berrys = picked_berrys +1
        point = point-distance_to_next_bush
    return picked_berrys

def testrightleft():
    while True:
        right()
        motor.drive(0)
        time.sleep(2)
        left()
        motor.drive(0)
        time.sleep(2)
#################################################################################################
########################### BEGIN OF PROGRAM ######################################################
#################################################################################################
print("Program start")



collectedberrys = 0
motor.drive(0)
pick.armdown()
print("opening camera stream")
cap = cam.opencam(framerate)

if cap.isOpened():
    try:
        testrightleft()
        ## MAIN Program is here ##
        start_point = ((5*27+14+10)/100) - turning_distance#setpoint
        collectedberrys = collectedberrys + pick_all_in_line(cap,1,start_point)
        left()
        if drivetomarker(cap,2,0.27-turning_distance) == True:
            left()
        start_point = ((5*27)/100) - turning_distance#setpoint
        collectedberrys = collectedberrys + pick_all_in_line(cap,3,start_point)
        print(str(collectedberrys) + " Berrys picked")
    except KeyboardInterrupt:
        end(cap)
end(cap)