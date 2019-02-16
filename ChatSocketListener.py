from ChatSocket import ChatSocket
import threading
import socket
import GlobalVars as GlobalVars
from datetime import datetime
import time


class ChatSocketListener(ChatSocket):
    """
    This will be the servant thread, and will listen for any messages coming in from other users
    and the Membership Server.
    """
    def __init__(self, local_ip="127.0.0.1", listener_port="7575"):
        self.local_ip = local_ip
        self.listener_port = listener_port
        self.hosts = {}
        self.open_socket = None

        self.chat_socket_tcp_listener = threading.Thread(target=self.listen_over_tcp)
        self.chat_socket_tcp_listener.start()
        return

    def close_listener(self):
        self.chat_socket_listener.join()

        return

    def listen_to_socket(self, screenname):
        """
        This made more sense to be in this class...
        :return:
        """
        try:
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.connect((self.hosts[screenname][0], self.hosts[screenname][1]))
            # GlobalVars.CHAT_SOCKET_LISTENER.hosts[screenname].append(sock)

            while True:
                msg, addr = sock.recvfrom(1024)
                msg = str(msg, 'utf-8')
                GlobalVars.LOGGER.info("(" + str(datetime.now()) + " MESSAGED RECEIVED: " + msg)
                if "EXIT" in msg:
                    self.user_exited_room(str(msg[5:-1]))
                else:
                    GlobalVars.LOGGER.warning("(" + str(datetime.now()) + ") UNKNOWN MESSAGE: " + msg)
        except:
            GlobalVars.LOGGER.exception("(" + str(datetime.now()) + ") FAILED TO CLAIM PORT " + str(self.listener_port) + "!")

    def listen_over_tcp(self):
        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ")" + " ATTEMPTING CONNECTION TO " +
                                self.local_ip + " " + str(self.listener_port))

        self.open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.local_ip, self.listener_port)
        self.open_socket.bind(server_address)
        self.open_socket.listen(1)
        self.open_socket, addr = self.open_socket.accept()

        while(True):
            msg = self.recv_msg_over_tcp()
            if msg[:4] == "HELO":
                msg = str(msg[5:-1]).split(" ")
                if msg[0] in self.hosts:
                    self.reject_user()
                else:
                    # self.establish_tcp_socket(msg[0])
                    listener = threading.Thread(target=self.listen_to_socket, args=(msg[0],))
                    self.hosts[msg[0]] = (msg[1], int(msg[2]), listener)
                    listener.start()

                    self.send_acpt_message(msg[0])
                    self.send_join_to_room(msg[0])

        # """
        # This made more sense to be in this class...
        # :return:
        # """
        # try:
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     server_address = (self.local_ip, int(self.listener_port))
        #     sock.bind(server_address)
        #
        #     while True:
        #         msg, addr = sock.recvfrom(1024)
        #         msg = str(msg, 'utf-8')
        #         GlobalVars.LOGGER.info("(" + str(datetime.now()) + " MESSAGED RECEIVED: " + msg)
        #         if "EXIT" in msg:
        #             self.user_exited_room(str(msg[5:-1]))
        #         else:
        #             GlobalVars.LOGGER.warning("(" + str(datetime.now()) + ") UNKNOWN MESSAGE: " + msg)
        # except:
        #     GlobalVars.LOGGER.exception("(" + str(datetime.now()) + ") FAILED TO CLAIM PORT " + self.listener_port + "!")

    def user_exited_room(self, msg):
        for host in GlobalVars.CHAT_SOCKET_SENDER.hosts:
            self.send_msg_over_udp("EXIT " + host + "\n", self.hosts[host][0], self.hosts[host][1])
            GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") SENT USER EXIT TO " + host)

        # Remove the user from the list
        del GlobalVars.CHAT_SOCKET_SENDER.hosts[msg]
        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") PROCESSED USER EXIT: " + msg)

    def send_join_to_room(self, screenname):
        for host in GlobalVars.CHAT_SOCKET_SENDER.hosts:
            self.send_msg_over_udp("JOIN " + screenname + " " + self.hosts[screenname][1] + " " + str(self.hosts[screenname][2]) + "\n",
                                   self.hosts[screenname][0], self.hosts[screenname][1])
            GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") SENT USER JOIN TO " + screenname)

    def reject_user(self, screenname, ip, port):
        self.send_msg_over_tcp("RJCT " + screenname + "\n")
        del GlobalVars.CHAT_SOCKET_SENDER.hosts[screenname]
        GlobalVars.LOGGER.debug("(" + str(datetime.now()) + ") USER REJECTED: " + screenname)

    def send_acpt_message(self, screenname):
        msg = "ACPT "
        for user in self.hosts:
            msg += user + " " + self.hosts[user][0] + " " + str(self.hosts[user][1]) + ":"
        msg = msg[:-1]
        msg += "\n"
        time.sleep(5)
        self.send_msg_over_tcp(msg, self.hosts[screenname][3])

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


