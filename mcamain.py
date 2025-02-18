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
dt=0.4
total_time=0
filename = ""
recordingTime=60

#
# baudRate array defined in globalVars
# baudRate = [38400, 115200, 460800, 600000, 921600]
# select rate with index br

br=0 # this setting must match the speed last set by setnanospeed.py

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

#recording=True

if not recording:
	print("Sending start {}s silent mode...".format(recordingTime))
	sendCommand('-sta {} -r -s'.format(recordingTime),nano)
	myReturnByte=readDevice(nano,30,dt)
	logger.info(decodeResponse(myReturnByte))

	mcaRecording() #determine if recording
	while recording:
		sendCommand('-inf',nano) #get information from nano.
		myReturnByte=readDevice(nano,30,dt)
		returnmessage=decodeResponse(myReturnByte)
		if re.search('VERSION', returnmessage):
			myInfo=returnmessage
		info_dict = parse_device_info(myInfo)
		nanoTime = info_dict.get('t')
		for x in range(10):
			sys.stdout.write(".")
			sys.stdout.flush()
			time.sleep(0.5)
		print("Elapse Time:{}\tTemp: {}C".format(nanoTime,info_dict.get('T1')))
		mcaRecording()


print("Sending stop...")
logger.info("Requesting stop")
sendCommand('-sto',nano)
myReturnByte=readDevice(nano,30,dt)
returnmessage=decodeResponse(myReturnByte)
logger.info(returnmessage)

time.sleep(1)

print("Requesting information")
sendCommand('-inf',nano) #get information from nano.
myReturnByte=readDevice(nano,30,dt)
returnmessage=decodeResponse(myReturnByte)
if re.search('VERSION', returnmessage):
	myInfo=returnmessage

time.sleep(1)

print("Downloading spectrum...")
logger.info("Requesting spectrum")
sendCommand('-sho',nano)
rawData=[]

myReturnByte=readDevice(nano,5,dt)
while len(myReturnByte)>0:
	sys.stdout.write(".")
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

"""
if len(rawData)>33830:
	print("processing histogram data")
	div_idx=[]
	idx=[]

	for x in range(16,len(rawData)):
		if (rawData[x-1]==1)and(rawData[x-2]==254)and(rawData[x-3]==255)and(rawData[x-4]==165):
			offset=(rawData[x] & 0xFF) | ((rawData[x+1]&0xFF)<<8)
			if(x+2+4*63+3)<len(rawData):
				div_idx.append(x)
				for i in range(0,64):
					index = offset+i
					idx.append(index)
					value = (rawData[x+2+4*i]&0xFF) | ((rawData[x+2+4*i+1]&0xFF)<<8) | ((rawData[x+2+4*i+2]&0xFF)<<16) | ((rawData[x+2+4*i+3]&0xFF)<<24)
					histogram[index] = value & 0x7FFFFFF
		elif (rawData[x-1]==4)and(rawData[x-2]==254)and(rawData[x-3]==255)and(rawData[x-4]==165):
				if(x+9<len(rawData)):
					total_time = (rawData[x]&0xFF) | ((rawData[x+1]&0xFF)<<8) | ((rawData[x+2]&0xFF)<<16) | ((rawData[x+3]&0xFF)<<24)
					cps = (rawData[x+6]&0xFF) | ((rawData[x+7]&0xFF)<<8) | ((rawData[x+8]&0xFF)<<16) | ((rawData[x+9]&0xFF)<<24)

	print("total time:{}".format(total_time))
	print("CPS:{}".format(cps))
	print("writing histogram to histogram.csv")
	f=open("histogram.csv","w")
	f.write(myInfo)
	f.write("\nChannel,Idx,Count\n")
	for x in range(len(idx)):
		f.write("{},{},{}\n".format(x,idx[x],histogram[x]))
	f.close()



print("writing delta index")
f=open("deltaidx.csv","w")
f.write("i+1,idx,deltaidx\n")
for x in range(len(div_idx)-1):
	f.write("{},{},{}\n".format(x+1,div_idx[x+1],div_idx[x+1]-div_idx[x]))
f.close()

"""

print("Closing connection")
nano.close()
os._exit(0)
