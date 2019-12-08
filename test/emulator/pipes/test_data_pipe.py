import unittest
from hamcrest import *
from threading import Thread
from queue import Queue as DefaultQueue

from src.MAMEToolkit.emulator.pipes import DataPipe
from src.MAMEToolkit.emulator import Address
from src.MAMEToolkit.emulator.BitmapFormat import BitmapFormat
from multiprocessing import get_start_method, set_start_method, Process, Queue as MPQueue

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


def setup_data_pipe(data_pipe):
    console = MockConsole(data_pipe.pipe)
    data_pipe.open(console)
    console.open_thread.join(timeout=0.1)
    assert_that(console.open_thread.is_alive(), equal_to(False))
    return console.results.get(timeout=0.1)


def open_pipe(path, mode, queue):
    queue.put(open(path, mode))


def close_pipes(pipe1, pipe2):
    close_thread = Thread(target=pipe1.close)
    close_thread.start()
    pipe2.close()
    close_thread.join(timeout=0.1)


def run_read(output_pipe):
    bitmap_format = BitmapFormat.RGB32
    addresses = {"test1": Address("0x00000000", "u8"), "test2": Address("0x00000001", "u16")}
    screen_dims = {"width": 1, "height": 1}
    data_pipe = DataPipe("env1", screen_dims, bitmap_format, addresses, "mame/pipes/")
    write_pipe = setup_data_pipe(data_pipe)
    write_pipe.write("1+2+abc\n")
    write_pipe.flush()

    output_pipe.put(data_pipe.read_data())


class MockConsole(object):

    def __init__(self, test_pipe):
        self.test_pipe = test_pipe
        self.results = DefaultQueue()
        self.open_thread = None
    
    def writeln(self, line):
        lua_mode = 'r' if self.test_pipe.mode == 'w' else 'w'
        assert_that(line, equal_to(self.test_pipe.pipeId + ' = assert(io.open("' + str(self.test_pipe.path.absolute()) + '", "' + lua_mode + '"))'))
        self.open_thread = Thread(target=open_pipe, args=[self.test_pipe.path, lua_mode, self.results])
        self.open_thread.start()


class DataPipeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tearDownClass()

    @classmethod
    def tearDownClass(cls):
        files = os.listdir("mame/pipes/")
        if len(files) > 0:
            for f in files:
                os.remove("mame/pipes/"+f)

    def test_empty_lua_string(self):
        data_pipe, write_pipe = [None, None]
        try:
            bitmap_format = BitmapFormat.RGB32
            addresses = {}
            screen_dims = {"width": 1, "height": 1}
            data_pipe = DataPipe("env1", screen_dims, bitmap_format, addresses, "mame/pipes")
            write_pipe = setup_data_pipe(data_pipe)
            write_pipe.write("1+2+abc\n")
            write_pipe.flush()

            assert_that(data_pipe.get_lua_string(), equal_to('dataPipe:write(s:bitmap_binary().."\\n"); dataPipe:flush(); '))
        finally:
            close_pipes(data_pipe, write_pipe)

    def test_lua_string(self):
        data_pipe, write_pipe = [None, None]
        try:
            bitmap_format = BitmapFormat.RGB32
            addresses = {"test1": Address("0x00000000", "u8"), "test2": Address("0x00000001", "u16")}
            screen_dims = {"width": 1, "height": 1}
            data_pipe = DataPipe("env1", screen_dims, bitmap_format, addresses, "mame/pipes")
            write_pipe = setup_data_pipe(data_pipe)
            write_pipe.write("1+2+abc\n")
            write_pipe.flush()

            assert_that(data_pipe.get_lua_string(), equal_to('dataPipe:write(mem:read_u8(0x00000000).."+"..mem:read_u16(0x00000001).."+"..s:bitmap_binary().."\\n"); dataPipe:flush(); '))
        finally:
            close_pipes(data_pipe, write_pipe)

    def test_read_data(self):
        data_pipe, write_pipe = [None, None]
        try:
            bitmap_format = BitmapFormat.RGB32
            addresses = {"test1": Address("0x00000000", "u8"), "test2": Address("0x00000001", "u16")}
            screen_dims = {"width": 1, "height": 1}
            data_pipe = DataPipe("env1", screen_dims, bitmap_format, addresses, "mame/pipes")
            write_pipe = setup_data_pipe(data_pipe)
            write_pipe.write("1+2+abc\n")
            write_pipe.flush()

            data = data_pipe.read_data()
            assert_that(len(data), is_(equal_to(3)))
            assert_that(data["frame"][0][0][0], is_(equal_to(97)))
            assert_that(data["frame"][0][0][1], is_(equal_to(98)))
            assert_that(data["frame"][0][0][2], is_(equal_to(99)))
            assert_that(data["test1"], is_(equal_to(1)))
            assert_that(data["test2"], is_(equal_to(2)))
        finally:
            close_pipes(data_pipe, write_pipe)

    def test_read_data_multiprocessing(self):
        if get_start_method(True) != "spawn":
            set_start_method("spawn")
        workers = 1
        output_queue = MPQueue()
        processes = [Process(target=run_read, args=[output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            data = output_queue.get(timeout=0.1)
            assert_that(data["frame"][0][0][0], is_(equal_to(97)))
            assert_that(data["frame"][0][0][1], is_(equal_to(98)))
            assert_that(data["frame"][0][0][2], is_(equal_to(99)))
            assert_that(data["test1"], is_(equal_to(1)))
            assert_that(data["test2"], is_(equal_to(2)))