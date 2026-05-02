# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 14:53:14 2026

@author: Emerson
Adapted from lab code
"""

#!/usr/bin/env python3

import RPi.GPIO as GPIO
from DHT11_lib import DHT11
import time
import datetime
import sys
from digi.xbee.devices import XBeeDevice

# xbee setup
device_url = '/dev/ttyUSB0'
device = XBeeDevice(device_url,9600)
device.open()

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = DHT11(pin=27)  # its at pin 13 rn

while True:
    result = instance.read()
    if result.is_valid():
        # debug information
        print("Last valid input: " + str(datetime.datetime.now()))
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
        print(result.temperature.to_bytes())
        print(result.humidity.to_bytes())

        # send payload with sensor header
        try:
            payload = result.temperature.to_bytes() + result.humidity.to_bytes()
            data = b'\x02' + payload
            device.send_data_broadcast(data)
            print('sending...')
        except Exception as e:
            print(e, '\nNo one listening')
    
    else:
        # wait until valid output
        continue
        

    time.sleep(2)
