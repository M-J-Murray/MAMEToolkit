import unittest
from hamcrest import *
from time import sleep
from multiprocessing import set_start_method, get_start_method, Process, Queue
from src.MAMEToolkit.emulator.Console import Console

import os
del os.environ["FONTCONFIG_PATH"]

mame_root = os.environ["MAME_ROOT"]
game_id = os.environ.get("GAME_ID", "sfiii3n")

def run_console(game_id, output_queue):
    console = None
    try:
        console = Console(mame_root, game_id)
        sleep(5)
        console.writeln('s = manager.machine.screens[":screen"]')
        output = console.writeln('print(s.width)', expect_output=True)
        output_queue.put(output[0])
    finally:
        console.close()


class ConsoleTest(unittest.TestCase):

    def test_write_read(self):
        console = None
        try:
            console =  Console(mame_root, game_id)
            sleep(5)
            console.writeln('s = manager.machine.screens[":screen"]')
            output = console.writeln('print(s.width)', expect_output=True)
            assert_that(output[0], equal_to("384"))
        finally:
            console.close()

    def test_multiprocessing(self):
        if get_start_method(True) != "spawn":
            set_start_method("spawn")
        workers = 10
        output_queue = Queue()
        processes = [Process(target=run_console, args=[game_id, output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            assert_that(output_queue.get(timeout=0.1), equal_to("384"))
