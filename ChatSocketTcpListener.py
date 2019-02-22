import socketserver
import GlobalVars
from datetime import datetime
from socket import SHUT_RDWR

class ChatSocketTcpListener(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while 1:
                msg = self.recv_msg_over_tcp(self.request)
                if isinstance(msg, bytes):
                    msg = msg.decode("utf-8")

                if msg[:4] == "HELO":
                    msg = str(msg[5:-1]).split(" ")
                    if msg[0] in GlobalVars.CHAT_SOCKET_PARENT.hosts:
                        self.reject_user(msg[0])
                        self.request.close()
                        break
                    else:
                        GlobalVars.CHAT_SOCKET_PARENT.hosts[msg[0]] = (msg[1], int(msg[2]), self.client_address, self.request)
                        self.send_acpt_message(msg[0])
                        GlobalVars.CHAT_SOCKET_PARENT.send_join_to_room(msg[0])
                elif msg[:4] == "EXIT":
                    self.user_exited_room()
                    self.request.close()
                    break
        except BaseException as e:
            GlobalVars.LOGGER.exception(str(e))
            # self.request.close()

    def reject_user(self, screenname):
        self.send_msg_over_tcp("RJCT " + screenname + "\n", self.request)
        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") USER REJECTED: " + screenname)


    def parse_HELO(self, msg: str):
        """
        Using the welcome response sent from the Membership server, parse out the user data of people
        currently in the chatroom.
        :param acpt_message: The string version of the response from the HELO message to the Membership server/.
        :return: A dictionary of user data, with the screenname as the key, and the ip and host as the value in a tuple.
                 Returns False if a RJCT message was sent.
        """
        temp_dict = {}
        for user in msg:
            data = user.split(" ")
            temp_dict[data[0]] = (data[1], data[2])
        return temp_dict

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

    def recv_msg_over_tcp(self, socket):
        """
        Recieve a message from the Membership, and return it.
        :return: Membership server's response, casted from bytes to string.
        """
        chunks = []
        # According to https://docs.python.org/3/howto/sockets.html, it is best practice
        # to keep receiving until your condition is met, which is a newline in our case.
        while True:
            chunk = socket.recv(1024)
            # if chunk == b'':
            #     raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            if b"\n" in chunk:
                break

        return str(b''.join(chunks), 'utf-8')

    def send_acpt_message(self, screenname):
        msg = "ACPT "
        for user in GlobalVars.CHAT_SOCKET_PARENT.hosts:
            msg += user + " " + GlobalVars.CHAT_SOCKET_PARENT.hosts[user][0] + " " + str(GlobalVars.CHAT_SOCKET_PARENT.hosts[user][1]) + ":"
        msg = msg[:-1]
        msg += "\n"

        self.send_msg_over_tcp(msg, GlobalVars.CHAT_SOCKET_PARENT.hosts[screenname][3]) # This is crashing
        GlobalVars.LOGGER.debug("SENT ACPT MESSAGE TO: " + screenname + str(GlobalVars.CHAT_SOCKET_PARENT.hosts[screenname][0])
                                + " " + str(GlobalVars.CHAT_SOCKET_PARENT.hosts[screenname][1]))

    def user_exited_room(self):
        screenname = GlobalVars.CHAT_SOCKET_PARENT.get_host_by_client_address(self.client_address)

        for host in GlobalVars.CHAT_SOCKET_PARENT.hosts:
            GlobalVars.CHAT_SOCKET_PARENT.send_msg_over_udp("EXIT " + screenname + "\n",
                                                                GlobalVars.CHAT_SOCKET_PARENT.hosts[host][0],
                                                                GlobalVars.CHAT_SOCKET_PARENT.hosts[host][1])
            GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") SENT USER EXIT TO " + host)

        del GlobalVars.CHAT_SOCKET_PARENT.hosts[screenname]
        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") PROCESSED USER EXIT: " + screenname)
        self.request.close()