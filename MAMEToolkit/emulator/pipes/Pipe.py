import os
from MAMEToolkit.emulator.StreamGobbler import StreamGobbler
from pathlib import Path
from queue import Queue
from threading import Thread
import logging


def delete_old_pipes(pipes_path):
    for the_file in os.listdir(pipes_path):
        file_path = os.path.join(pipes_path, the_file)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(e)


def open_pipe(pipe_queue, path, mode):
    pipe_queue.put(open(path, mode + "b"))


# A class used for creating and interacting with a Linux FIFO pipe
class Pipe(object):

    def __init__(self, env_id, pipe_id, mode, pipes_path):
        self.pipeId = pipe_id + "Pipe"
        self.mode = mode
        self.pipes_path = Path(pipes_path)
        if not self.pipes_path.exists():
            self.pipes_path.mkdir()
        self.path = self.pipes_path.joinpath(Path(pipe_id + "-" + str(env_id) + ".pipe"))
        self.logger = logging.getLogger("Pipe: "+str(self.path.absolute()))
        if self.path.exists():
            self.path.unlink()
        os.mkfifo(str(self.path.absolute()))
        self.logger.info("Created pipe file")

    # Generates the equivalent Lua code specifying how the Lua engine should use the pipe
    # Args are used for specifying which data should be returned to the toolkit at every time step
    def get_lua_string(self, args=None):
        if self.mode == 'r':
            if not args:
                raise IOError("Write pipe expects arguments to write")
            return self.pipeId+':write('+'.."+"..'.join(args)+'.."\\n"); '+self.pipeId+':flush(); '
        elif self.mode == 'w':
            return self.pipeId+':read(); '
        else:
            error = "Invalid mode for pipe, '"+self.mode+"'"
            self.logger.error(error)
            raise IOError(error)

    # Opens the pipe in the toolkit and in the Lua engine
    # When a pipe is opened in read mode, it will block the thread until the same pipe is opened in write mode on a different thread 
    def open(self, console):
        try:
            lua_mode = 'r' if self.mode == 'w' else 'w'
            # Open Console pipe
            console.writeln(self.pipeId+' = assert(io.open("'+str(self.path.absolute())+'", "'+lua_mode+'"))')
            self.logger.info("Opened lua pipe")

            # Read bytes not strings
            pipe_queue = Queue()
            open_thread = Thread(target=open_pipe, args=[pipe_queue, str(self.path.absolute()), self.mode])
            open_thread.start()
            open_thread.join(timeout=3)
            self.fifo = pipe_queue.get(timeout=1)

            self.logger.info("Opened local pipe")

            if self.mode == "r":
                self.read_queue = Queue()
                StreamGobbler(self.fifo, self.read_queue).start()
        except Exception as e:
            error = "Failed to open pipe '" + str(self.path.absolute()) + "'"
            self.logger.error(error)
            raise IOError(error)

    def close(self):
        self.fifo.close()
    
    # Writes to the pipe
    def writeln(self, line):
        if self.mode == 'w':
            self.fifo.write(line.encode("utf-8")+b'\n')
            self.fifo.flush()
        else:
            error = "Attempted to write to '"+str(self.path.absolute())+"' in '"+str(self.mode)+"' mode"
            self.logger.error(error)
            raise IOError(error)
    
    # Reads to the pipe
    # timeout specifies how long the pipe should wait before there is likely to be a problem on the Lua engines side
    def readln(self, timeout=1):
        if self.mode == 'r':
            try:
                return self.read_queue.get(timeout=timeout)
            except Exception as e:
                error = "Failed to read value from '"+self.pipeId+"'"
                self.logger.error(error)
                raise IOError(error)
        else:
            error = "Attempted to read from '"+str(self.path.absolute())+"' in '"+str(self.mode)+"' mode"
            self.logger.error(error)
            raise IOError(error)