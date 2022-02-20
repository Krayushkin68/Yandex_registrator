import logging
import sys
from logging import StreamHandler, Formatter

logger = logging.getLogger('my_logger')
logger.propagate = False
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s', datefmt='%d-%m-%y %H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
