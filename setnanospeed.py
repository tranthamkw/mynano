#setnanospeed.py
import sys
import time
import serial
import port
import logging
import packet
import os
import re
import threading
from datetime import datetime

recording=False
myInfo="test"
returnMessage=""

# baudRate array defined in globalVars
# baudRate = [38400, 115200, 460800, 600000, 921600]
# select rate with index br

br=3
brNew=2

import globalVars

from commonFunctions import(
	parse_device_info,
	printmybyte,
	sendCommand,
	readDevice,
	decodeResponse)

#															#
# ++++++++++++++++++++    START MAIN +++++++++++++++++++++++#
#															#


data_directory  = os.getcwd()
# Set up logging configuration
if not os.path.exists(data_directory):
	os.makedirs(data_directory)

logging.basicConfig(
    filename="setspeedlog.log",
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("action log located at {}/setspeedlog.log".format(data_directory))
logger = logging.getLogger(__name__)

print("Connecting to device ...")

nano = port.connectdevice(None,globalVars.baudRate[br])

if not nano:
	logger.error("Failed to connect to MAX.")
	sys.exit(0)
else:
	nano.flushInput()
	nano.flushOutput()
	print("Connected")

print("Sending mode 0...")

sendCommand('-mode 0',nano)
myReturnByte=readDevice(nano,60,0.2)
print(decodeResponse(myReturnByte))

print("Requesting unit information...")
sendCommand('-inf',nano)
myReturnByte=readDevice(nano,30,0.2)
returnmessage=decodeResponse(myReturnByte)
if re.search('VERSION', returnmessage):
	myInfo=returnmessage
	info_dict = parse_device_info(myInfo)
	print("MAX Version:\t\t{}".format(info_dict.get('VERSION')))
	nanoTime = info_dict.get('t')
	print("Discriminator:\t\t{}".format(info_dict.get('NOISE')))
	print("Elapse Time:\t\t{}".format(nanoTime))
	print("Temperature:\t\t{} C".format(info_dict.get('T1')))
	print("HighVoltage(0-255):\t{}".format(info_dict.get('POT')))
else:
	print("Invalid response from device information")

print("Requesting working status...")
sendCommand('-stt',nano)
myReturnByte=readDevice(nano,30,0.2)
returnmessage=decodeResponse(myReturnByte)

if re.search('stopped', returnmessage):
	recording=False
elif re.search('collecting',returnmessage):
	recording=True

if not recording:
	logger.info("set speed to {}".format(globalVars.baudRate[brNew]))
	print("sending speed information {}".format(globalVars.baudRate[brNew]))
	sendCommand('-spd {}'.format(globalVars.baudRate[brNew]),nano)
# nothing is returned from setting the speed
else:
	print("Device is recording. Cannot change speed. Recording\t{}".format(recording))

print("Ensure to update any software that use this setting")
print("Closing connection")
time.sleep(0.2)
nano.close()

os._exit(0)
