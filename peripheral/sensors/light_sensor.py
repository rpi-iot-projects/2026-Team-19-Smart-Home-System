# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 00:36:31 2026

@author: Emerson

I used this tutorial to learn to control the light sensor: 
    https://randomnerdtutorials.com/raspberry-pi-pico-bh1750-micropython/
"""

import time
import smbus
import RPi.GPIO as GPIO
from digi.xbee.devices import XBeeDevice

# xbee setup
device_url='/dev/ttyUSB3'
device=XBeeDevice(device_url, 9600)
device.open()

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

bus = smbus.SMBus(1)
address = 0x23

while True:
    try:
        # read light level
        level = bus.read_i2c_block_data(address, 0x10, 2)
        lux = ((level[0] << 8) + level[1]) / 1.2
        print("Luminance:", lux, "lux")
        
        # send payload with sensor header
        payload = bytes(level)
        data = b'\x03' + payload
        device.send_data_broadcast(data)
        print('sending...')
        
    except Exception as e:
        print(e, 'no one listening...')
                
    
    time.sleep(2)