from __future__ import absolute_import
from Queue import Queue

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

def show(matrix):
    for line in matrix:
        print line
    print

matrix=maze.splitlines()
matrix=[i.strip() for i in matrix]
matrix=[i.split() for i in matrix]
numrows, numcols = len(matrix), len(matrix[0])

print 'MAP LEGEND\n0: clear space\n1: wall/obstacle\n'

#show(matrix)

q=Queue()

startx,starty=12,1
destx,desty=4,2 # toilet
#destx,desty=10,2 # bedroom
#destx,desty=10,7 # kitchen
#destx,desty=2,7 # entrace
dir = 'U'

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

show(matrix)

if var == '0' :
    exit()
elif var == '1' :
	print 'robot position not in the path'
	exit()

# Trace the path
step = {'U': (-1, 0), 'D': (1, 0), 'R': (0, 1), 'L': (0, -1)}

print 'robot position (%s, %s)' % (startx, starty)
print 'robot direction %s \n' % dir
print 'destination (%s, %s) \n' % (destx, desty)

while True:
	
	if row == desty and col == destx:
	    break
	
	if (dir == 'R' and var == 'U' ) or (dir == 'L' and var == 'D' ):
		print 'turn left, robot position (%s, %s)' % (startx, starty)
		dir = var
	elif (dir == 'R' and var == 'D' ) or (dir == 'L' and var == 'U' ):
		print 'turn right, robot position (%s, %s)' % (startx, starty)
		dir = var
	elif (dir == 'U' and var == 'R' ) or (dir == 'D' and var == 'L' ):
		print 'turn right, robot position (%s, %s)' % (startx, starty)
		dir = var
	elif (dir == 'U' and var == 'L' ) or (dir == 'D' and var == 'R' ):
		print 'turn left, robot position (%s, %s)' % (startx, starty)
		dir = var
	elif (dir == 'U' and var == 'D' ):
		print 'turn left, robot position (%s, %s)' % (startx, starty)
		dir = 'L'
	elif (dir == 'R' and var == 'L' ):
		print 'turn right, robot position (%s, %s)' % (startx, starty)
		dir = 'D'
	elif (dir == 'D' and var == 'U' ):
		print 'turn left, robot position (%s, %s)' % (startx, starty)
		dir = 'R'
	elif (dir == 'L' and var == 'R' ):
		print 'turn right, robot position (%s, %s)' % (startx, starty)
		dir = 'U'
	elif var == dir:
		movement = 0 
		while var == dir:
			if row == desty and col == destx :
				break
			r, c = step[var]
			row += r
			col += c
			if r == 0:
				movement += c
				startx += c
			else:
				movement += r
				starty += r
			var = matrix[row][col]
		if movement != 0:
			print 'move %s steps direction %s' % (movement, dir), 
			print '-> robot position (%s, %s)' % (startx, starty)

print
print 'finish (%s, %s)' % (row, col)	
