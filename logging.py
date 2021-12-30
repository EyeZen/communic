from datetime import datetime
import threading

class Log:
    def __init__(self, log_file, save=False):
        self.lock = threading.Lock()
        self.lock.acquire()
        if save:
            self.file = open(log_file, "at")
            self.write = self.file.write
        else:
            self.file = None
            self.write = print
        self.write('\n------------------------------------------------------------\n')
        self.lock.release()

    def log(self, msg):
        time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S | ")
        self.lock.acquire()
        self.write(f"\n{time} << {msg} >>")
        self.lock.release()

    def __del__(self):
        if self.file:
            self.file.close()