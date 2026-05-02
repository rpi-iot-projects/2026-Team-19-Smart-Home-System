# -*- coding: utf-8 -*-
"""
@author: Fan

Adapted from lab code
"""

import RPi.GPIO as GPIO
import time
import struct

import struct
from HCSR04_lib import HCSR04
from digi.xbee.devices import XBeeDevice


# setup 
device_url = '/dev/ttyUSB1'
device = XBeeDevice(device_url,9600)
device.open()

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

TRIG = 4
ECHO = 17

GPIO.setup(TRIG,GPIO.OUT)
ranger = HCSR04(TRIG_pin=TRIG, ECHO_pin=ECHO)
ranger.init_HCSR04()

while True:
    # get reading
    try:
        dist = ranger.measure_distance()
    except Exception as e:
        print(e)
        
    print(f'ranger output: {dist} cm')

    # send payload with sensor header
    try:
        payload = struct.pack('f',dist)
        data = b'\x01' + payload
        device.send_data_broadcast(data)
        print('sending...')
    except Exception as e:
        print(e, '\nNo one listening')
    
    time.sleep(.2)
