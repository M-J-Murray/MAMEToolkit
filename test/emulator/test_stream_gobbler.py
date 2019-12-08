import unittest
from hamcrest import *
from src.MAMEToolkit.emulator.StreamGobbler import StreamGobbler
from multiprocessing import get_start_method, set_start_method, Process, Queue
import queue


def run_gobbler(lines, output_queue):
    pipe = MockPipe(lines)
    line_queue = queue.Queue()
    gobbler = None
    try:
        gobbler = StreamGobbler(pipe, line_queue)
        gobbler.wait_for_cursor()
        gobbler.start()
        for _ in range(3):
            output_queue.put(line_queue.get(timeout=0.1))
    finally:
        gobbler.stop()


class MockPipe(object):

    def __init__(self, lines):
        self.lines = lines
        self.index = 0

    def readline(self):
        if self.index < 3:
            line = b"\n"
        else:
            line = self.lines[self.index % 3]
        self.index += 1
        return line


class StreamGobblerTest(unittest.TestCase):

    def test_read_lines(self):
        lines = [b"test1\n", b"test2\n", b"test3\n"]
        pipe = MockPipe(lines)
        line_queue = queue.Queue()
        gobbler = None
        try:
            gobbler = StreamGobbler(pipe, line_queue, debug=True)
            gobbler.wait_for_cursor()
            gobbler.start()
            for i in range(3):
                assert_that(line_queue.get(timeout=0.1), is_(equal_to(lines[i][:-1])))
        finally:
            gobbler.stop()

    def test_multiprocessing(self):
        if get_start_method(True) != "spawn":
            set_start_method("spawn")
        workers = 2
        lines = [b"test1\n", b"test2\n", b"test3\n"]
        output_queue = Queue()
        processes = [Process(target=run_gobbler, args=[lines, output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for _ in range(workers):
            for j in range(3):
                assert_that(output_queue.get(timeout=0.1), is_(equal_to(lines[j][:-1])))
