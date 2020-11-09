# Nome: Iago Jardim Lourenço  RA:15610116
# Nome:Lucas Rodrigues Coutinho  RA:17776501
# Opcionais funcionando: 1,3,4
# Observações: O opcional 4 está funcionando em partes, pois as copias temporarias não são excluidas
# Valor do Projeto: 7 pontos


import socket
import json

def receive(s: socket):
    s.sendall('readd'.encode())
    
    res=''
    while True:
        bytes_read = s.recv(1)
        if ord(bytes_read) == 0: 
            break
        res += bytes_read.decode()
    return res


print("What is the address of the DNS? <ip:port>")
dns_input = input()
dns_ip,dns_port = dns_input.split(':')
try:
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dns_socket.connect((dns_ip, int(dns_port)))
    dns_socket.sendall('getsr'.encode())
    add = dns_socket.recv(1024)
    d = json.loads(add)
    server_ip = d.get('ip')
    server_port = d.get('port')
    dns_socket.sendall('close'.encode())
    dns_socket.sendall(('0000'+chr(0)).encode())
    dns_socket.close()
except socket.error:
    while True:
        try:
            print('Houston, we have a problem...')
            print('This DNS server does not respond, type another address or Ctrl+C to finish.')
            dns_input = input()
            dns_ip,dns_port = dns_input.split(':')
            dns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dns_socket.connect((dns_ip, int(dns_port)))
            dns_socket.sendall('getsr'.encode())
            add = dns_socket.recv(1024)
            d = json.loads(add)
            server_ip = d.get('ip')
            server_port = d.get('port')
            dns_socket.sendall('close'.encode())
            dns_socket.sendall(('0000'+chr(0)).encode())
            dns_socket.close()
            break
        except socket.error:
            pass
        except KeyboardInterrupt:
            exit()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((server_ip,server_port))
print('Connected to ' + server_ip + ':' + str(server_port))
s.sendall('cliack'.encode())

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








