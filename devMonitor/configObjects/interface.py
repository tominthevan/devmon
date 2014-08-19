'''
Created on Aug 30, 2013

@author: tom
'''
import random
import wiringpi2 as wiringpi

from .configObject import ConfigObject

class Interface(ConfigObject):
    instances = {}

    def __init__(self, config, key):

        pass
    
class GPIO(Interface):
    next_pin = 65           # using WiringPi first available pin is #81
    
    def __init__(self,config,key):
        
        pass
    
    @classmethod
    def add_pins(cls,pins):
        base = cls.next_pin
        cls.next_pin = cls.next_pin + pins
        return(base)
        
class I2C(GPIO):
    
    def __init__(self, config, key):
        iface = config[key]
        self.port = int(iface["Port"],0)
        super().__init__(config,key)

class PCF8591(I2C):
    
    def __init__(self, config, key):
        iface = config[key]
        self.address = int(iface["Address"],0)
        self.pin_base = self.add_pins(4)
        self.fullScale = float(iface["FullScale"])*1000.
        wiringpi.pcf8591Setup(self.pin_base, self.address)
        super().__init__(config,key)


    def get_value(self, channel):
#        raw_value = random.random()
#
#       reading is an 8 bit value (i.e.0 - 255)
#       return millivolts read by the adc
        int_value = wiringpi.analogRead(self.pin_base + channel)
        millivolts = self.fullScale * int_value / 255.0
#        print("getvalue %f3(%i) from channel %i at address %i on port %i" % (millivolts, int_value, channel,self.address, self.port))
        return(millivolts)
