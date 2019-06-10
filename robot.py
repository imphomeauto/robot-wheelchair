from __future__ import absolute_import
from Queue import Queue
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
turnLeftEnc = 347
turnRightEnc = 347

# INS VARIABLES
maze='''\
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1
1 1 1 1 1 1 1 0 0 1 1 1 1 1 0 0 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 0 0 1 1 1 1 1 0 0 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 0 0 1 1 1 1 1 0 0 1 1 1 1 1 1 1 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
'''

matrix=maze.splitlines()
matrix=[i.strip() for i in matrix]
matrix=[i.split() for i in matrix]
numrows, numcols = len(matrix), len(matrix[0])

step = {'U': (-1, 0), 'D': (1, 0), 'R': (0, 1), 'L': (0, -1)}

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
			data = sock.recv(5)
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
		elif self.path.startswith( '/n', 0, 2 ) :
			navigate(str(self.path[2:]))
		self.wfile.write(output)


def robot_ahead(destination, direction):
	global rX
	global rY
	
	#direction ahead
	motorA.forward()
	motorB.forward()
	
	if direction == 'R' :
		while rX < destination:
			print 'x: %s - dest %s' % (rX, destination)
			motorA.speed = 22
			motorB.speed = 20
	elif direction == 'L' :
		while rX > destination:
			print 'x: %s - dest %s' % (rX, destination)
			motorA.speed = 22
			motorB.speed = 20
	elif direction == 'D' :
		while rY < destination:
			print 'y: %s - dest %s' % (rY, destination)
			motorA.speed = 22
			motorB.speed = 20
	elif direction == 'U' :
		while rY > destination:
			print 'y: %s - dest %s' % (rY, destination)
			motorA.speed = 22
			motorB.speed = 20
	
	motorA.stop()
	motorB.stop()

	
def robot_left():	
	global dir
	
	print 'turn left'
	
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
	global dir
	
	print 'turn right'
	
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
		

def navigate(destination):
	global dir
	global rX
	global rY
		
	startx,starty=rX,rY
	
	destx,desty=-1,-1
	
	if destination == 'kitchen':
		destx,desty=20,15
	elif destination == 'toilet':
		destx,desty=5,5
	elif destination == 'bedroom':
		destx,desty=20,5
	elif destination == 'entrance':
		destx,desty=4,13
		
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
	
	if var == "0":
		# already at destination
		return
	
	while True:
		if row == desty and col == destx:
			break
		
		if (dir == 'R' and var == 'U' ) or (dir == 'L' and var == 'D' ):
			robot_left()
			dir = var
			continue
		elif (dir == 'R' and var == 'D' ) or (dir == 'L' and var == 'U' ):
			robot_right()
			dir = var
			continue
		elif (dir == 'U' and var == 'R' ) or (dir == 'D' and var == 'L' ):
			robot_right()
			dir = var
			continue
		elif (dir == 'U' and var == 'L' ) or (dir == 'D' and var == 'R' ):
			robot_left()
			dir = var
			continue
		elif (dir == 'U' and var == 'D' ):
			robot_left()
			dir = 'L'
			continue
		elif (dir == 'R' and var == 'L' ):
			robot_right()
			dir = 'D'
			continue
		elif (dir == 'D' and var == 'U' ):
			robot_left()
			dir = 'R'
			continue
		elif (dir == 'L' and var == 'R' ):
			robot_right()
			dir = 'U'
			continue
		
		axetomove = '-'
		
		while var == dir:
			r, c = step[var]
			row += r
			col += c
			var = matrix[row][col]
			if r == 0:
				axetomove = 'x'
			else:
				axetomove = 'y'
		
		if axetomove == 'x':
			print 'moving to %s (axe x)' % col
			robot_ahead(col, dir)
			continue
		elif axetomove == 'y':
			print 'moving to %s (axe y)' % row
			robot_ahead(row, dir)
			continue
	

if __name__ == '__main__':
	server = MyHTTPServer(('', 8000), RequestHandler)
	print('Starting server at port 8000')
	server.serve_forever()
