import unittest
from hamcrest import *

from MAMEToolkit.emulator.Emulator import Emulator
from MAMEToolkit.emulator.Address import Address
from multiprocessing import set_start_method, Process, Queue


def run_emulator(env_id, game_id, roms_path, memory_addresses, output_queue):
    emulator = None
    try:
        emulator = Emulator(env_id, roms_path, game_id, memory_addresses)
        output_queue.put(emulator.step([]))
    finally:
        emulator.close()


class EmulatorTest(unittest.TestCase):

    def test_screen_dimensions(self):
        memory_addresses = {"test": Address("02000008", "u8")}
        game_id = "sfiii3n"
        emulator = None
        try:
            emulator = Emulator("testEnv1", "/home/michael/dev/MAMEToolkit/MAMEToolkit/emulator/mame/roms", game_id, memory_addresses)
            assert_that(emulator.screenDims["width"], equal_to(384))
            assert_that(emulator.screenDims["height"], equal_to(224))
        finally:
            emulator.close()

    def test_step(self):
        memory_addresses = {"test": Address("02000008", "u8")}
        game_id = "sfiii3n"
        emulator = None
        try:
            emulator = Emulator("testEnv1", game_id, memory_addresses)
            data = emulator.step([])
            assert_that(data["frame"].shape, equal_to((224, 384, 3)))
            assert_that(data["test"], equal_to(0))
        finally:
            emulator.close()

    def test_multiprocessing(self):
        set_start_method("spawn")
        workers = 10
        game_id = "sfiii3n"
        memory_addresses = {"test": Address("02000008", "u8")}
        output_queue = Queue()
        processes = [Process(target=run_emulator, args=[f"testEnv{i}", "/home/michael/dev/MAMEToolkit/MAMEToolkit/emulator/mame/roms", game_id, memory_addresses, output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            data = output_queue.get(timeout=0.1)
            assert_that(data["frame"].shape, equal_to((224, 384, 3)))
            assert_that(data["test"], equal_to(0))
