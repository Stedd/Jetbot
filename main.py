#!/usr/bin/python3
print("----initializing----")
#import cv2
import time
import camera as cam
import motor as motor
import findberry as find
import pickberry_old as pick
import vel_control as vel_control
import findaruco as ID

#Settings
turningtime_left = 0.37*2
turningtime_right = turningtime_left+0.05
Size_threshhold = 30
turning_distance = 0.05 #meter
driveback_time = 0.35 #seconds

a_moment = 0.05

def end(cap):    
    motor.drive(0)
    pick.armdown()
    cam.closecam(cap)
    cv2.destroyAllWindows()  # Close all windows

def right():
    #motor.drive_l(30)
    #motor.drive_r(-100)
    motor.drive_l(15)
    motor.drive_r(-50)
    time.sleep(turningtime_right)
    motor.drive(0)

def left():
    #motor.drive_l(-30)
    #motor.drive_r(100)
    motor.drive_l(-15)
    motor.drive_r(50)
    time.sleep(turningtime_left)
    motor.drive(0)

def left_to_bush():
    #motor.drive_l(-30)
    #motor.drive_r(100)
    motor.drive_l(-15)
    motor.drive_r(50)
    time.sleep(turningtime_left-0.1)
    motor.drive(0)


def halfright():
    motor.drive_l(15)
    motor.drive_r(-50)
    time.sleep(turningtime_right/2)
    motor.drive(0)

def safe_right(cap):
    right()
    time.sleep(a_moment)
    img = cam.get_calibrated_img(cap)
    x,y,distance1,x_aruco = ID.getarucoPosition(img,1)
    if distance1 == 0:
        time.sleep(a_moment)
        img = cam.get_calibrated_img(cap)
        x,y,distance3,x_aruco = ID.getarucoPosition(img,3)
        if distance3 == 0:
            halfright()
            time.sleep(a_moment)
            img = cam.get_calibrated_img(cap)
            x,y,distance1,x_aruco = ID.getarucoPosition(img,1)
            if distance1 == 0:
                time.sleep(a_moment)
                img = cam.get_calibrated_img(cap)
                x,y,distance3,x_aruco = ID.getarucoPosition(img,3)
                if distance3 == 0:
                    left()
                    img = cam.get_calibrated_img(cap)
                    x,y,distance1,x_aruco = ID.getarucoPosition(img,1)
                    if distance1 == 0:
                        time.sleep(a_moment)
                        img = cam.get_calibrated_img(cap)
                        x,y,distance3,x_aruco = ID.getarucoPosition(img,3)
                        if distance3 == 0:
                            halfright()

def driveback(cap):
    motor.drive_l(-100)
    motor.drive_r(-100)
    time.sleep(driveback_time)
    safe_right(cap)
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
        window_handle = cv2.namedWindow('Calibrated camera', cv2.WINDOW_AUTOSIZE)

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
            x = int(720/2)
            y = int(540-100)

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
            y_old = int(540-100)
            x_old = int(720/2)
            reachedberry = False
            #doublecheck
            time.sleep(0.25) #waitng before capturing the next image as this shows if the berry is still there or not
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
    left_to_bush()
    time.sleep(0.25) #waiting before capturing the next image as this shows if red berry is there or not
    x,area,y = find.firstImage(cam.get_calibrated_img(cap))
    if area/10000 > Size_threshhold: # red berry on this bush
        print("RED Berry found!")
        if findandpickberry(cap) == True: #pick it
            driveback(cap)
            return True
    else: # green berry on this bush
        print('\033[92m' + "green berry" + '\033[0m')
        safe_right(cap)
        return False

def vel_to_marker(cap,id,desired_distance,x_old):
    #Settings
    on_top = 15 #10
    distancetoline_Limit = 0.06 # in m #0.06
    img = cam.get_calibrated_img(cap)
    x,y,distance,x_aruco,x1,x2 = ID.getarucoPosition(img,id)
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
    if x_aruco > distancetoline_Limit and x2 < 720-20 and abs(distance - desired_distance) > 0.02:
        speedr = speedr - on_top
        speedl = speedl + on_top
        if x_aruco > distancetoline_Limit*2:
            speedr = speedr - on_top/2
            speedl = speedl + on_top/2
    elif x_aruco < -distancetoline_Limit and x1 > 20:
        speedr = speedr + on_top
        speedl = speedl - on_top
        if x_aruco < -distancetoline_Limit*2:
            speedr = speedr + on_top/2
            speedl = speedl - on_top/2
    #reducing velocity at the last centimeters
    #4 cm
    if abs(distance-desired_distance) < 0.04 :
        speedl = speedl * 0.5
        speedr = speedr * 0.5
        #2cm
        if abs(distance-desired_distance) < 0.02 :
            speedl = speedl * 0.2
            speedr = speedr * 0.2
    #reduccing velocity at high distance and high turn rate to not loose the marker in the image
    if distance > 1 and abs(speedl-speedr) > 20:
        speedl = speedl * 0.5
        speedr = speedr * 0.5
    print("")
    print("x-value: "+str(x_aruco))
    return speedl,speedr,distance,x

def drivetomarker(cap,id,desired_distance):
    #Settings
    drivingspeed = 100
    tolerance = 1/100 #+- in m


    x_old = int(720/2)
    distance = 0
    newlylost = True
    distancereached = False
    distancecorrect = False
    while not distancereached:
        speedl,speedr,distance,x = vel_to_marker(cap,id,desired_distance,x_old)
        print("distance to arucomarker:" + str(distance))
      
        if x == int(720/2): #nothing found
            if newlylost == True:
                timelost = 0
                tic = time.time()
                newlylost = False
            if timelost < 5000:
                toc = time.time()
                timelost = (toc - tic)*1000 #ms
                #print("lost since " + str(timelost) + " ms")
                if x_old > 720/2+100: #lost it to the right
                    if timelost <= 1000:
                        speedl = 25 #turn right
                        speedr = 0 
                        #print("search sequence 1")
                    elif timelost < 3000: # turn the other way
                        #print("search sequence 2")
                        speedl = 0
                        speedr = 25 
                    else:
                        #print("search sequence3")
                        speedl = 10 
                        speedr = 0
                elif x_old < 720/2-100: #lost it to the left
                    if timelost <= 1000:
                        speedl = 0 #turn left
                        speedr = 25 
                    elif timelost < 3000: # turn the other way
                        speedl = 25
                        speedr = 0 
                    else:
                        speedl = 10 
                        speedr = 0
                elif x_old == int(720/2): #beginning
                    pass
                else:#lost in the middle
                    speedl = -5
                    speedr = -5
        else:
            newlylost = True
            x_old = x
        speedl = speedl*(drivingspeed/100)
        speedr = speedr*(drivingspeed/100)
        motor.drive_l(speedl)
        motor.drive_r(speedr)
        if distance > desired_distance - tolerance and distance < desired_distance + tolerance and distancecorrect ==True:
            distancereached = True
        elif distance > desired_distance - tolerance and distance < desired_distance + tolerance:
            distancecorrect = True
        else:
            distancecorrect = False
    return True

def pick_all_in_line(cap,ID,point):

    ## Settings
    distance_to_next_bush = 0.17

    picked_berrys = 0
    for x in range(5):
        if drivetomarker(cap,ID,point) == True:
            motor.drive(0)
            #time.sleep(1.5)
            if checkthisbush(cap) == True:
                picked_berrys = picked_berrys +1
        point = point-distance_to_next_bush
    return picked_berrys

def testleftright():
    while True:
        left()
        motor.drive(0)
        time.sleep(0.5)
        right()
        motor.drive(0)
        time.sleep(1)

def camtest():
    while True:
        tic = time.time()
        img = cam.get_calibrated_img(cap)
        print("time of that frame in ms: " +str((time.time()-tic)*1000))
#################################################################################################
########################### BEGIN OF PROGRAM ######################################################
#################################################################################################
print("----- Program start -----")

#testrightleft()


collectedberrys = 0
motor.drive(0)
pick.armdown()
print("opening camera stream")
cap = cam.opencam()
if cap.isOpened():
    try:
        ## MAIN Program is here ##
        start_point = ((5*17+14+10)/100) + turning_distance #setpoint
        collectedberrys = collectedberrys + pick_all_in_line(cap,1,start_point)
        if drivetomarker(cap,1,0.27+turning_distance) == True:
            left()
        if drivetomarker(cap,2,0.27+turning_distance) == True:
            left()
        start_point = ((5*17)/100) + turning_distance #setpoint
        collectedberrys = collectedberrys + pick_all_in_line(cap,3,start_point)
        motor.drive(150)
        time.sleep(0.5)
        motor.drive(0)
    except KeyboardInterrupt:
        end(cap)
end(cap)
print("----- END OF PROGRAM -----")
print(str(collectedberrys) + " Berrys picked")
print("---------------------------")
