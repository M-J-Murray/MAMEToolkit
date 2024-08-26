import atexit
import tempfile
from MAMEToolkit.emulator.Console import Console
from MAMEToolkit.emulator.pipes import Pipe
from MAMEToolkit.emulator.pipes import DataPipe

# Converts a list of action Enums into the relevant Lua engine representation
def actions_to_string(actions):
    action_strings = [action.get_lua_string() for action in actions]
    return '+'.join(action_strings)


def list_actions(mame_root, game_id):
    console = Console(mame_root, game_id)
    console.writeln('iop = manager.machine.ioport')
    actions = []
    ports = console.writeln("for k,v in pairs(iop.ports) do print(k) end", expect_output=True, timeout=0.5)
    for port in ports:
        try:
            fields = console.writeln("for k,v in pairs(iop.ports['"+port+"'].fields) do print(k) end", expect_output=True)
            for field in fields:
                actions.append({"port": port, "field": field})
        except IOError as e:
            console.logger.error("Could indicate unused button set")

    console.close()
    return actions


def see_games():
    Emulator("env1", "", "", {})


def run_cheat_debugger(mame_root, game_id):
    Console(mame_root, game_id, cheat_debugger=True, render=True, throttle=True, debug=True)


# An interface for using the Lua engine console functionality
class Emulator(object):

    # env_id - the unique id of the emulator, used for fifo pipes
    # game_id - the game id being used
    # memory_addresses - The internal memory addresses of the game which this class will return the value of at every time step
    # frame_ratio - the ratio of frames that will be returned, 3 means 1 out of every 3 frames will be returned. Note that his also effects how often memory addresses are read and actions are sent
    # See console for render, throttle & debug
    def __init__(self, env_id, mame_root, game_id, memory_addresses, frame_ratio=3, render=True, throttle=False, frame_skip=0, sound=False, debug=False, maximize=False):
        self.memory_addresses = memory_addresses
        self.frame_ratio = frame_ratio

        # setup lua engine
        self.console = Console(mame_root, game_id, render=render, throttle=throttle, frame_skip=frame_skip, sound=sound, debug=debug, maximize=maximize)
        atexit.register(self.close)
        self.wait_for_resource_registration()
        self.create_lua_variables()
        screen_width = self.setup_screen_width()
        screen_height = self.setup_screen_height()
        self.screenDims = {"width": screen_width, "height": screen_height}

        # open pipes
        pipes_path = tempfile.mkdtemp()
        self.actionPipe = Pipe(env_id, "action", 'w', pipes_path)
        self.actionPipe.open(self.console)

        self.dataPipe = DataPipe(env_id, self.screenDims, memory_addresses, pipes_path)
        self.dataPipe.open(self.console)

        # Connect inter process communication
        self.setup_frame_access_loop()

        self.first = True

    def create_lua_variables(self):
        self.console.writeln('iop = manager.machine.ioport')
        self.console.writeln('s = manager.machine.screens[":screen"]')
        self.console.writeln('mem = manager.machine.devices[":maincpu"].spaces["program"]')
        self.console.writeln('releaseQueue = {}')

    def wait_for_resource_registration(self, max_attempts=10):
        screen_registered = False
        program_registered = False
        attempt = 0
        while not screen_registered or not program_registered:
            if not screen_registered:
                result = self.console.writeln('print(manager.machine.screens[":screen"])', expect_output=True, timeout=3, raiseError=False)
                screen_registered = result is not None and result != "nil"
            if not program_registered:
                result = self.console.writeln('print(manager.machine.devices[":maincpu"].spaces["program"])', expect_output=True, timeout=3, raiseError=False)
                program_registered = result is not None and result != "nil"
            if attempt == max_attempts:
                raise EnvironmentError("Failed to register MAME resources!")
            attempt += 1

    # Gets the game screen width in pixels
    def setup_screen_width(self):
        output = self.console.writeln('print(s.width)', expect_output=True, timeout=1)
        if len(output) != 1:
            raise IOError('Expected one result from "print(s.width)", but received: ', str(output))
        return int(output[0])

    # Gets the game screen height in pixels
    def setup_screen_height(self):
        output = self.console.writeln('print(s.height)', expect_output=True, timeout=1)
        if len(output) != 1:
            raise IOError('Expected one result from "print(s.height)"", but received: ', output)
        return int(output[0])

    # Pauses the emulator
    def pause_game(self):
        self.console.writeln('emu.pause()')

    # Unpauses the emulator
    def unpause_game(self):
        self.console.writeln('emu.unpause()')

    # Sets up the callback function written in Lua that the Lua engine will execute each time a frame done
    def setup_frame_access_loop(self):
        pipe_data_func = 'function pipeData() ' \
                            'if (math.fmod(tonumber(s:frame_number()),' + str(self.frame_ratio) +') == 0) then ' \
                                'for i=1,#releaseQueue do ' \
                                    'releaseQueue[i](); ' \
                                    'releaseQueue[i]=nil; ' \
                                'end; ' \
                                '' + self.dataPipe.get_lua_string() + '' \
                                'actions = ' + self.actionPipe.get_lua_string() + '' \
                                'if (string.len(actions) > 1) then ' \
                                    'for action in string.gmatch(actions, "[^+]+") do ' \
                                        'actionFunc = load(action..":set_value(1)"); ' \
                                        'actionFunc(); ' \
                                        'releaseFunc = load(action..":set_value(0)"); ' \
                                        'table.insert(releaseQueue, releaseFunc); ' \
                                    'end; ' \
                                'end; ' \
                            'end; ' \
                        'end'
        self.console.writeln(pipe_data_func)
        self.console.writeln('frame_notifier_sub = emu.add_machine_frame_notifier(pipeData, "data")')

    # Steps the emulator along one time step
    def step(self, actions):
        if self.first:
            self.dataPipe.read_data(timeout=10)
            self.first = False
        action_string = actions_to_string(actions)
        self.actionPipe.writeln(action_string)  # sends the actions for the game to perform before the next step
        data = self.dataPipe.read_data(timeout=10)  # gathers the frame data and memory address values
        return data

    # Testing
    # Safely stops all of the processes related to running the emulator
    def close(self):
        self.console.close()
        self.actionPipe.close()
        self.dataPipe.close()
