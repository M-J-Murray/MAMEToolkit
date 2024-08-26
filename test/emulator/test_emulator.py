import unittest
from hamcrest import *

from src.MAMEToolkit.emulator import Emulator
from src.MAMEToolkit.emulator import Address
from multiprocessing import Process, Queue
from time import sleep

import os
#del os.environ["FONTCONFIG_PATH"]

mame_root = os.environ["MAME_ROOT"]
game_id = os.environ.get("GAME_ID", "sfiii3n")

def run_emulator(env_id, roms_path, game_id, memory_addresses, output_queue):
    emulator = None
    try:
        emulator = Emulator(env_id, mame_root, game_id, memory_addresses)
        output_queue.put(emulator.step([]))
    finally:
        emulator.close()


class EmulatorTest(unittest.TestCase):

    def test_screen_dimensions(self):
        memory_addresses = {"test": Address("02000008", "u8")}
        emulator = None
        try:
            emulator = Emulator("testEnv1", mame_root, game_id, memory_addresses)
            assert_that(emulator.screenDims["width"], equal_to(384))
            assert_that(emulator.screenDims["height"], equal_to(224))
        finally:
            emulator.close()

    def test_step(self):
        memory_addresses = {"test": Address("02000008", "u8")}
        emulator = None
        try:
            emulator = Emulator("testEnv1", mame_root, game_id, memory_addresses)
            data = emulator.step([])
            assert_that(data["frame"].shape, equal_to((224, 384, 4)))
            assert_that(data["test"], equal_to(0))
        finally:
            emulator.close()

    def test_multiprocessing(self):
        workers = 2
        memory_addresses = {"test": Address("02000008", "u8")}
        output_queue = Queue()
        processes = [Process(target=run_emulator, args=[f"testEnv{i}", mame_root, game_id, memory_addresses, output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        sleep(14)
        [process.join(timeout=1) for process in processes]
        for i in range(workers):
            data = output_queue.get(timeout=0.1)
            assert_that(data["frame"].shape, equal_to((224, 384, 4)))
            assert_that(data["test"], equal_to(0))
