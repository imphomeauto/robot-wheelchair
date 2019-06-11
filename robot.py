from __future__ import absolute_import
from Queue import Queue
from SunFounder_TB6612 import TB6612
import RPi.GPIO as GPIO
import socket
import threading
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
turnLeftEnc = 359
turnRightEnc = 359
encoderA_value = 0
encoderB_value = 0
encoderA_prev_error = 0
encoderB_prev_error = 0
encoderA_sum_error = 0
encoderB_sum_error = 0
SAMPLETIME = 0.05
TARGET = 18
stop_thread_run = True
################### INS VARIABLES ###################
maze='''\
1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 1 0 0 0 0 0 0 1 1 1 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1
'''

matrix=maze.splitlines()
matrix=[i.strip() for i in matrix]
matrix=[i.split() for i in matrix]
numrows, numcols = len(matrix), len(matrix[0])

step = {'U': (-1, 0), 'D': (1, 0), 'R': (0, 1), 'L': (0, -1)}

################### IPS VARIABLES ###################

rX = -1
rY = -1
dir = 'R'
room = 'entrance'

################### IPS THREAD ###################

class Pos(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('position started thread')
				
	def run(self):
		global rX
		global rY
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('ips.local', 8000)
		sock.connect(server_address)
		message = 'pos';
		
		while True:
			sock.sendall(message)
			data = sock.recv(5)
			if data:
				arr = data.split(',')
				rX = int(arr[0])
				rY = int(arr[1])
				#print 'X "%s", Y "%s"' % (rX, rY)

class Encoders(threading.Thread):	
	def __init__(self):
		threading.Thread.__init__(self)
		print('encoders thread started')
		
	def run(self):
		global encoderA
		global encoderB
		global encoderA_value
		global encoderB_value
		global stop_thread_run

		stop_thread_run = False

		while True:
			encoderA_read = GPIO.input(20)
			encoderB_read = GPIO.input(5)
		
			if encoderA_read != encoderA:
				encoderA = encoderA_read
				encoderA_value += 1
		
			if encoderB_read != encoderB:
				encoderB = encoderB_read
				encoderB_value += 1
			
			if stop_thread_run:
				break

class MyHTTPServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		HTTPServer.__init__(self, *args, **kwargs)

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.send_header('Access-Control-Allow-Origin','*')
		self.end_headers()
		output = '<p>X: %s</p><p>Y: %s</p><p>dir: %s</p><p>room: %s</p>' % (rX, rY, dir, room)
		if self.path.startswith( '/a', 0, 2 ) :
			robot_ahead(int(self.path[2:]))
		elif self.path == '/l' :
			robot_left()
		elif self.path == '/r' :
			robot_right()
		elif self.path.startswith( '/n', 0, 2 ) :
			navigate(str(self.path[2:]))
		self.wfile.write(output)

def navigate(destination):
	global room
	if destination == 'kitchen' and room == 'entrance':
		move(10,7)
		room == 'kitchen'
	elif destination == 'kitchen' and room == 'toilet':
		move(4,4)
		move(10,7)
		room == 'kitchen'
	elif destination == 'kitchen' and room == 'bedroom':
		move(8,4)
		move(10,7)
		room == 'kitchen'
	elif destination == 'toilet' and room == 'entrance':
		move(4,4)
		move(3,2)
		room == 'toilet'
	elif destination == 'toilet' and room == 'bedroom':
		move(8,5)
		move(4,4)
		move(3,2)
		room == 'toilet'
	elif destination == 'toilet' and room == 'kitchen':
		move(4,4)
		move(3,2)
		room == 'toilet'
	elif destination == 'bedroom' and room == 'entrance':
		move(8,4)
		move(10,2)
		room == 'bedroom'
	elif destination == 'bedroom' and room == 'toilet':
		move(4,5)
		move(4,4)
		move(10,2)
		room == 'bedroom'
	elif destination == 'bedroom' and room == 'kitchen':
		move(8,4)
		move(10,2)
		room == 'bedroom'
	elif destination == 'entrance' and room == 'toilet':
		move(4,4)
		move(2,7)
		room == 'entrance'
	elif destination == 'entrance' and room == 'kitchen':
		move(2,7)
		room == 'entrance'
	elif destination == 'entrance' and room == 'bedroom':
		move(8,4)
		move(2,7)
		room == 'entrance'


def robot_ahead(steps, dir):
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
	global stop_thread_run
	
	enc = Encoders()
	enc.start()
	
	#direction ahead
	motorA.forward()
	motorB.forward()
	
	sleep(SAMPLETIME)
	
	if dir == 'R':
		destination = rX + steps
		while rX > destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
	elif dir == 'L':
		destination = rX + steps
		while rX < destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
	elif dir == 'U':
		destination = rY + steps
		while rY > destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
	elif dir == 'D':
		destination = rY + steps
		while rY < destination:
			new_motorA_speed = motorA.speed + (TARGET - encoderA_value)
			new_motorB_speed = motorB.speed + (TARGET - encoderB_value)
			motorA.speed = int(abs(new_motorA_speed))
			motorB.speed = int(abs(new_motorB_speed))
			encoderA_value = 0
			encoderB_value = 0
			sleep(SAMPLETIME)
			
	stop_thread_run = True
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
		
	startx,starty=rX,rY
	
	destx,desty=cx,cy
	
	if (startx < 0) or (starty < 0) or (desty < 0) or (destx < 0):
		return
	
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
	
	row,col=starty,startx
	var=matrix[row][col]
	
	print 'start %s %s' % (startx,starty)
	print 'destination %s %s' % (destx,desty)
	print 'dir %s - var %s' % (dir,var)
	
	if var == "0":
		return
	
	while True:
		if row == desty and col == destx:
			break
		
		if (dir == 'R' and var == 'U' ) or (dir == 'L' and var == 'D' ):
			print 'turn left'
			dir = var
			robot_left()
			continue
		elif (dir == 'R' and var == 'D' ) or (dir == 'L' and var == 'U' ):
			print 'turn right'
			robot_right()
			dir = var
			continue
		elif (dir == 'U' and var == 'R' ) or (dir == 'D' and var == 'L' ):
			print 'turn right'
			robot_right()
			dir = var
			continue
		elif (dir == 'U' and var == 'L' ) or (dir == 'D' and var == 'R' ):
			print 'turn left'
			robot_left()
			dir = var
			continue
		elif (dir == 'U' and var == 'D' ):
			print 'turn left'
			robot_left()
			dir = 'L'
			continue
		elif (dir == 'R' and var == 'L' ):
			print 'turn right'
			robot_right()
			dir = 'D'
			continue
		elif (dir == 'D' and var == 'U' ):
			print 'turn left'
			robot_left()
			dir = 'R'
			continue
		elif (dir == 'L' and var == 'R' ):
			print 'turn right'
			robot_right()
			dir = 'U'
			continue
		
		steps = 0 
		
		while var == dir:
			var = matrix[row][col]
			if var != dir:
				continue
			r, c = step[var]
			row += r
			col += c
			if r == 0:
				steps += c
			else:
				steps += r
		
		if steps != 0:
			print 'move %s steps (direction %s)' % (steps, dir)
			robot_ahead(steps, dir)
			continue


if __name__ == '__main__':
	pos = Pos()
	pos.start()
	server = MyHTTPServer(('', 8000), RequestHandler)
	print('Starting server at port 8000')
	server.serve_forever()
