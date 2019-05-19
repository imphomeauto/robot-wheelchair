#!/usr/bin/env python
import time
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO

def main():
	import time

	GPIO.setmode(GPIO.BCM)
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
	motorA.debug = False
	motorB.debug = False
	motorA.pwm = a_speed
	motorB.pwm = b_speed

	motorA.speed = 30
	motorB.speed = 30

	# left
	motorA.backward()
	motorB.backward()
	time.sleep(0.9)
	motorA.stop()
	motorB.stop()

	
def destroy():
	motorA.stop()
	motorB.stop()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()