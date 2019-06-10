from __future__ import absolute_import
from Queue import Queue

maze='''\
0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0
1 1 1 1 1 0 0 1 0 0 1 1 1 1 1 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
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

show(matrix)

q=Queue()

startx,starty=1,7
#destx,desty=3,2 # toilet
#destx,desty=12,2 # bedroom
destx,desty=13,6 # kitchen
#destx,desty=1,7 # entrace

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

#show(matrix)

if var=="0":
    exit()

# Trace the path
step = {'U': (-1, 0), 'D': (1, 0), 'R': (0, 1), 'L': (0, -1)}

dir = 'L'

print 'robot position (%s, %s)' % (startx, starty)
print 'robot direction %s \n' % dir
print 'destination (%s, %s) \n' % (destx, desty)

while True:
	
	if row == desty and col == destx:
	    break
	
	if (dir == 'R' and var == 'U' ) or (dir == 'L' and var == 'D' ):
		print 'turn left'
		dir = var
		continue
	elif (dir == 'R' and var == 'D' ) or (dir == 'L' and var == 'U' ):
		print 'turn right'
		dir = var
		continue
	elif (dir == 'U' and var == 'R' ) or (dir == 'D' and var == 'L' ):
		print 'turn right'
		dir = var
		continue
	elif (dir == 'U' and var == 'L' ) or (dir == 'D' and var == 'R' ):
		print 'turn left'
		dir = var
		continue
	elif (dir == 'U' and var == 'D' ):
		print 'turn left'
		dir = 'L'
		continue
	elif (dir == 'R' and var == 'L' ):
		print 'turn right'
		dir = 'D'
		continue
	elif (dir == 'D' and var == 'U' ):
		print 'turn left'
		dir = 'R'
		continue
	elif (dir == 'L' and var == 'R' ):
		print 'turn right'
		dir = 'U'
		continue
		
	movement = 0 
	
	while var == dir:
		r, c = step[var]
		row += r
		col += c
		var = matrix[row][col]
		if r == 0:
			movement += c
		else:
			movement += r
	
	if movement != 0:
		print 'move %s steps (direction %s)' % (movement, dir) 
		continue

print
print 'finish (%s, %s)' % (row, col)	

