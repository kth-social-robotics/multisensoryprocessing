from datetime import datetime
from multiprocessing import Process, Queue
from os.path import abspath, dirname, join

class Logger(Process):
    def __init__(self, log_file=""):
        super(Logger, self).__init__()
        if log_file == "":
            self.log_file = abspath(join(dirname( __file__ ), '..', 'log_file.csv'))
        self.queue = Queue()

    def run(self):
        while True:
            sender, message = self.queue.get().split("#")
            if message == "done":
                break
            else:
                self.log(sender, message)

    def log(self, sender, message):
        """ Add a time stamp and write the message to the log file.
        """
        time = datetime.now()
        time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}\t{:11}\t".format(\
                      time.year, time.month, time.day, time.hour, time.minute, time.second,\
                      str(time.microsecond)[:3], sender)
        message = "{}{}".format(time_stamp, message)
        print(message)
        with open(self.log_file, "a") as log_file:
            log_file.write(message + "\n")
