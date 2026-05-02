# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 22:51:09 2026

@author: Emerson
"""

# -*- coding: utf-8 -*-
"""
Curtains with BH1750 + servo

Rules:
- lux < 50   -> close curtains
- lux >= 50  -> open curtains

This version assumes a NORMAL servo:
- CLOSED_ANGLE = curtains closed position
- OPEN_ANGLE   = curtains open position
"""

import time
import smbus
import RPi.GPIO as GPIO
from time import sleep

"""BH1750 setup"""
bus = smbus.SMBus(1)
address = 0x23

"""servo setup"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SERVO_PIN = 27
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

"""curtain settings"""
LIGHT_THRESHOLD = 50

"""pick the two servo positions that match your curtain setup"""
CLOSED_ANGLE = 180
OPEN_ANGLE = 0

"""remember current curtain state so servo does not keep moving"""
current_state = "unknown"


def read_lux():
    data = bus.read_i2c_block_data(address, 0x10, 2)
    lux = ((data[0] << 8) + data[1]) / 1.2
    return lux


def set_angle(angle):
    duty = angle / 18 + 2

    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)

    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)


try:
    while True:
        lux = read_lux()
        print("Luminance:", lux, "lux")

        if lux < LIGHT_THRESHOLD:
            if current_state != "closed":
                print("Too dark -> closing curtains")
                set_angle(CLOSED_ANGLE)
                current_state = "closed"
            else:
                print("Curtains already closed")

        else:
            if current_state != "open":
                print("Bright enough -> opening curtains")
                set_angle(OPEN_ANGLE)
                current_state = "open"
            else:
                print("Curtains already open")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    pwm.stop()
    GPIO.cleanup()
