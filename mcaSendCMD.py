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
command = ""
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
    filename="/home/pi/data/mcaCMDlog.csv",
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)

#print("Connecting to MAX...")

nano = port.connectdevice(None,globalVars.baudRate[br])

if not nano:
	logger.error("Failed to connect to MAX.")
	sys.exit(0)
else:
	nano.flushInput()
	nano.flushOutput()
#	print("Connected")
#	logger.info("MAX connected successfully.")


command=sys.argv[1]

print("Sending mode 0...")
#logger.info("send mode 0")
sendCommand('-mode 0',nano)
myReturnByte=readDevice(nano,60,0.2)
returnmessage=decodeResponse(myReturnByte)
#logger.info(returnmessage)

#get recording status
#mcaRecording()
"""
print("Requesting unit information...")
sendCommand('-inf',nano)
myReturnByte=readDevice(nano,30,0.2)
returnmessage=decodeResponse(myReturnByte)
print(returnmessage)
#logger.info(returnmessage)
"""


time.sleep(0.1)
print("Sending command {}".format(command))
logger.info("Send command {}".format(command))
sendCommand(command,nano)
myReturnByte=readDevice(nano,30,0.2)
returnmessage=decodeResponse(myReturnByte)
logger.info(returnmessage)
print(returnmessage)

time.sleep(0.1)

nano.close()
os._exit(0)
