# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 01:50:51 2026

@author: Emerson
"""


import time
from digi.xbee.devices import XBeeDevice
import RPi.GPIO as GPIO


# servo and GPIO setup
SERVO_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)


# function to change pwm according to desired angle
def set_angle(angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180

    duty = angle / 18 + 2

    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)

    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

# xbee setup
device_url = '/dev/ttyUSB3'
device = XBeeDevice(device_url, 9600)

# callback for receiving xbee packet
def servo_data_callback(xbee_msg):
    data = xbee_msg.data

    if len(data) < 2:
        return
    
    # motor command header is 0x04
    if data[0] != 0x04:
        return

    angle = data[1]

    print(f"Received servo angle: {angle}")
    set_angle(angle)

# set up xbee receiver callback
try:
    device.open()
    device.add_data_received_callback(servo_data_callback)

    print("send me something...")

    while True:
        time.sleep(1)

except Exception as e:
    print(e)

# cleanup
finally:
    try:
        device.close()
    except:
        pass

    pwm.stop()
    GPIO.cleanup()