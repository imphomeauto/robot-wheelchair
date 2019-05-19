#!/usr/bin/env python
import time
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import urllib, json

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup((27, 22), GPIO.OUT)
a = GPIO.PWM(27, 60)
b = GPIO.PWM(22, 60)
a.start(0)
b.start(0)

def a_speed(value):
	a.ChangeDutyCycle(value)

def b_speed(value):
	b.ChangeDutyCycle(value)
	
motorA = TB6612.Motor(17)
motorB = TB6612.Motor(18)

motorA.pwm = a_speed
motorB.pwm = b_speed

url = "http://ips.local:8000"

def main():	
	
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	posX = data["x"]
	posY = data["y"]
	print "x: " + str(data["x"]) + " - y: " + str(data["y"])
	
	if (posX < 0) or (posY < 0):
		destroy()
	
	motorA.speed = 23
	motorB.speed = 20
	
	#direction ahead
	motorA.forward()
	motorB.forward()

	while posX <= 20:
	
		response = urllib.urlopen(url)
		data = json.loads(response.read())
		posX = data["x"]
		posY = data["y"]
		print "x: " + str(data["x"]) + " - y: " + str(data["y"])

	destroy()

def destroy():
	motorA.stop()
	motorB.stop()
	GPIO.cleanup()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()