import numpy as np
from MAMEToolkit.emulator.pipes import Pipe


# A special implementation of a Linux FIFO pipe which is used for reading all of the frame data and memory address values from the emulator
class DataPipe(object):

    def __init__(self, env_id, screen_dims, addresses, pipes_path):
        self.pipe = Pipe(env_id, "data", 'r', pipes_path)
        self.screenDims = screen_dims
        self.addresses = addresses

    def open(self, console):
        self.pipe.open(console)

    def close(self):
        self.pipe.close()

    # Generates the equivalent Lua code specifying what data the Lua engine should return every time step 
    def get_lua_string(self):
        return self.pipe.get_lua_string(args=[address.get_lua_string() for address in self.addresses.values()]+['s:pixels()'])

    def read_data(self, timeout=10):
        data = {}
        line = self.pipe.readln(timeout=timeout)
        cursor = 0
        for k in self.addresses.keys():
            cursor_end = cursor
            while line[cursor_end] != 43:
                cursor_end += 1
            part = line[cursor:cursor_end]
            data[k] = int(part.decode("utf-8"))
            cursor = cursor_end+1
        data["frame"] = np.frombuffer(line[cursor:], dtype='uint8').reshape(self.screenDims["height"], self.screenDims["width"], 4)
        return data

