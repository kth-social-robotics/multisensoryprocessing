""" This is the Hololens experiment Server that connects the hololens with all the other parts of
    the system.
"""

import socket
import select
import traceback
import platform
from subprocess import check_output
from datetime import datetime
import re

class Server:
    """ A simple TCP server.
    """
    def __init__(self):
        # Set log behaviour
        self.do_print = True
        self.do_log = True
        self.log_file = "log_txt.txt"

        # List to keep track of socket descriptors
        self.connection_dict = {}
        self.new_connections = []
        self.recv_buffer = 4096 # Advisable to keep it as an exponent of 2
        self.port = 5000

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # In order to get the correct (local) ip we need to detect which platform we are running on
        server_address = self.get_local_ip(platform.system())
        server_address = (server_address, self.port)
        self.server_socket.bind(server_address)
        self.server_socket.listen(10)

        # Add server socket to the list of readable connections
        self.connection_dict["server"] = self.server_socket
        self.log("Server started\t addr:\t{}\tport:{} ".format(self.server_socket.getsockname()[0],\
                                                               self.server_socket.getsockname()[1]))
    def run(self):
        """ The main loop of the server.
        """
        while True:
            # Get the list sockets which are ready to be read through select
            all_connections = list(self.connection_dict.values()) + self.new_connections
            read_sockets, _, _ = select.select(all_connections, [], [])

            for sock in read_sockets:
                #New connection
                if sock == self.server_socket:
                    # Handle the case in which there is a new connection recieved through
                    # server_socket
                    sockfd, addr = self.server_socket.accept()
                    self.new_connections.append(sockfd)
                    self.log("Client (%s, %s) connected" % addr)

                #Some incoming message from a client
                else:
                    # Data recieved from client, process it
                    try:
                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(self.recv_buffer)
                        print(data.decode("utf-8"))
                        if data:
                            self.parse(sock, data)
                    except:
                        self.log("Client (%s, %s) is offline" % addr)
                        traceback.print_exc()
                        sock.close()
                        self.remove_socket(sock)
                        continue

        self.server_socket.close()

    def remove_socket(self, socket_rem):
        """ Remove a socket from the dictionary of sockets if they appear to be broken.
        """
        clients_to_pop = []
        # Iterate through the dictionary to find the client to pop. Can't pop the clien during the
        # iteration because the dictionary size will change and you will get the error:
        # RuntimeError: dictionary changed size during iteration
        # Instead save the clients to pop in the clients_to_pop list.
        for client, sock in self.connection_dict.items():
            if sock == socket_rem:
                clients_to_pop.append(client)

        # Now iterate through the clients_to_pop list and remove the clients from the dictionary.
        if len(clients_to_pop) > 0:
            for client in clients_to_pop:
                self.connection_dict.pop(client, None)
                self.log("Client: {} ".format(client) + "has been removed from the connection" \
                         + "list, due to a broken socket.")

    def parse(self, sock, data):
        """ Split the data at figure out whether this is a new client presenting itself or a
            message that should be sent to a specific clien.
        """
        data = data.decode("utf-8")
        tmp = ""
        # Clean up if the client sent faulty chars
        for char in data:
            if not ord(char) < 32 or ord(char) > 126:
                tmp += char
        data = tmp
        data = data.split(";")
        if data[0] == "close me":
            self.remove_socket(sock)

        if data[0] == "client_type":
            self.log("A new client, '{}', has joined with addr {}".format(data[1], \
                     sock.getpeername()))
            # New client
            for new_socket in self.new_connections:
                if new_socket == sock:
                    self.connection_dict[data[1]] = new_socket
                    self.new_connections.remove(new_socket)
                    return
            self.log("Warning! The new client: {} was not found in".format(data[1]) \
                     + " the list of connections")
        else:
            # A message that should be forwarded
            for client, recipient_socket in self.connection_dict.items():
                if client == data[0]:
                    self.send(recipient_socket, data[1])

    def send(self, recipient_socket, message):
        """ The send command handles the forwarding of messages to different clients of the system.
        """
        try:
            recipient_socket.send(message.encode('utf-8'))
            for client, sock in self.connection_dict.items():
                if sock == recipient_socket:
                    self.log("A message '{}' has been sent to client '{}'".format(message, client))
        except:
            # Broken socket connection may be, chat client pressed ctrl+c for example
            recipient_socket.close()
            self.remove_socket(recipient_socket)

    def get_local_ip(self, system):
        """ The socket.gethostbyname(socket.gethostname()) - method does, apparently, not work on
            the raspberry pi. The call only returns the "localhost" address so we need some extra
            work to be able to detect the ip.
        """
        if system == "Linux":
            # This is a bit ugly but it works
            ips = check_output(['hostname', '--all-ip-addresses']).decode("utf-8")
            return ips.split(" ")[0]
        else:
            #return socket.gethostbyname(socket.gethostname())
            return socket.gethostbyname('130.229.140.0')

    def log(self, message):
        """ Add a time stamp and write the message to the log file.
        """
        time = datetime.now()
        time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}\t".format(time.year, time.month,\
                                                                          time.day, time.hour, \
                                                                          time.minute, time.second)
        message = "{}\t{}".format(time_stamp, message)
        if self.do_print:
            print(message)
        if self.do_log:
            with open(self.log_file, "a") as log_file:
                log_file.write(message + "\n")

if __name__ == "__main__":
    SERVER = Server()
    SERVER.run()
