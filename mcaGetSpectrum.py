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
rawData=[]
dt=0.05
total_time=0
filename = ""
recordingTime=60

#
# baudRate array defined in globalVars
# baudRate = [38400, 115200, 460800, 600000, 921600]
# select rate with index br

br=2 # this setting must match the speed last set by setnanospeed.py

import globalVars

from commonFunctions import(
    parse_device_info,
	calculateFilename,
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

filename = calculateFilename("RawGSPEC")
print(filename)

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


if not recording:
	print("Downloading spectrum...")
	logger.info("Requesting spectrum")
	sendCommand('-sho',nano)
	rawData=[]

	myReturnByte=readDevice(nano,5,dt)
	while len(myReturnByte)>0:
		sys.stdout.write(".{} bytes".format(len(myReturnByte)))
		sys.stdout.flush()
		for rx_byte in myReturnByte:
			rawData.append(rx_byte)
		myReturnByte=readDevice(nano,5,dt)

	print("Return raw data total length {}".format(len(rawData)))
	logger.info("Saving data to file {}".format(filename))

	with open(filename, mode='w') as f:
		f.write(myInfo)
		for x in range(len(rawData)):
			f.write(bytes(rawData[x]))
			f.write("\n")

else:
	print("nano recording. spectrum not aquired")

print("Closing connection")
nano.close()
os._exit(0)
