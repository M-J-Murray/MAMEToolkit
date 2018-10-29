import unittest
from hamcrest import *
from time import sleep
from multiprocessing import set_start_method, Process, Queue
from src.emulator.Console import Console


def run_console(game_id, output_queue):
    console = None
    try:
        console = Console(game_id)
        sleep(5)
        console.writeln('s = manager:machine().screens[":screen"]')
        output = console.writeln('print(s:width())', expect_output=True)
        output_queue.put(output[0])
    finally:
        console.close()


class ConsoleTest(unittest.TestCase):

    def test_write_read(self):
        game_id = "sfiii3n"
        console = None
        try:
            console = Console(game_id)
            sleep(5)
            console.writeln('s = manager:machine().screens[":screen"]')
            output = console.writeln('print(s:width())', expect_output=True)
            assert_that(output[0], equal_to("384"))
        finally:
            console.close()

    def test_multiprocessing(self):
        set_start_method("spawn")
        workers = 10
        game_id = "sfiii3n"
        output_queue = Queue()
        processes = [Process(target=run_console, args=[game_id, output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            assert_that(output_queue.get(timeout=0.1), equal_to("384"))
