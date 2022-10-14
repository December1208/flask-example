import multiprocessing
from logging.handlers import RotatingFileHandler
import logging


class SafeRotatingFileHandler(RotatingFileHandler):
    """
    多进程下 RotatingFileHandler 会出现问题
    """

    _rollover_lock = multiprocessing.Lock()

    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                with self._rollover_lock:
                    if self.shouldRollover(record):
                        self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def shouldRollover(self, record):
        if self._should_rollover():
            # if some other process already did the rollover we might
            # checked log.1, so we reopen the stream and check again on
            # the right log file
            if self.stream:
                self.stream.close()
                self.stream = self._open()

            return self._should_rollover()

        return 0

    def _should_rollover(self):
        if self.maxBytes > 0:
            self.stream.seek(0, 2)
            if self.stream.tell() >= self.maxBytes:
                return True

        return False
