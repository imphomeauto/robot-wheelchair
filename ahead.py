#!/usr/bin/env python
import time
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO

print "***** FORWARD *****"
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)
#GPIO.setup(20, GPIO.IN)
#GPIO.setup(21, GPIO.IN)

def handle_pulse_event():
	if GPIO.input(5):
		print "5"
	if GPIO.input(6):
		print "6"

def a_speed(value):
	a.ChangeDutyCycle(value)

def b_speed(value):
	b.ChangeDutyCycle(value)

#GPIO.add_event_detect(5, GPIO.RISING)
#GPIO.add_event_detect(6, GPIO.RISING)
#GPIO.add_event_callback(5, handle_pulse_event)
#GPIO.add_event_callback(6, handle_pulse_event)
#GPIO.add_event_detect(20, GPIO.RISING, callback=handle_pulse_event)
#GPIO.add_event_detect(21, GPIO.RISING, callback=handle_pulse_event)

a = GPIO.PWM(27, 60)
b = GPIO.PWM(22, 60)
a.start(0)
b.start(0)

motorA = TB6612.Motor(17)
motorB = TB6612.Motor(18)
motorA.debug = False
motorB.debug = False
motorA.pwm = a_speed
motorB.pwm = b_speed

motorA.speed = 20
motorB.speed = 20

start = time.time()
period = 1

try:
	while True:
		handle_pulse_event()
		motorA.forward()
		motorB.forward()
		#time.sleep(0.8)
		#motorA.stop()
		#motorB.stop()
		if time.time() > start + period : break

except KeyboardInterrupt:
	pass

motorA.stop()
motorB.stop()
GPIO.cleanup()