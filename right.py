#!/usr/bin/env python
import time
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO

def main():
	print "********************************************"
	print "*                                          *"
	print "*                TEST LEFT                 *"
	print "*                                          *"
	print "********************************************"
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup((27, 22), GPIO.OUT)
	a = GPIO.PWM(27, 60)
	b = GPIO.PWM(22, 60)
	a.start(0)
	b.start(0)
	
	GPIO.setup(20, GPIO.IN)
	stateLastA1 = GPIO.input(20)
	
	GPIO.setup(5, GPIO.IN)
	stateLastB1 = GPIO.input(5) 
	
	stateCountA = 0
	stateCountB = 0

	def a_speed(value):
		a.ChangeDutyCycle(value)

	def b_speed(value):
		b.ChangeDutyCycle(value)
		
	motorA = TB6612.Motor(17)
	motorB = TB6612.Motor(18)
	
	motorA.pwm = a_speed
	motorB.pwm = b_speed

	motorA.speed = 30
	motorB.speed = 30
	
	#direction left
	motorA.backward()
	motorB.forward()
	
	while True:
		stateCurrentA1 = GPIO.input(20)
		stateCurrentB1 = GPIO.input(5)
	
		if stateCurrentA1 != stateLastA1:
			stateLastA1 = stateCurrentA1
			stateCountA += 1
			print "Encoder A: "+ str(stateCountA)
		
		if stateCountA == 175:
			motorA.stop()
	
		if stateCurrentB1 != stateLastB1:
			stateLastB1 = stateCurrentB1
			stateCountB += 1
			print "Encoder B: "+ str(stateCountB)
			
		if stateCountB == 175:
			motorB.stop()
			
		if stateCountA > 175 and stateCountB > 175:
			destroy()

def destroy():
	GPIO.cleanup()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()