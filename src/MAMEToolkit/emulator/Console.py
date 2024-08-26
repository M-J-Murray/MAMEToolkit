import os
from pathlib import Path
from subprocess import Popen, PIPE
from MAMEToolkit.emulator.StreamGobbler import StreamGobbler
import queue
import logging

fonts_path = os.path.join(os.path.dirname(__file__), 'mame', 'fonts')
if "FONTCONFIG_PATH" not in os.environ:
    os.environ["FONTCONFIG_PATH"] = fonts_path
elif fonts_path not in os.environ["FONTCONFIG_PATH"]:
    os.environ["FONTCONFIG_PATH"] += ";" + fonts_path


# A class for starting the MAME emulator, and communicating with the Lua engine console
class Console(object):

    # Starts up an instance of MAME with POpen
    # Uses a separate thread for reading from the console outputs
    # render is for displaying the frames to the emulator window, disabling it has little to no effect
    # throttle enabled will run any game at the intended gameplay speed, disabling it will run the game as fast as the computer can handle
    # debug enabled will print everything that comes out of the Lua engine console
    def __init__(self, mame_root, game_id, cheat_debugger=False, render=True, throttle=False, frame_skip=0, sound=False, debug=False, maximize=True):
        self.logger = logging.getLogger("Console")

        mame_path = str(Path(mame_root).absolute())
        
        command = f"exec mame -rompath roms -pluginspath plugins -skip_gameinfo -window -nomaximize -console "+game_id
        if not render:
            command += " -video none"

        if cheat_debugger:
            command += " -debug"

        if throttle:
            command += " -throttle"
        else:
            command += " -nothrottle"

        if maximize:
            command += " -maximize"
        else:
            command += " -nomaximize"

        command += " -frameskip "+str(frame_skip)

        if not sound:
            command += " -sound none"

        # Start lua console
        self.process = Popen(command, cwd=mame_path, shell=True, stdin=PIPE, stdout=PIPE)

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

        # Strip LUA prompt from output.
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

    def writeln(self, command, expect_output=False, timeout=0.5, raiseError=True):
        self.process.stdin.write(command.encode("utf-8") + b'\n')
        self.process.stdin.flush()
        output = self.readAll(timeout=timeout)

        # Sometimes the input command is included in the output so we strip it.
        if len(output) > 0 and output[0] == command:
            del(output[0])

        if expect_output and len(output) == 0:
            error = "Expected output but received nothing from emulator after '" + command + "'"
            if raiseError:
                self.logger.error(error)
                raise IOError(error)
            else:
                return None
        if not expect_output and len(output) > 0:
            error = "No output expected from command '" + command + "', but recieved:" + str(output)
            if raiseError:
                self.logger.error(error)
                raise IOError(error)
            else:
                return None
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
