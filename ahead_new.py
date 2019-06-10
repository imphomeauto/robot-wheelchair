#!/usr/bin/env python
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import socket
import threading

# MOTORS VARIABLES

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

# IPS VARIABLES

rX = -1
rY = -1
dir = '-'

# IPS THREAD

class Pos(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('started thread')
				
	def run(self):
		global rX
		global rY
		global dir
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('ips.local', 8000)
		sock.connect(server_address)
		message = 'pos';
		
		while True:
			sock.sendall(message)
			data = sock.recv(9)
			if data:
				arr = data.split(',')
				rX = int(arr[0])
				rY = int(arr[1])
				dir = arr[2]
				print 'X "%s", Y "%s", dir "%s"' % (rX, rY, dir)

def main():		
	#direction ahead
	motorA.forward()
	motorB.forward()

	while rX <= 40:
		motorA.speed = 23
		motorB.speed = 20

	destroy()

def destroy():
	motorA.stop()
	motorB.stop()
	GPIO.cleanup()

if __name__ == '__main__':
	pos = Pos()
	pos.start()
	try:
		main()
	except KeyboardInterrupt:
		destroy()