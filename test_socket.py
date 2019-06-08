import socket

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the port 8000
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
