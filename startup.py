from apps.delegation.main import Delegation
from apps.player.main import Player

import threading, time
import logging


if __name__ == '__main__':
    logging.disable()
    
    threading.Thread(target=Delegation).start()
    threading.Thread(target=Player).start()
