import threading


# A thread used for reading data from a thread
# pipes don't have very good time out functionality, so this is used in combination with a queue
class StreamGobbler(threading.Thread):

    def __init__(self, pipe, queue, debug=False):
        threading.Thread.__init__(self)
        self.pipe = pipe
        self.queue = queue
        self.debug = debug
        self._stop_event = threading.Event()
        self.has_cursor = False

    def run(self):
        for line in iter(self.pipe.readline, b''):
            if self.debug:
                print(line)
            self.queue.put(line[:-1])
            if self._stop_event.is_set():
                break

    def wait_for_cursor(self):
        new_line_count = 0
        while new_line_count != 3:
            line = self.pipe.readline()
            if line == b'\n':
                new_line_count += 1

    def stop(self):
        self._stop_event.set()
