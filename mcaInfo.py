#mcamain.py
import sys
import time
import serial
import port
import re
import logging
import packet
import os
import threading
from datetime import datetime

max_bins            = 8192
nanoTime=0
histogram           = [0] * max_bins
recording=False
myInfo="test"
returnmessage=""
dt=0.4
total_time=0
filename = ""
recordingTime=1800


# baudRate array defined in globalVars
# baudRate = [38400, 115200, 460800, 600000, 921600]
# select rate with index br

br=2  # this must match the speed last set by setnanospeed.py

import globalVars

from commonFunctions import(
    parse_device_info,
    printmybyte,
    sendCommand,
    readDevice,
    decodeResponse)

def mcaRecording():
	global recording
	error=True
	#print("Requesting working status...")
	sendCommand('-stt',nano)
	myReturnByte=readDevice(nano,30,0.2)
	returnmessage=decodeResponse(myReturnByte)
	if re.search('stopped', returnmessage):
		recording=False
		error=False
	if re.search('collecting',returnmessage):
		recording=True
		error=False

	return error


#															#
# ++++++++++++++++++++    START MAIN +++++++++++++++++++++++#
#															#



logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("get logger name")

print("Connecting to MAX...")
logger.info("Main requests connection")

nano = port.connectdevice(None,globalVars.baudRate[br])

if not nano:
	logger.error("Failed to connect to MAX.")
	sys.exit(0)
else:
	nano.flushInput()
	nano.flushOutput()
	print("Connected")
	logger.info("MAX connected successfully.")

print("Sending mode 0...")
sendCommand('-mode 0',nano)
myReturnByte=readDevice(nano,60,0.2)
returnmessage=decodeResponse(myReturnByte)
logger.info(returnmessage)

print("Requesting unit information...")
sendCommand('-inf',nano)
myReturnByte=readDevice(nano,30,0.2)
returnmessage=decodeResponse(myReturnByte)
logger.info(returnmessage)
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

if mcaRecording():
	print("error getting recording status")

print("Recording\t{}".format(recording))
logger.info("Recording {}".format(recording))

time.sleep(1)

print("Closing connection")
nano.close()
os._exit(0)
