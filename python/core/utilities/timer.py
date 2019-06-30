import time
import log_tools

logger = log_tools.logger(__name__)


class Timer(object):

    def __init__(self):
        self.start = time.time()

    def end(self):
        logger.info(time.time() - self.start)
