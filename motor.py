# File for handling motor control

import Adafruit_PCA9685
import sys, termios, tty, os

# Class for the motor driver card
class MotorDriver():
    def __init__(self, i2cbus, frequency=50):
        '''
        Initializes a motor on the motor driver

        Parameters
        ----------
        i2cbus : int
            Which bus to connect. Motor driver is connected on I2C bus 1 on Jetson Nano
        frequency : int
            PWM frequency for the motor. 
            The continuous motors require 50 Hz'''
        self.i2cbus = i2cbus
        self.frequency = frequency # The contiuous servo motors require 50 Hz
        self.pwm = Adafruit_PCA9685.PCA9685(busnum=self.i2cbus) # I2C bus 1 is used for the Motor driver
        self.pwm.set_pwm_freq(self.frequency) # The spec sheet for the motors says 50 Hz
        for i in range(0, 15):
            self.pwm.set_pwm(i, 0, 0)

# Class for each motor
class Motor():
    def __init__(self, motorDriver, channel):
        '''
        Initializes a motor

        Parameters
        ----------
        motorDriver : object
            MotorDriver object
        channel : int
            Which channel the motor is connected to
            Between 0 and 15
        '''
        self.motorDriver = motorDriver
        self.channel = channel
    def actuate(self, state):
        if 0 <= state <= 4095:
            self.motorDriver.pwm.set_pwm(self.channel, 0, state)
        else:
            self.stop() 
    def stop(self):
        self.motorDriver.pwm.set_pwm(self.channel, 0, 321)

# Initialize motor driver
motorDriver = MotorDriver(1, 50)

# Initialize motors
rightmotor = Motor(motorDriver, 0)
leftmotor = Motor(motorDriver, 1)

# Set zero actuation point
# Theoreically, the servo can be controlled between 204 and 408, and the theoretical center is 306
rightactuation_zero = 321
right_fwd_start = 311
right_bwd_start = 326
right_fwd_max = 272
right_bwd_max = 363
rightactuation_pos_range = right_bwd_max - right_bwd_start
rightactuation_neg_range = right_fwd_start - right_fwd_max

leftactuation_zero = 321
left_fwd_start = 326
left_bwd_start = 311
left_fwd_max = 363
left_bwd_max = 275
leftactuation_pos_range = left_fwd_max - left_fwd_start
leftactuation_neg_range = left_bwd_start - left_bwd_max

def drive(speed):
    if speed > 100:
        speed = 100
    elif speed < -100:
        speed = -100

    if speed > 0:
        # drive fwd
        rightactuation = right_fwd_start - speed / 100 * rightactuation_neg_range
        leftactuation = left_fwd_start + speed / 100 * leftactuation_pos_range
    elif speed < 0:
        # drive bwd
        rightactuation = right_bwd_start - (speed / 100) * rightactuation_pos_range
        leftactuation = left_bwd_start + (speed / 100) * leftactuation_neg_range
    elif speed == 0:
        # stand still
        rightactuation = rightactuation_zero
        leftactuation = leftactuation_zero
    
    print(rightactuation)
    rightactuation = int(rightactuation)
    leftactuation = int(leftactuation)
    leftmotor.actuate(leftactuation)
    rightmotor.actuate(rightactuation)

def drive_l(speed):
    if speed > 0:
        # drive fwd
        leftactuation = left_fwd_start + speed / 100 * leftactuation_pos_range
    elif speed < 0:
        # drive bwd
        leftactuation = left_bwd_start + (speed / 100) * leftactuation_neg_range
    elif speed == 0:
        # stand still
        leftactuation = leftactuation_zero
    leftmotor.actuate(int(leftactuation))
    print('l %i'%leftactuation)

def drive_r(speed):
    if speed > 0:
        # drive fwd
        rightactuation = right_fwd_start - speed / 100 * rightactuation_neg_range
    elif speed < 0:
        # drive bwd
        rightactuation = right_bwd_start - (speed / 100) * rightactuation_pos_range
    elif speed == 0:
        # stand still
        rightactuation = rightactuation_zero
    rightmotor.actuate(int(rightactuation))
    print('r %i'%rightactuation)