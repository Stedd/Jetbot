import sys, termios, tty, os, time
from adafruit_servokit import ServoKit
import time

speed = 20
low_angle = 40
high_angle = 180
kit = ServoKit(channels=16)

kit.servo[2].angle = low_angle

def berry():
    print("picking Strawberry")
    #drive up
    for i in range(low_angle, high_angle,1):
        kit.servo[2].angle=i
        print('arm angle' + str(i))
        time.sleep(1/speed)
    
    #shaking if needed

    #drive down
    for i in range(high_angle, low_angle,1):
        kit.servo[2].angle=i
        print('arm angle' + str(i))
        time.sleep(1/speed)
    kit.servo[2].angle = low_angle



def dummy():
    print("picking Strawberry")
    time.sleep(3)