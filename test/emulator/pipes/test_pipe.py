import unittest
from hamcrest import *
from threading import Thread
from queue import Queue as DefaultQueue
from multiprocessing import set_start_method, get_start_method, Process, Queue as MPQueue

from src.MAMEToolkit.emulator.pipes import Pipe

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


def setup_pipe(pipe):
    console = MockConsole(pipe)
    pipe.open(console)
    console.openThread.join(timeout=0.1)
    assert_that(console.openThread.is_alive(), equal_to(False))
    return console.results.get()


def open_pipe(path, mode, queue):
    queue.put(open(path,mode))


def close_pipes(pipe1, pipe2):
    closeThread = Thread(target=pipe1.close)
    closeThread.start()
    pipe2.close()
    closeThread.join(timeout=0.1)


def setup_all_pipes():
    write_pipe = Pipe("env1", "write", 'w', "mame/pipes")
    lua_read_pipe = setup_pipe(write_pipe)

    read_pipe = Pipe("env1", "read", 'r', "mame/pipes")
    lua_write_pipe = setup_pipe(read_pipe)

    return write_pipe, lua_read_pipe, read_pipe, lua_write_pipe


def run_write(output_queue):
    write_pipe, lua_read_pipe = [None, None]
    try:
        write_pipe = Pipe("env1", "write", 'w', "mame/pipes")
        lua_read_pipe = setup_pipe(write_pipe)

        write_pipe.writeln("test")
        output_queue.put(lua_read_pipe.readline())
    finally:
        close_pipes(write_pipe, lua_read_pipe)


def run_read(output_queue):
    read_pipe, lua_write_pipe = [None, None]
    try:
        read_pipe = Pipe("env1", "read", 'r', "mame/pipes")
        lua_write_pipe = setup_pipe(read_pipe)

        lua_write_pipe.write("test\n")
        lua_write_pipe.flush()
        output_queue.put(read_pipe.readln(timeout=1))
    finally:
        close_pipes(read_pipe, lua_write_pipe)


class MockConsole(object):

    def __init__(self, testPipe):
        self.testPipe = testPipe
        self.results = DefaultQueue()

    def writeln(self, line):
        luaMode = 'r' if self.testPipe.mode == 'w' else 'w'
        assert_that(line, equal_to(self.testPipe.pipeId+' = assert(io.open("'+str(self.testPipe.path.absolute())+'", "'+luaMode+'"))'))
        self.openThread = Thread(target=open_pipe, args=[self.testPipe.path, luaMode, self.results])
        self.openThread.start()


# pipes must be opened simultaneously
class PipeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if get_start_method(True) != "spawn":
            set_start_method("spawn")
        cls.tearDownClass()

    @classmethod
    def tearDownClass(cls):
        files = os.listdir("mame/pipes/")
        if len(files) > 0:
            for f in files:
                os.remove("mame/pipes/"+f)

    def test_write(self):
        write_pipe, lua_read_pipe = [None, None]
        try:
            write_pipe = Pipe("env1", "write", 'w', "mame/pipes")
            lua_read_pipe = setup_pipe(write_pipe)

            write_pipe.writeln("test")
            assert_that(lua_read_pipe.readline(), equal_to("test\n"))
        finally:
            close_pipes(write_pipe, lua_read_pipe)

    def test_read(self):
        read_pipe, lua_write_pipe = [None, None]
        try:
            read_pipe = Pipe("env1", "read", 'r', "mame/pipes")
            lua_write_pipe = setup_pipe(read_pipe)

            lua_write_pipe.write("test\n")
            lua_write_pipe.flush()
            assert_that(read_pipe.readln(timeout=0.1), equal_to(b"test"))
        finally:
            close_pipes(read_pipe, lua_write_pipe)

    def test_readln_empty(self):
        read_pipe, lua_write_pipe = [None, None]
        try:
            read_pipe = Pipe("env1", "read", 'r', "mame/pipes")
            lua_write_pipe = setup_pipe(read_pipe)

            with self.assertRaises(IOError) as context:
                read_pipe.readln(timeout=0.1)

            assert_that(str(context.exception), contains_string("Failed to read value from 'readPipe'"))
        finally:
            close_pipes(read_pipe, lua_write_pipe)

    def test_read_from_write_pipe(self):
        write_pipe, lua_read_pipe = [None, None]
        try:
            write_pipe = Pipe("env1", "write", 'w', "mame/pipes")
            lua_read_pipe = setup_pipe(write_pipe)

            with self.assertRaises(IOError) as context:
                write_pipe.readln()

            assert_that(str(context.exception), contains_string("Attempted to read from '/home/michael/dev/MAMEToolkit/test/emulator/mame/pipes/write-env1.pipe' in 'w' mode"))

        finally:
            close_pipes(write_pipe, lua_read_pipe)

    def test_write_to_read_pipe(self):
        read_pipe, lua_write_pipe = [None, None]
        try:
            read_pipe = Pipe("env1", "read", 'r', "mame/pipes")
            lua_write_pipe = setup_pipe(read_pipe)

            with self.assertRaises(IOError) as context:
                read_pipe.writeln("TEST")

            assert_that(str(context.exception), contains_string("Attempted to write to '/home/michael/dev/MAMEToolkit/test/emulator/mame/pipes/read-env1.pipe' in 'r' mode"))

        finally:
            close_pipes(read_pipe, lua_write_pipe)

    def test_lua_string(self):
        write_pipe, lua_read_pipe, read_pipe, lua_write_pipe = [None, None, None, None]
        try:
            write_pipe, lua_read_pipe, read_pipe, lua_write_pipe = setup_all_pipes()

            assert_that(read_pipe.get_lua_string(args=["test"]), equal_to('readPipe:write(test.."\\n"); readPipe:flush(); '))
            assert_that(write_pipe.get_lua_string(), equal_to("writePipe:read(); "))
        finally:
            close_pipes(write_pipe, lua_read_pipe)
            close_pipes(read_pipe, lua_write_pipe)

    def test_multiprocessing_read(self):
        workers = 4
        output_queue = MPQueue()
        processes = [Process(target=run_read, args=[output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            assert_that(output_queue.get(timeout=0.1), equal_to(b"test"))

    def test_multiprocessing_write(self):
        workers = 4
        output_queue = MPQueue()
        processes = [Process(target=run_write, args=[output_queue]) for i in range(workers)]
        [process.start() for process in processes]
        [process.join() for process in processes]
        for i in range(workers):
            assert_that(output_queue.get(timeout=0.1), equal_to("test\n"))
