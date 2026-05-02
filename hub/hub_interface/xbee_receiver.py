# -*- coding: utf-8 -*-
"""
@author: Fan

Class for handling all XBee communication on hub side
"""

from digi.xbee.devices import XBeeDevice
import time
import struct

class DataAggregator():
    def __init__(self, xbee_url, enable_debug=False):
        # enables debug information output
        self.enable_debug = enable_debug
        
        # xbee setup
        self.xbee_device = XBeeDevice(xbee_url,9600)
        try: 
            self.xbee_device.open()
            self.xbee_device.add_data_received_callback(self.recv_callback)
        except Exception as e:
            print(e)

        # initial data states
        self.dist_reading = 0
        self.string = ""
        self.humidity = 0
        self.temp = 0
        self.motor_angle = 0
        self.lumens = 0

    # callback upon receiving xbee packet
    def recv_callback(self, xbee_msg):
        data = xbee_msg.data
        
        # check header for sensor/actuator type and decode accordingly
        # hub is sender for motor data so it shouldn't receive anything
        transmit_type = data[0]
        match transmit_type:
            case 1:                     # ranger
                if self.enable_debug:
                    print('got ranger data')
                self.dist_reading = struct.unpack('f',data[1:])[0]
            case 2:                     # temperature & humidity
                if self.enable_debug:
                    print('got HT data')
                self.temp = data[1]
                self.humidity = data[2]
            case 3:                     # light
                if self.enable_debug:
                    print('got lumen data')
                self.lumens = struct.unpack('f',data[1:])[0]
            case 4:                     # motor 
                pass
            case 5:                     # dummy data for initial debug
                if self.enable_debug:
                    print('got dummy data')
                self.string = data[1:].decode()
            
    # for closing xbee connection
    def close(self):
        self.xbee_device.close()

    # displays all current data state for debug
    def disp(self):
        print(f'-----stored data at time {time.time():.3f}-----')
        print(f'debug string: {self.string}')
        print(f'ranger distance: {self.dist_reading}')
        print(f'temperature: {self.temp} C')
        print(f'humidity: {self.humidity} %')
        
    # send servo command (accessed via ble_interface)
    def send_angle(self,value):
        self.motor_angle = value
        return self.xbee_device.send_data_broadcast(b'\x04'+value)
    
    # getters for data access on ble side
    def get_temp(self):
        return f'{self.temp}'.encode()

    def get_humidity(self):
        return f'{self.humidity}'.encode()

    def get_dist(self):
        return f'{self.dist_reading:.2f}'.encode()

    def get_lumen(self):
        return f'{self.lumens:.2f}'.encode()

    def get_angle(self):
        return self.motor_angle
    
# run this file for DEBUG ONLY 
# ble_interface holds DataAggregator object to handle xbee internally
if __name__ == "__main__":
    try:
        node = DataAggregator('/dev/ttyUSB0')
        while True:
            node.disp()
            time.sleep(5)   # display current data every 5 seconds
    except KeyboardInterrupt:
        print('keyboard interrupt')
