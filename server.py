from multiprocessing import Process,Lock,Event
from threading import Thread
import socket
from socket import SOCK_STREAM
import sys


#The variables below are shared across the servers and need to sincronized with others servers
shr_variable = '' 


#Structure with all adresses of the servers
#  server = {counter:<amount of servers> ,server1: (ip,port),server2:(ip,port),server3: (ip,port),server4: (ip,port)}
server_list = {'counter':0}


def add_server(address):
    c = server_list.get('counter')
    server_list['server'+str(c)] = address
    server_list['counter']+=1




# mutex = Lock()
event = Event()

def send(s:socket,data):
    #Send data through socket
    s.sendall(data)

def receive(s: socket):
    #Returns the received data
    res=''
    while True:
        bytes_read = s.recv(1)
        if ord(bytes_read) == 0: 
            break
        if not bytes_read:
            return None
        
        res += bytes_read.decode()

    return res



def server_thread(port):
    #Communicate with other server for sincronization.
    #global shr_variable
    global event
    print('Server Thread running')


    #Register the current address to the server list
    address = (socket.gethostname(),port)
    add_server(address)
    

    while True:
        try:
            if event.is_set():                
                print("Echo server_thread-> \"{}\"".format(shr_variable))
                
                #Send to all servers the new variable


                event.clear()
        except KeyboardInterrupt:
            return


def client_thread(ns,address):
    global shr_variable
    global event

    print('Connection from',address)
    while True:
        bytes_received = ns.recv(5)
        command = bytes_received.decode()
        if not bytes_received:
            return

        print('Command ->',"\""+command+"\"",'from',address)
        if command == 'readd':
            try:
                send(ns,(shr_variable+chr(0)).encode())
            except IOError:
                print('Failed to send data to',address)

        elif command == 'write':

            ret = receive(ns)
            if ret:
                shr_variable = ret
                print('Received data',"\""+ret+"\"",'from',address)
                event.set()
            else:
                print('Failed to receive data from',address)

        elif command == 'quit':
            print('Connection closed',address)
            return


def main(port):
    # Main execution
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',port))
    s.listen(5)
    print('Listening on',port)
    Thread(target=server_thread,args=(port,)).start()


    while True:
            ns,address = s.accept()
            Thread(target=client_thread,args=(ns,address,)).start()
        
    
if __name__ == '__main__':
    try:
        main(int(sys.argv[1]))
    except KeyboardInterrupt:
        exit()
