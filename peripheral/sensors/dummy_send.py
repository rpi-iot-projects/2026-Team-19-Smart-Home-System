# -*- coding: utf-8 -*-
"""
@author: Fan

This is a debug file used to test xbee receiver functionalities
It sends constant 'abcd' bytes to receiver with 0x05 prefix
"""

import time

from digi.xbee.devices import XBeeDevice

device_url = '/dev/ttyUSB0'
device = XBeeDevice(device_url,9600)
device.open()


while True: 
    try:
        data = b'abcd'
        data = b'\x05' + data
        device.send_data_broadcast(data)
        print('sending...')
    except Exception as e:
        print(e, '\nNo one listening')
    #print(dist)
    time.sleep(1)
