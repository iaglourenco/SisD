import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost',int(sys.argv[1])))




def receive(s: socket):
    s.sendall('readd'.encode())
    

    res=''
    while True:
        bytes_read = s.recv(1)
        if ord(bytes_read) == 0: 
            break
        res += bytes_read.decode()
    return res


while True:
    try:
        print("1 - Write new data\n2 - Read current data\n3 - Close connection\n>",end='\0')
        option = input()

        if option == '1':
            s.sendall('write'.encode())
            print('Data>',end='\0')
            data = input()
            s.sendall( (data + chr(0) ).encode() ) 

        elif option == '2':
            ret = receive(s)
            print("Message received:",ret)
        
        elif option == '3':
            s.sendall('quit'.encode())
            s.close()
            raise KeyboardInterrupt
        else:
            print("Invalid option")



    except KeyboardInterrupt:
        print("Finished")
        break








