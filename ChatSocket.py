import socket
import GlobalVars

class ChatSocket:
    def __init__(self):
        self.host_ip = ""
        self.host_port = ""


    def establish_tcp_socket(self, screenname):
        """
        Establishes a TCP socket to the Membership Server to talk to it.
        IMPORTANT: You MUST close the socket using shutdown_socket when you are finished with your call.
        :return: None
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GlobalVars.CHAT_SOCKET_LISTENER.hosts[screenname][0], GlobalVars.CHAT_SOCKET_LISTENER.hosts[screenname][0]))
        return s

    def shutdown_tcp_socket(self):
        """
        Closes the currently open socket, and removes it so that we know that the socket is closed.
        :return: None
        """
        self.open_socket.close()
        self.open_socket = None

    def send_msg_over_tcp(self, msg: str, socket):
        """
        Send a message to the Membership server. This will use the currently open socket.
        :param msg: a string representing the message you would like to send to the Membership server.
        :return: None
        """
        totalsent = 0
        msg = bytes(msg, 'utf-8')
        # According to https://docs.python.org/3/howto/sockets.html, it is best practice to
        # continue sending until the message is completely set, as this does not always happen.
        while totalsent < len(msg):
            sent = socket.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def recv_msg_over_tcp(self):
        """
        Recieve a message from the Membership, and return it.
        :return: Membership server's response, casted from bytes to string.
        """
        chunks = []
        # According to https://docs.python.org/3/howto/sockets.html, it is best practice
        # to keep receiving until your condition is met, which is a newline in our case.
        while True:
            chunk = self.open_socket.recv(2048)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            if b"\n" in chunk:
                break

        return str(b''.join(chunks), 'utf-8')

    def send_msg_over_udp(self, message, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message, "utf-8"), (host, int(port)))
