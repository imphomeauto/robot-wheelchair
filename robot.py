#!/usr/bin/env python
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import socket
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import sleep

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

# ENCODERS VARIABLES

GPIO.setup(20, GPIO.IN)	
GPIO.setup(5, GPIO.IN)

turnLeftEnc = 355
turnRightEnc = 355

# IPS VARIABLES

rX = -1
rY = -1
dir = 'R'

# IPS THREAD

class Pos(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('started thread')
				
	def run(self):
		global rX
		global rY
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('ips.local', 8000)
		sock.connect(server_address)
		message = 'pos';
		
		while True:
			sock.sendall(message)
			data = sock.recv(7)
			if data:
				arr = data.split(',')
				rX = int(arr[0])
				rY = int(arr[1])
				#print 'X "%s", Y "%s"' % (rX, rY)

class MyHTTPServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		HTTPServer.__init__(self, *args, **kwargs)
		self.pos = Pos()
		self.pos.start()

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.send_header('Access-Control-Allow-Origin','*')
		self.end_headers()
		output = '<p>X: %s</p><p>Y: %s</p><p>dir: %s</p><p>path: %s</p>' % (rX, rY, dir, self.path)
		if self.path.startswith( '/a', 0, 2 ) :
			robot_ahead(int(self.path[2:]))
		elif self.path == '/l' :
			robot_left()
		elif self.path == '/r' :
			robot_right()
		self.wfile.write(output)


def robot_ahead(destination):
	global dir
	global rX
	global rY
	
	#direction ahead
	motorA.forward()
	motorB.forward()
	
	if dir == 'R' :
		while rX <= destination:
			motorA.speed = 23
			motorB.speed = 20
	elif dir == 'L' :
		while rX >= destination:
			motorA.speed = 23
			motorB.speed = 20
	elif dir == 'D' :
		while rY <= destination:
			motorA.speed = 23
			motorB.speed = 20
	elif dir == 'U' :
		while rY <= destination:
			motorA.speed = 23
			motorB.speed = 20
	
	robot_stop()

	
def robot_left():	
	global dir
	
	#direction left
	motorA.forward()
	motorB.backward()
	
	turn = True
	
	stateCountA = 0
	stateCountB = 0
	
	stateLastA1 = GPIO.input(20)
	stateLastB1 = GPIO.input(5)
	
	motorA.speed = 29
	motorB.speed = 28
	
	while turn:
		
		stateCurrentA1 = GPIO.input(20)
		stateCurrentB1 = GPIO.input(5)
	
		if stateCurrentA1 != stateLastA1:
			stateLastA1 = stateCurrentA1
			stateCountA += 1
		
		if stateCountA >= turnLeftEnc:
			motorA.stop()
	
		if stateCurrentB1 != stateLastB1:
			stateLastB1 = stateCurrentB1
			stateCountB += 1
			
		if stateCountB >= turnLeftEnc:
			motorB.stop()
			
		if stateCountA >= turnLeftEnc and stateCountB >= turnLeftEnc:
			turn = False
	
	if dir == 'R' :
		dir = 'U'
	elif dir == 'L' :
		dir = 'D'
	elif dir == 'D' :
		dir = 'R'
	elif dir == 'U' :
		dir = 'L'

	
def robot_right():
	global dir
	
	#direction right
	motorA.backward()
	motorB.forward()
	
	turn = True
	
	stateCountA = 0
	stateCountB = 0
	
	stateLastA1 = GPIO.input(20)
	stateLastB1 = GPIO.input(5)
	
	motorA.speed = 29
	motorB.speed = 28
	
	while turn:
		
		stateCurrentA1 = GPIO.input(20)
		stateCurrentB1 = GPIO.input(5)
	
		if stateCurrentA1 != stateLastA1:
			stateLastA1 = stateCurrentA1
			stateCountA += 1
		
		if stateCountA >= turnRightEnc:
			motorA.stop()
	
		if stateCurrentB1 != stateLastB1:
			stateLastB1 = stateCurrentB1
			stateCountB += 1
			
		if stateCountB >= turnRightEnc:
			motorB.stop()
		
		if stateCountA >= turnRightEnc and stateCountB >= turnRightEnc:
			turn = False
	
	if dir == 'R' :
		dir = 'D'
	elif dir == 'L' :
		dir = 'U'
	elif dir == 'D' :
		dir = 'L'
	elif dir == 'U' :
		dir = 'R'


def robot_stop():
	motorA.stop()
	motorB.stop()


if __name__ == '__main__':
	server = MyHTTPServer(('', 8000), RequestHandler)
	print('Starting server at port 8000')
	server.serve_forever()
