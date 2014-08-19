'''
Test ads1x15
'''
from  Ads1x15.Ads1x15 import ADS1015
import wiringpi2 as wiringpi
import time

import sys
import os

if os.getuid() != 0:
  print("Must run as root. Exiting")
  sys.exit(1)

wiringpi.wiringPiSetup()
ads1 = ADS1015(address=0x49, debug=True)
while True:
  print("adc 0: %f3mv" % ads1.readADCSingleEnded(0))
  print("adc 1: %f3mv" % ads1.readADCSingleEnded(1))
  print("adc 2: %f3mv" % ads1.readADCSingleEnded(2))
  print("adc 3: %f3mv" % ads1.readADCSingleEnded(3))
  time.sleep(2)

