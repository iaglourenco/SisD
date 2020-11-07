from multiprocessing import Process,Lock,Event
from threading import Thread
import socket
from socket import SOCK_STREAM
import sys


#The variables below are shared across the servers and need to sincronized with others servers
shr_variable = '' 


#Structure with all adresses of the servers
server_list = {}

#  server = {server1: (ip,port),server2:(ip,port),server3: (ip,port),server4: (ip,port)}





mutex = Lock()
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



def server_thread():
    #Communicate with other server for sincronization.
    #global shr_variable
    global event
    print('Thread do servidor rodando')


    while True:
        if event.is_set():
            #Send to all servers the new variable
            print("Entrou no evento")
            print(shr_variable)

            event.clear()


    return

def client_thread(ns):
    global shr_variable
    global event
    while True:
        bytes_received = ns.recv(5)
        command = bytes_received.decode()

        print('Command ->',command)
        if command == 'readd':
            send(ns,(shr_variable+chr(0)).encode())

        elif command == 'write':

            ret = receive(ns)
            if ret:
                shr_variable = ret
                print('Mensagem recebida',ret)
                event.set()
            else:
                print('Falha ao receber a mensagem')

        elif command == 'quit':
            return

server_t = Thread(target=server_thread)


def main(port):
    # Main execution
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',port))
    s.listen(5)
    print('Listening on',port)
    server_t.start()

    while True:
        try:
            ns,address = s.accept()
            print('Connection from',address)
            Thread(target=client_thread,args=(ns,)).start()
        except KeyboardInterrupt:
            exit()
    
if __name__ == '__main__':
    main(int(sys.argv[1]))

