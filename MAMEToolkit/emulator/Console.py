import os
from pathlib import Path
from subprocess import Popen, PIPE
from MAMEToolkit.emulator.StreamGobbler import StreamGobbler
import queue
import logging


# A class for starting the MAME emulator, and communicating with the Lua engine console
class Console(object):

    # Starts up an instance of MAME with POpen
    # Uses a separate thread for reading from the console outputs
    # render is for displaying the frames to the emulator window, disabling it has little to no effect
    # throttle enabled will run any game at the intended gameplay speed, disabling it will run the game as fast as the computer can handle
    # debug enabled will print everything that comes out of the Lua engine console
    def __init__(self, roms_path, game_id, render=True, throttle=False, debug=False):
        self.logger = logging.getLogger("Console")

        command = f"exec ./mame -rompath '{str(Path(roms_path).absolute())}' -pluginspath plugins -skip_gameinfo -sound none -console "+game_id
        if not render:
            command += " -video none"
        if throttle:
            command += " -throttle"
        else:
            command += " -frameskip 10"

        # Start lua console
        script_path = os.path.dirname(os.path.abspath(__file__))
        self.process = Popen(command, cwd=f"{script_path}/mame", shell=True, stdin=PIPE, stdout=PIPE)

        # Start read queues
        self.stdout_queue = queue.Queue()
        self.gobbler = StreamGobbler(self.process.stdout, self.stdout_queue, debug=debug)
        self.gobbler.wait_for_cursor()
        self.gobbler.start()

    # Read the oldest line which may have been output by the console
    # Uses the FIFO principle, once a line is read it is removed from the queue
    # timeout determines how long the function will wait for an output if there is nothing immediately available
    def readln(self, timeout=0.5):
        line = self.stdout_queue.get(timeout=timeout)
        while len(line)>0 and line[0] == 27:
            line = line[19:]
        return line.decode("utf-8")

    # Read as many lines from the console as there are available
    # timeout determines how long the function will wait for an output if there is nothing immediately available
    def readAll(self, timeout=0.5):
        lines = []
        while True:
            try:
                lines.append(self.readln(timeout=timeout))
            except queue.Empty as e:
                break
        return lines

    def writeln(self, command, expect_output=False, timeout=0.5):
        self.process.stdin.write(command.encode("utf-8") + b'\n')
        self.process.stdin.flush()
        output = self.readAll(timeout=timeout)

        if expect_output and len(output) == 0:
            error = "Expected output but received nothing from emulator after '" + command + "'"
            self.logger.error(error)
            raise IOError(error)
        if not expect_output and len(output) > 0:
            error = "No output expected from command '" + command + "', but recieved: " + "\n".join(output)
            self.logger.error(error)
            raise IOError(error)
        if expect_output:
            return output

    # Mainly for testing
    # Safely kills the emulator process
    def close(self):
        self.process.kill()
        try:
            self.process.wait(timeout=3)
        except Exception as e:
            error = "Failed to close emulator console"
            self.logger.error(error, e)
            raise EnvironmentError(error)
        self.gobbler.stop()
