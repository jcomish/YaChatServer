from threading import Thread, Lock
import logging
import coloredlogs
import GlobalVars as GlobalVars
from ChatSocketParent import ChatSocketParent
import socket

server_lock = Lock()
GlobalVars.LOGGER = logging.getLogger(__name__)
# GlobalVars.LOGGER.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=GlobalVars.LOGGER)

def run_client(port="7575"):
    GlobalVars.CHAT_SOCKET_LISTENER = ChatSocketParent("127.0.0.1", int(port))
    # socket.gethostbyname(socket.gethostname())

if __name__ == '__main__':
    GlobalVars.LOGGER.debug("Starting client")
    t = Thread(target=run_client, args=("7583",))
    t.start()
    GlobalVars.LOGGER.debug("Server started")