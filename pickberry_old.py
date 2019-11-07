print("init arm servo control")
import sys, termios, tty, os, time
import Adafruit_PCA9685
import time



i2cbus = 1
frequency = 50 # The contiuous servo motors require 50 Hz
servoDriver = Adafruit_PCA9685.PCA9685(busnum=i2cbus)
servoDriver.set_pwm_freq(frequency) # The spec sheet for the motors says 50 Hz
for i in range(0, 1):
    servoDriver.set_pwm(i, 0, 0)

# Set channels for the two motors
servo = 2
# channelLeft = 1

# To control the servo signal, use adafruit.pwm.set_pwm(channel, HIGH, LOW)
# channel: Which channel to operate
# HIGH: integer within [0, 4095] stating when in the 20 ms cycle to go HIGH
#   For servo signal, should always be 0
# LOW: Interfer within [0, 4095] stating when in the 20 ms cycle the signal
# should revert to LOW from being HIGH
#   For servo signal, should be between 204 and 408 (between 1ms and 2ms)



servo_min = 75
servo_max = 561

def armdown():
    print("Arm Down")
    servoDriver.set_pwm(servo, 0, servo_min)

def berry(speed):
    print("picking Strawberry")
    #drive up
    for x in range(servo_min, servo_max+1):
        servoDriver.set_pwm(servo, 0, x)
        #print("arm setpoint: "+str(x))
        time.sleep(1/speed)

    #drive down
    for x in range(servo_min, servo_max+1):
        servoDriver.set_pwm(servo, 0, servo_max+servo_min-x)
        #print("arm setpoint: "+str(x))
        time.sleep(1/speed)
    servoDriver.set_pwm(servo, 0, servo_min)

def dummy():
    print("picking Strawberry")
    time.sleep(1)