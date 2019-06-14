from __future__ import absolute_import
from Queue import Queue
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import socket
import threading
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import sleep

################### MOTORS VARIABLES ###################

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
motorAaheadSpeed = 17
motorBaheadSpeed = 16

################### ENCODERS VARIABLES ###################

GPIO.setup(20, GPIO.IN)
encoderA = GPIO.input(20)
GPIO.setup(5, GPIO.IN)
encoderB = GPIO.input(5)
turnLeftEnc = 362
turnRightEnc = 362
encoderA_value = 0
encoderB_value = 0
encoderA_prev_error = 0
encoderB_prev_error = 0
encoderA_sum_error = 0
encoderB_sum_error = 0
SAMPLETIME = 0.05
TARGET = 18

################### INS VARIABLES ###################
maze='''\
1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 0 0 0 0 1 1 1 0 0 0 0 0 1
1 1 1 1 0 1 1 1 0 1 1 1 1 1
1 1 1 1 0 1 1 1 0 1 1 1 1 1
1 1 1 1 0 1 1 1 0 1 1 1 1 1
1 1 1 1 0 1 1 1 0 1 1 1 1 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1
'''

step = {'U': (-1, 0), 'D': (1, 0), 'R': (0, 1), 'L': (0, -1)}

def show(matrix):
	for line in matrix:
		print line
	print

################### IPS VARIABLES ###################

rX = -1
rY = -1
dir = 'R'
room = 'out'

################### IPS THREAD ###################

class Pos(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('position started thread')
	def run(self):
		self.kill = False
		global rX
		global rY
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('ips.local', 8000)
		sock.connect(server_address)
		message = 'pos';
		while not self.kill:
			sock.sendall(message)
			data = sock.recv(5)
			if data:
				arr = data.split(',')
				rX = int(arr[0])
				rY = int(arr[1])
				#print 'X "%s", Y "%s"' % (rX, rY)

class Lights(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('lights started thread')
	def run(self):
		self.kill = False
		global rX
		global rY
		global room
		light = -1;
		while not self.kill:
			if rX <= 6 and rY >= 5 and light != 0:
				#entrance
				light = 0;
				room = 'entrance'
				urllib2.urlopen("http://192.168.1.4/offall")
				urllib2.urlopen("http://192.168.1.4/on/0")
			elif rX <= 6 and rY < 5 and light != 2:
				#toilet
				light = 2
				room = 'toilet'
				urllib2.urlopen("http://192.168.1.4/offall")
				urllib2.urlopen("http://192.168.1.4/on/2")
			elif rX > 6 and rY < 5 and light != 4:
				#bedroom
				light = 4
				room = 'bedroom'
				urllib2.urlopen("http://192.168.1.4/offall")
				urllib2.urlopen("http://192.168.1.4/on/4")
			elif rX > 6 and rY >= 5 and light != 6:
				#kitchen
				light = 6
				room == 'kitchen'
				urllib2.urlopen("http://192.168.1.4/offall")
				urllib2.urlopen("http://192.168.1.4/on/6")
			elif rX < 0 and rY < 0:
				light = -1
				room = 'out'
				#out of the home, off all
				urllib2.urlopen("http://192.168.1.4/offall")
			sleep(0.4)

class Encoders(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('encoders thread start')
	def run(self):
		self.kill = False
		global encoderA
		global encoderB
		global encoderA_value
		global encoderB_value
		while not self.kill:
			encoderA_read = GPIO.input(20)
			encoderB_read = GPIO.input(5)
			if encoderA_read != encoderA:
				encoderA = encoderA_read
				encoderA_value += 1
			if encoderB_read != encoderB:
				encoderB = encoderB_read
				encoderB_value += 1
		print('encoders thread stop')

class MyHTTPServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		HTTPServer.__init__(self, *args, **kwargs)

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global rX
		global rY
		global dir
		global room
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin','*')
		output = '-'
		if self.path == '/init' :
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			output = '{"x": %s,"y": %s, "dir": "%s", "room": "%s"}' % (rX, rY, dir, room)
		elif self.path.startswith( '/go_', 0, 4 ) :
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			navigate(str(self.path[4:]))
			action = 'move to %s' % str(self.path[4:])
			output = '{"x": %s,"y": %s, "dir": "%s", "room": "%s", "action": "%s"}' % (rX, rY, dir, room, action)
		else:
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			output = urllib2.urlopen("file:///home/pi/IHA-Robot-Motors/index.html").read()
		self.wfile.write(output)

def navigate(destination):
	global room
	if room == destination or room == 'out':
		return
	elif destination == 'kitchen':
		move(10,7)
	elif destination == 'toilet':
		move(3,2)
	elif destination == 'bedroom':
		move(10,2)
	elif destination == 'entrance':
		move(2,7)

def robot_ahead(steps, moveto):
	global rX
	global rY
	global encoderA
	global encoderB
	global encoderA_value
	global encoderB_value
	global encoderA_prev_error
	global encoderB_prev_error
	global encoderA_sum_error
	global encoderB_sum_error
	global SAMPLETIME
	
	enc = Encoders()
	enc.start()
	
	#direction ahead
	motorA.forward()
	motorB.forward()
	
	sleep(SAMPLETIME)
	
	if moveto == 'X':
		destination = rX + steps
		while rX != destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
	elif moveto == 'Y':
		destination = rY + steps
		while rY != destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
	
	enc.kill = True
	motorA.stop()
	motorB.stop()


def robot_left():		
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
	
	
def robot_right():		
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
		

def move(cx,cy):
	global dir
	global rX
	global rY
	
	matrix=maze.splitlines()
	matrix=[i.strip() for i in matrix]
	matrix=[i.split() for i in matrix]
	numrows, numcols = len(matrix), len(matrix[0])
		
	startx,starty=rX,rY
	
	destx,desty=cx,cy
	
	if (startx < 0) or (starty < 0):
		return
	
	# error position correction, max 2 steps of correction, should not be more
	if matrix[starty][startx] == "1":
		matrix[starty][startx] = "0"
	if matrix[starty][startx+1] == "1":
		matrix[starty][startx+1] = "0"
	if matrix[starty][startx-1] == "1":
		matrix[starty][startx-1] = "0"
	if matrix[starty+1][startx] == "1":
		matrix[starty+1][startx] = "0"
	if matrix[starty+1][startx+1] == "1":
		matrix[starty+1][startx+1] = "0"
	if matrix[starty+1][startx-1] == "1":
		matrix[starty+1][startx-1] = "0"
	if matrix[starty-1][startx] == "1":
		matrix[starty-1][startx] = "0"
	if matrix[starty-1][startx+1] == "1":
		matrix[starty-1][startx+1] = "0"
	if matrix[starty-1][startx-1] == "1":
		matrix[starty-1][startx-1] = "0"
	
	q=Queue()
	
	row,col=desty,destx
	
	q.put((row,col))
	while not q.empty():
		row, col = q.get()
		if col+1 < numcols and matrix[row][col+1] == "0":
			q.put((row, col+1))
			matrix[row][col+1] = "L"
		if row+1 < numrows and matrix[row+1][col] == "0":
			q.put((row+1, col))
			matrix[row+1][col] = "U"
		if 0 <= col-1 and matrix[row][col-1] == "0":
			q.put((row, col-1))
			matrix[row][col-1] = "R"
		if 0 <= row-1 and matrix[row-1][col] == "0":
			q.put((row-1, col))
			matrix[row-1][col] = "D"
	
	#show(matrix)
	
	row,col=starty,startx
	var=matrix[row][col]
	
	print 'start %s %s' % (startx,starty)
	print 'destination %s %s' % (destx,desty)
	print 'dir %s - var %s' % (dir,var)
	
	if var == "0":
		return
	elif var == '1' :
		print 'robot position not in the path'
		return

	while True:
		
		if row == desty and col == destx:
		    break
		
		if (dir == 'R' and var == 'U' ) or (dir == 'L' and var == 'D' ):
			print 'turn left, robot position (%s, %s)' % (startx, starty)
			dir = var
			robot_left()
		elif (dir == 'R' and var == 'D' ) or (dir == 'L' and var == 'U' ):
			print 'turn right, robot position (%s, %s)' % (startx, starty)
			dir = var
			robot_right()
		elif (dir == 'U' and var == 'R' ) or (dir == 'D' and var == 'L' ):
			print 'turn right, robot position (%s, %s)' % (startx, starty)
			dir = var
			robot_right()
		elif (dir == 'U' and var == 'L' ) or (dir == 'D' and var == 'R' ):
			print 'turn left, robot position (%s, %s)' % (startx, starty)
			dir = var
			robot_left()
		elif (dir == 'U' and var == 'D' ):
			print 'turn left, robot position (%s, %s)' % (startx, starty)
			dir = 'L'
			robot_left()
		elif (dir == 'R' and var == 'L' ):
			print 'turn right, robot position (%s, %s)' % (startx, starty)
			dir = 'D'
			robot_right()
		elif (dir == 'D' and var == 'U' ):
			print 'turn left, robot position (%s, %s)' % (startx, starty)
			dir = 'R'
			robot_left()
		elif (dir == 'L' and var == 'R' ):
			print 'turn right, robot position (%s, %s)' % (startx, starty)
			dir = 'U'
			robot_right()
		elif var == dir:
			steps = 0
			moveto = 'X'
			while var == dir:
				if row == desty and col == destx :
					break
				r, c = step[var]
				row += r
				col += c
				if r == 0:
					steps += c
					startx += c
				else:
					steps += r
					starty += r
					moveto = 'Y'
				var = matrix[row][col]
			if steps != 0:
				print 'move %s steps direction %s' % (steps, dir), 
				print '-> hypothetical position (%s, %s)' % (startx, starty)
				robot_ahead(steps, moveto)


if __name__ == '__main__':
	pos = Pos()
	pos.start()
	sl = Lights()
	sl.start()
	server = MyHTTPServer(('', 8000), RequestHandler)
	try:
		print('Starting server at port 8000')
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	pos.kill = True
	sl.kill = True
	server.server_close()
