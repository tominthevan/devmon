'''
device.py

Created on Aug 30, 2013

@author: tom
'''

from .configObject import ConfigObject

class Device(ConfigObject):
    instances = {}
    def __init__(self,config,key):
        pass
    
class Generic(Device):
    def __init__(self,config,key):
        devtype = config[key]
        if "Expression" in devtype:
            self.expression = devtype["Expression"]
        super().__init__(config,key)


    def convert(self,millivolts):
        return float(eval(self.expression.format(millivolts)))
    
class Tmp36(Device):
    
    def __init__(self,config,key):
        devtype = config[key]
        super().__init__(config,key)
    
    def convert(self,millivolts):
        # TMP36 is an analog temperature sensor
        tempC = (millivolts - 500.0) / 10.0
#        print("TMP36: millivolts= %f3 Temp = %f3" % (millivolts, tempC))
        return(tempC)
        
class OWDevice(Device):
    def __init__(self,config,key):
        super().__init__(config,key)

# OW Sensors generally report values in applicable engineering units    
    def convert(self,reading):
        return reading
