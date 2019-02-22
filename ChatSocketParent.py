import threading
import socket
import GlobalVars as GlobalVars
from datetime import datetime
import socketserver
from ChatSocketTcpListener import ChatSocketTcpListener
import time
import socket
import threading

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class ChatSocketParent:
    """
    This will be the servant thread, and will listen for any messages coming in from other users
    and the Membership Server.
    """
    def __init__(self, local_ip="127.0.0.1", listener_port="7575"):
        GlobalVars.CHAT_SOCKET_PARENT = self
        self.local_ip = local_ip
        self.listener_port = listener_port
        self.hosts = {}
        self.open_socket = None

        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ")" + " ATTEMPTING CONNECTION TO " +
                                    self.local_ip + " " + str(self.listener_port))

        server = ThreadedTCPServer(('', self.listener_port), ChatSocketTcpListener)
        server.serve_forever()
        return

    def send_msg_over_udp(self, message, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message, "utf-8"), (host, int(port)))

    def get_host_by_client_address(self, client_address):
        for host in self.hosts:
            if client_address == self.hosts[host][2]:
                return host

    def send_join_to_room(self, screenname):
        msg = "JOIN " + screenname + " " + self.hosts[screenname][0] + " " + str(self.hosts[screenname][1]) + "\n"
        for host in GlobalVars.CHAT_SOCKET_PARENT.hosts:
            self.send_msg_over_udp(msg, self.hosts[host][0], self.hosts[host][1])
            GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") SENT USER JOIN TO " + screenname)

