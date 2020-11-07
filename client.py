import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost',int(sys.argv[1])))



s.sendall('readd'.encode())

res=''
while True:
    bytes_read = s.recv(1)
    if ord(bytes_read) == 0: 
        break
    res += bytes_read.decode()

print(res)

exit()

while True:
    try:
        data = input()

        s.sendall( (data + chr(0)).encode() ) 


    except KeyboardInterrupt:
        break


# s.send('readd'.encode())






