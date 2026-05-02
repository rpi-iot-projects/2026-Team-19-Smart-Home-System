# -*- coding: utf-8 -*-
"""
@author: Fan

Class and main function for BLE advertisement and functions
"""
import dbus

# re-use objects from lab code
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor

# for handling xbee data, see xbee_receiver.py
from xbee_receiver import DataAggregator

# GATT setup
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

# main advertisement
class XBeeAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("XBeeData")
        self.include_tx_power = True

# main service
class XBeeService(Service):
    SMARTHOME_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):

        Service.__init__(self, index, self.SMARTHOME_SVC_UUID, True)
        
        # peripheral and password characteristics
        self.add_characteristic(TempCharacteristic(self))
        self.add_characteristic(HumidCharacteristic(self))
        self.add_characteristic(DistCharacteristic(self))
        self.add_characteristic(MotorCharacteristic(self))
        self.add_characteristic(LumenCharacteristic(self))
        self.add_characteristic(PassKeyCharacteristic(self))
        
        # data aggregator from xbee_receiver.py
        self.xbee_data = DataAggregator('/dev/ttyUSB0')

        # passkey-based security
        self.password = b'abcd'
        self.attempt = b''

    # wrappers for data aggregator functions (xbee data & communication)
    # disables ble access to xbee without correct passkey
    def get_temp(self):
        return self.xbee_data.get_temp() if self.attempt == self.password else b''

    def get_humidity(self):
        return self.xbee_data.get_humidity() if self.attempt == self.password else b''
        
    def get_dist(self):
        return self.xbee_data.get_dist() if self.attempt == self.password else b''

    def get_motor_angle(self):
        return self.xbee_data.get_angle() if self.attempt == self.password else b''

    def get_lumens(self):
        return self.xbee_data.get_lumen() if self.attempt == self.password else b''

    def send_motor_cmd(self,val):
        if self.attempt == self.password:
            self.xbee_data.send_angle(val)
        

# characteristic for temperature READ ONLY
class TempCharacteristic(Characteristic):
    TEMP_CHARACTERISTIC_UUID = "00000007-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, self.TEMP_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(TempDescriptor(self))
        
    def get_value(self):
        return self.service.get_temp()
        
    def set_val_callback(self):
        if self.notifying:
            value = self.get_value()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        
        value = self.get_value()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_val_callback)

    def StopNotify(self):
        self.notifying = False
        
    # cast value directly into ByteArray since data is already encoded
    # see getters of xbee_receiver.py
    def ReadValue(self, options):
        print("reading temp")
        return dbus.ByteArray(self.get_value())
        
# decriptor for temperature 
class TempDescriptor(Descriptor):
    TEMP_DESCRIPTOR_UUID = "2901"
    TEMP_DESCRIPTOR_VALUE = "Temperature Sensor Output (C)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.TEMP_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value

# characteristic for humidity READ ONLY
class HumidCharacteristic(Characteristic):
    HUMID_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        self.notifying = False
        
        Characteristic.__init__(
                self, self.HUMID_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(HumidDescriptor(self))
        
    def get_value(self):
        return self.service.get_humidity()
        
    def set_val_callback(self):
        if self.notifying:
            value = self.get_value()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        return self.notifying
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        
        value = self.get_value()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_val_callback)

    def StopNotify(self):
        self.notifying = False
        
    # cast value directly into ByteArray since data is already encoded
    # see getters of xbee_receiver.py
    def ReadValue(self, options):
        print("reading humidity")
        return dbus.ByteArray(self.get_value())
        
# descriptor for humidity
class HumidDescriptor(Descriptor):
    TEMP_DESCRIPTOR_UUID = "2901"
    TEMP_DESCRIPTOR_VALUE = "Humidity Sensor Output (%)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.TEMP_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value
        
# characteristic for distance (ranger output) READ ONLY
class DistCharacteristic(Characteristic):
    DIST_CHARACTERISTIC_UUID = "00000004-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        self.notifying = False
        
        Characteristic.__init__(
                self, self.DIST_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(DistDescriptor(self))
        
    def get_value(self):
        return self.service.get_dist()
        
    def set_val_callback(self):
        if self.notifying:
            value = self.get_value()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        return self.notifying
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        
        value = self.get_value()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_val_callback)

    def StopNotify(self):
        self.notifying = False
        
    # cast value directly into ByteArray since data is already encoded
    # see getters of xbee_receiver.py
    def ReadValue(self, options):
        print("reading ranger output")
        return dbus.ByteArray(self.get_value())
        
# descriptor for ranger output READ ONLY
class DistDescriptor(Descriptor):
    DIST_DESCRIPTOR_UUID = "2901"
    DIST_DESCRIPTOR_VALUE = "Ranger Output (cm)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.DIST_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.DIST_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value

# characteristic for motor READ AND WRITE
class MotorCharacteristic(Characteristic):
    MOTOR_CHARACTERISTIC_UUID = "00000005-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        Characteristic.__init__(
                self, self.MOTOR_CHARACTERISTIC_UUID,
                ["read", "write"], service)
        self.add_descriptor(MotorDescriptor(self))
        
    # sends desired motor angle 
    def WriteValue(self, value, options):
        target = value[0].to_bytes()
        self.service.send_motor_cmd(target)
        print("writing motor command")
        
    # cast into byte as value is not encoded string unlike the others
    # see getters of xbee_receiver.py
    def ReadValue(self, options):
        value = []
        val = self.service.get_motor_angle()
        value.append(dbus.Byte(val))
        print("reading motor angle")
        return value

# descriptor for motor
class MotorDescriptor(Descriptor):
    MOTOR_DESCRIPTOR_UUID = "2901"
    MOTOR_DESCRIPTOR_VALUE = "Send motor command"
    
    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.MOTOR_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.MOTOR_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value

# characteristic for light sensor READ ONLY
class LumenCharacteristic(Characteristic):
    LUMEN_CHARACTERISTIC_UUID = "00000006-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        self.notifying = False
        
        Characteristic.__init__(
                self, self.LUMEN_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(LumenDescriptor(self))
        
    def get_value(self):
        return self.service.get_lumens()
        
    def set_val_callback(self):
        if self.notifying:
            value = self.get_value()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        return self.notifying
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        
        value = self.get_value()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_val_callback)

    def StopNotify(self):
        self.notifying = False
        
    # cast value directly into ByteArray since data is already encoded
    # see getters of xbee_receiver.py
    def ReadValue(self, options):
        print("reading lumens output")
        return dbus.ByteArray(self.get_value())
        
# descriptor for light sensor
class LumenDescriptor(Descriptor):
    LUMEN_DESCRIPTOR_UUID = "2901"
    LUMEN_DESCRIPTOR_VALUE = "Light Sensor Output (lux)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.LUMEN_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.LUMEN_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value

# characteristic for passkey WRITE ONLY
class PassKeyCharacteristic(Characteristic):
    PASSKEY_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"
    
    def __init__(self, service):
        Characteristic.__init__(
                self, self.PASSKEY_CHARACTERISTIC_UUID,
                ["write"], service)
        self.add_descriptor(PassKeyDescriptor(self))
        
    # stores current passkey attempt to compare to internal key
    def WriteValue(self, value, options):
        target = dbus.ByteArray(value)
        self.service.attempt = target
        
# descriptor for passkey
class PassKeyDescriptor(Descriptor):
    PASSKEY_DESCRIPTOR_UUID = "2901"
    PASSKEY_DESCRIPTOR_VALUE = "Enter PassKey to Access Data & Controls"
    
    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.PASSKEY_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.PASSKEY_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value

# start application
app = Application()
app.add_service(XBeeService(0))
app.register()

adv = XBeeAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
