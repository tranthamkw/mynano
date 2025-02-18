#mcamain.py
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

def calculateFilename(prefix):
	filename=""
	file=""
	data_directory  = "/home/pi/data/"
	if not os.path.exists(data_directory):
		print("path does not exist")
		os._exit(-1)
	t1=time.time()
	end_time = datetime.fromtimestamp(t1)
	dir_ext = "{}/".format(end_time.strftime("%Y-%m-%d"))
	file="{}{}.csv".format(prefix,end_time.strftime("%Y-%m-%d_%H%M%S"))
	data_directory = data_directory+dir_ext
	if not os.path.exists(data_directory):
		os.makedirs(data_directory)
	filename=data_directory+file
	return filename

def parse_device_info(info_string):
	components = info_string.split()
	settings = {}
	for i in range(0, len(components) - 1, 2):
		key = components[i]
		value = components[i + 1]
		if value.replace('.', '', 1).isdigit() and value.count('.') < 2:
			converted_value = float(value) if '.' in value else int(value)
		else:
			converted_value = value
		settings[key] = converted_value
	return settings


def printmybyte(payload):
	for char in payload:
		sys.stdout.write(hex(char))
		sys.stdout.write(" ")
		sys.stdout.flush()
	sys.stdout.write("\n")
	sys.stdout.flush()


def sendCommand(myCommand,device):
	tx_packet = packet.packet()
	tx_packet.cmd = packet.MODE_TEXT
	tx_packet.start()
	for i in range(len(myCommand)):
		tx_packet.add(ord(myCommand[i]))
	tx_packet.stop()
#	sys.stdout.write("Tx:")
	device.write(tx_packet.payload)
#	printmybyte(tx_packet.payload)
#	time.sleep(0.1)


def readDevice(device,timeOut,delay):
	READ_BUFFER = 1
	rx_byte_arr=[]
	t=0
	time.sleep(delay)
	while not((t>timeOut)or(device.in_waiting> 0)):
		time.sleep(delay)
		t+=1
		sys.stdout.write(".")
		sys.stdout.flush()
	if (t>timeOut):
		return rx_byte_arr
	READ_BUFFER = device.in_waiting
	try:
		with threading.Lock():
			rx_byte_arr = bytearray(device.read(size=READ_BUFFER))
	except serial.SerialException as e:
		print("SerialException:%s\n",e)

	return rx_byte_arr


def decodeResponse(RxByte):
	returnmsg=""
	response = packet.packet()
	for rx_byte in RxByte:
		response.read(rx_byte)
	resp_lines = []
	if (response.cmd==3):  # returned payload is text
		resp = response.payload[:len(response.payload) - 2]
		response_decoded=''
		for ch in resp:
			response_decoded+= chr(ch)
		returnmsg = response_decoded.decode("ascii")
	else:
		returnmsg=""
	return returnmsg
