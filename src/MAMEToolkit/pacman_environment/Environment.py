import ctypes

from MAMEToolkit.emulator import Emulator
from MAMEToolkit.emulator import Address
from MAMEToolkit.pacman_environment.util import *
from MAMEToolkit.pacman_environment.Steps import *
from MAMEToolkit.pacman_environment.Actions import Actions

# Combines the data of multiple time steps
def add_rewards(old_data, new_data):
    for k in old_data.keys():
        if "rewards" in k:
            for player in old_data[k]:
                new_data[k][player] += old_data[k][player]
    return new_data


# Returns the list of memory addresses required to train on Street Fighter
def setup_memory_addresses():
    return {
        "scoreHigh": Address('0x4E80','u8'),
        "scoreMid": Address('0x4E81','u8'),
        "scoreLow": Address('0x4E82','u8'),
        "livesP1":  Address('0x4E15','u8'),
        "level":    Address('0x4E13','u8'),
        "playing":  Address('0x4EAC','u8')
    }

# Converts and index (action) into the relevant movement action Enum, depending on the player
def index_to_move_action(action):
    return {
        0: [Actions.P1_UP],
        1: [Actions.P1_DOWN],
        2: [Actions.P1_LEFT],
        3: [Actions.P1_RIGHT],
        4: []
    }[action]

def format_score(high, mid, low):
    # The score is stored in 3 bytes with values representing the high, mid, and low digits.
    # These are values of 0-99 and must be converted from hex strings to numbers.
    return int(f'{str(hex(low)).removeprefix('0x').zfill(2)}{str(hex(mid)).removeprefix('0x').zfill(2)}{str(hex(high)).removeprefix('0x').zfill(2)}')

# The Pacman specific interface for training an agent against the game
class Environment(object):

    # env_id - the unique identifier of the emulator environment, used to create fifo pipes
    # difficulty - the difficult to be used in gameplay
    # frame_ratio, frames_per_step - see Emulator class
    # render, throttle, debug - see Console class
    def __init__(self, env_id, mame_root, difficulty=3, frame_ratio=3, frames_per_step=3, render=True, throttle=False, frame_skip=0, sound=False, debug=False, maximize=False, wall_detection=False):
        self.difficulty = difficulty
        self.frame_ratio = frame_ratio
        self.frames_per_step = frames_per_step
        self.throttle = throttle
        self.emu = Emulator(env_id, mame_root, "pacman", setup_memory_addresses(), frame_ratio=frame_ratio, render=render, throttle=throttle, frame_skip=frame_skip, sound=sound, debug=debug, maximize=maximize)
        self.level = 0
        self.lives = 0
        self.playing = False
        self.game_done = False
        self.score = 0
        self.wall_detection = wall_detection # If true the walls around pacman are detected and valid moves for the step are returned.
        self.valid_moves = tuple([0,1,2,3,4]) # Seed valid moves

    # Runs a set of action steps over a series of time steps
    # Used for transitioning the emulator through non-learnable gameplay, aka. title screens, character selects
    def run_steps(self, steps):
        for step in steps:
            for i in range(step["wait"]):
                self.emu.step([])
            self.emu.step([action.value for action in step["actions"]])

    # Must be called first after creating this class
    # Sends actions to the game until the learnable gameplay starts
    # Returns the first few frames of gameplay
    def start(self):
        self.run_steps(start_game(self.frame_ratio))
        frames = self.wait_for_playing()
        self.playing = True
        return frames

    # Observes the game and waits for gameplay to begin
    def wait_for_playing(self):
        data = self.emu.step([])
        while data["playing"] == False:
            data = self.emu.step([])
        data = self.gather_frames([])
        return data["frame"]

    def reset(self):
        self.game_done = False
        return self.start()
        

    # Collects the specified amount of frames the agent requires before choosing an action
    def gather_frames(self, actions):
        data = self.sub_step(actions)
        frames = [data["frame"]]
        for _ in range(self.frames_per_step - 1):
            data = add_rewards(data, self.sub_step(actions))
            frames.append(data["frame"])
        data["frame"] = frames[0] if self.frames_per_step == 1 else frames
        return data

    # Steps the emulator along by one time step and feeds in any actions that require pressing
    # Takes the data returned from the step and updates book keeping variables
    def sub_step(self, actions):
        data = self.emu.step([action.value for action in actions])
        
        old_score = self.score
        new_score = format_score(data["scoreHigh"], data["scoreMid"], data["scoreLow"])
        self.score = new_score

        old_lives = self.lives
        new_lives = ctypes.c_int8(data["livesP1"]).value
        self.lives = new_lives

        if self.lives < 0:
            self.game_done = True
        
        rewards = {
            "points": (new_score - old_score),
            "lives": (new_lives - old_lives)
        }

        data["rewards"] = rewards
        return data

    # Steps the emulator along by the requested amount of frames required for the agent to provide actions
    def step(self, move_action=4):
        if self.playing:
                actions = []
                actions += index_to_move_action(move_action)
                data = self.gather_frames(actions)
                if self.wall_detection:
                    self.valid_moves = get_valid_moves(data["frame"] if self.frames_per_step == 1 else data["frame"][-1])
                return data["frame"], data["rewards"], self.game_done, self.valid_moves
        else:
            raise EnvironmentError("Start must be called before stepping")
    
    # Safely closes emulator
    def close(self):
        self.emu.close()
