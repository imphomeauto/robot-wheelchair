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
				#print 'X "%s", Y "%s", dir "%s"' % (rX, rY, dir)


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
	#direction left
	motorA.forward()
	motorB.backward()
	
	motorA.speed = 23
	motorB.speed = 20
	
	sleep(1)
	
	robot_stop()
	
def robot_right():		
	#direction right
	motorA.backward()
	motorB.forward()
	
	motorA.speed = 23
	motorB.speed = 20
	
	sleep(1)
	
	robot_stop()

def robot_stop():
	motorA.stop()
	motorB.stop()

if __name__ == '__main__':
	server = MyHTTPServer(('', 8000), RequestHandler)
	print('Starting server at port 8000')
	server.serve_forever()