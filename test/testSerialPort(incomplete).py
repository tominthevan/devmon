from ..configObjects import SerialPort

conftxt = """
[serialports]
list = port1

[port1]
serialdevice = /dev/ttyUSB0
Type = Rf12demoPort
signature = [RF12demo.

serialbaudrate = 57600
serialstopbits = 1
Serialparity = N
"""
def testSerialPort():

    config = configparser.ConfigParser(allow_no_value=True,
                                       inline_comment_prefixes=('#'))
    config.read_str(conftxt)

    ports = config["serialports"]["list"].split(",")
    for port in ports:
        SerialPort.add(config, port.strip())

    sp = SerialPort.instances[0]

    
