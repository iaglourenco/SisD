# Nome: Iago Jardim Lourenço  RA:15610116
# Nome:Lucas Rodrigues Coutinho  RA:17776501
# Opcionais funcionando: 1,3,4
# Observações: O opcional 4 está funcionando em partes, pois as copias temporarias não são excluidas
# Valor do Projeto: 7 pontos


import argparse
import json
import socket
import time
from multiprocessing import Event
from threading import Thread

# The variable below are shared across the servers and need to sincronized with others servers
shr_variable = " "


# Structure with all adresses of the servers
#  server = {counter:<amount of servers> ,server1: (ip,port),server2:(ip,port),server3: (ip,port),server4: (ip,port)}
server_list = {"counter": 0}

# dns variables
server_index = 0
user_count = 0
time_count = time.time()
temp_servers = []
kill_yourself = False


def add_server(address):
    c = server_list.get("counter")
    server_list["server" + str(c)] = address
    server_list["counter"] += 1


def send(s: socket, data):
    # Send data through socket
    s.sendall(data)


def receive(s: socket):
    # Returns the received data
    res = ""
    while True:
        bytes_read = s.recv(1)
        if ord(bytes_read) == 0:
            break
        if not bytes_read:
            return None

        res += bytes_read.decode()

    return res


def server_thread(ns, address):
    # Communicate with other server for sincronization.
    global server_list
    global shr_variable
    print("Server Thread running")

    bytes_read = ns.recv(5)
    command = bytes_read.decode()

    if command == "msgns":
        shr_variable = receive(ns)
    elif command == "lista":
        server_list_cod = ns.recv(1024)
        server_list = json.loads(server_list_cod.decode())
        print(server_list)

    return


def client_thread(ns, address):
    global shr_variable
    global event

    print("Connection from", address)
    while True:
        bytes_received = ns.recv(5)
        command = bytes_received.decode()
        if not bytes_received:
            return

        print("Command ->", '"' + command + '"', "from", address)
        if command == "readd":
            try:
                send(ns, (shr_variable + chr(0)).encode())
            except IOError:
                print("Failed to send data to", address)

        elif command == "write":

            ret = receive(ns)
            if ret:
                shr_variable = ret
                print("Received data", '"' + ret + '"', "from", address)
                dns_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                dns_s.connect((server_list.get("dns")[0], server_list.get("dns")[1]))
                dns_s.sendall("propa".encode())
                buf_d = shr_variable + chr(0)
                dns_s.sendall(buf_d.encode())
                dns_s.sendall("close".encode())
                dns_s.sendall(("0000" + chr(0)).encode())
                dns_s.close()

            else:
                print("Failed to receive data from", address)

        elif command == "quit":
            print("Connection closed", address)
            return


def main(s, port):
    # Main execution
    print("Now i'm running on", port)
    global kill_yourself

    while True:

        if __name__.startswith("Temp"):
            if kill_yourself:
                print("R.I.P - Life of", __name__, "was too short :(")
                break

        ns, address = s.accept()

        rcb = ns.recv(6)
        identity = rcb.decode()

        if identity == "dnsack":  # DNS Connection
            Thread(
                target=server_thread,
                args=(
                    ns,
                    address,
                ),
            ).start()
        elif identity == "cliack":  # Client Connection
            Thread(
                target=client_thread,
                args=(
                    ns,
                    address,
                ),
            ).start()


def dns_thread(ns: socket, address):

    global shr_variable
    global server_index
    global user_count
    global time_count
    global temp_servers
    global kill_yourself

    while True:

        bytes_read = ns.recv(5)
        command = bytes_read.decode()

        if command == "inser":
            bytes_r = ns.recv(5)
            port = bytes_r.decode()

            add_server((address[0], int(port)))
            buf_lst = json.dumps(server_list)

            for serverN in range(0, server_list.get("counter")):
                try:
                    s_ip, s_port = server_list.get("server{}".format(serverN))
                    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("[INSER] Connecting to ", s_ip, s_port)
                    cs.connect((s_ip, s_port))

                    cs.sendall("dnsack".encode())
                    cs.sendall("lista".encode())
                    cs.sendall(buf_lst.encode())
                    cs.close()
                except socket.error as e:
                    print("Failed to send lista to", (s_ip, s_port), e)

        if command == "propa" or command == "inser":

            if command == "propa":
                rec = receive(ns)
                shr_variable = rec
                buf_msg = rec + chr(0)
            elif command == "inser":
                buf_msg = shr_variable + chr(0)

            for serverN in range(0, server_list.get("counter")):
                try:
                    s_ip, s_port = server_list.get("server{}".format(serverN))
                    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("[PROPA] Connecting to ", s_ip, s_port)
                    cs.connect((s_ip, s_port))

                    cs.sendall("dnsack".encode())
                    cs.sendall("msgns".encode())
                    cs.sendall(buf_msg.encode())
                    cs.close()
                except socket.error as e:
                    print("Failed to send data to", (s_ip, s_port), e)

        elif command == "getsr":
            user_count += 1

            if time.time() - time_count > 60:
                user_count = 0
                time_count = time.time()

            print("DEBUG", time.time() - time_count)
            print("USER_CONT", user_count)

            if time.time() - time_count < 60:
                if user_count < 2:
                    kill_yourself = False

                else:

                    kill_yourself = False
                    tmp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    print("[TEMPORARY] Creating a temporary server")
                    tmp_s.bind(("", 0))
                    tmp_port = tmp_s.getsockname()[1]
                    tmp_s.listen(5)
                    Thread(
                        target=main,
                        args=(
                            tmp_s,
                            tmp_port,
                        ),
                    ).start()
                    temp_servers.append(tmp_port)

                    tmp_dns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tmp_addr = (server_list.get("dns")[0], server_list.get("dns")[1])
                    tmp_dns_socket.connect(tmp_addr)
                    tmp_dns_socket.sendall("inser".encode())
                    tmp_dns_socket.sendall(str(tmp_port).encode())
                    tmp_dns_socket.sendall("close".encode())
                    tmp_dns_socket.close()

            if server_index < server_list.get("counter"):
                server_index += 1
            else:
                server_index = 1

            l_ip, l_port = server_list.get("server" + str(server_index - 1))

            print("[GETSR] Fowarding to server", server_index, "on", l_ip, l_port)
            add = {"ip": l_ip, "port": l_port}
            buf_l = json.dumps(add)
            ns.sendall(buf_l.encode())

        elif command == "close":
            return


def dns(port):
    print("DNS Running")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(("", port))
    s.listen(5)
    print("Listening on", get_ip() + ":" + str(port))
    server_list["dns"] = (get_ip(), port)

    while True:
        ns, address = s.accept()
        print("DNS Query connection from", address)
        Thread(target=dns_thread, args=(ns, address)).start()


def get_ip():
    try:
        ts = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ts.connect(("localhost", 1))
        ip = ts.getsockname()[0]
        ts.close()
        return ip
    except socket.error:
        print("Failed to retrieve ip")
        raise socket.error
        exit()


def yes_or_no(question):
    reply = str(input(question + " (y/n): ")).lower().strip()
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dns",
        help="create a new dns server, on the port informed",
        required=False,
        action="store_true",
    )
    ap.add_argument(
        "-p",
        "--port",
        help="the port to execute the script on",
        required=True,
        type=int,
    )
    args = vars(ap.parse_args())

    if args["dns"]:
        if len(str(args.get("port"))) != 5:
            print("Invalid port size, port is 5 digits")
            exit(-1)
        dns(args.get("port"))

    socket_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    socket_main.bind(("", args.get("port")))
    socket_main.listen(5)

    while True:
        print("What is the address of the DNS? <ip:port>")
        dns_input = input()
        dns_ip, dns_port = dns_input.split(":")
        if len(str(dns_port)) != 5:
            print("Invalid DNS port size, port is 5 digits")
            exit(-1)
        try:
            dns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dns_socket.connect((dns_ip, int(dns_port)))

            dns_socket.sendall("inser".encode())
            dns_socket.sendall(str(args.get("port")).encode())
            dns_socket.sendall("close".encode())
            dns_socket.sendall(("0000" + chr(0)).encode())

            dns_socket.close()
            break
        except KeyboardInterrupt as e:
            print("Could not connect to DNS server", e)
            promo = yes_or_no("Do you want to promote this execution to a DNS server?")
            if promo:
                dns(args.get("port"))
            else:
                print("Ok, can't continue without that")
                exit()

    main(socket_main, args.get("port"))
