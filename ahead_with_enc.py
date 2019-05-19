#!/usr/bin/env python
import time
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import threading
import urllib, json

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup((27, 22), GPIO.OUT)
a = GPIO.PWM(27, 60)
b = GPIO.PWM(22, 60)
a.start(0)
b.start(0)

GPIO.setup(20, GPIO.IN)
encoderA = GPIO.input(20)

GPIO.setup(5, GPIO.IN)
encoderB = GPIO.input(5)

encoderA_value = 0
encoderB_value = 0

def a_speed(value):
	a.ChangeDutyCycle(value)

def b_speed(value):
	b.ChangeDutyCycle(value)
	
motorA = TB6612.Motor(17)
motorB = TB6612.Motor(18)

motorA.pwm = a_speed
motorB.pwm = b_speed

encoderA_prev_error = 0
encoderB_prev_error = 0

encoderA_sum_error = 0
encoderB_sum_error = 0

SAMPLETIME = 0.1
TARGET = 18

url = "http://ips.local:8000"

class Encoders(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('encoders thread started')
		
	def run(self):
		global encoderA
		global encoderB
		global encoderA_value
		global encoderB_value

		while True:
			encoderA_read = GPIO.input(20)
			encoderB_read = GPIO.input(5)
		
			if encoderA_read != encoderA:
				encoderA = encoderA_read
				encoderA_value += 1
		
			if encoderB_read != encoderB:
				encoderB = encoderB_read
				encoderB_value += 1

			#print "enA: "+ str(encoderA_value) + " - enB: " + str(encoderB_value)

def main():
	enc = Encoders()
	enc.start()
		
	global encoderA
	global encoderB
	global encoderA_value
	global encoderB_value
	global encoderA_prev_error
	global encoderB_prev_error
	global encoderA_sum_error
	global encoderB_sum_error
	
	motorA.speed = 22
	motorB.speed = 20
	
	#direction ahead
	motorA.forward()
	motorB.forward()		

	time.sleep(SAMPLETIME)
	
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	print data["x"]
	print data["y"]
	print data["dir"]

	while True:
		
		new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
		new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
				
		motorA.speed = int(abs(new_motorA_speed))
		motorB.speed = int(abs(new_motorB_speed))
		
		encoderA_value = 0
		encoderB_value = 0
		
		time.sleep(SAMPLETIME)

def destroy():
	motorA.stop()
	motorB.stop()
	GPIO.cleanup()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()