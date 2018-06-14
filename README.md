# The MAME Reinforcement Learning Training Toolkit
# PUBLICATION PENDING...

## About
This toolkit has the to potential to train your reinforcement learning algorithm on almost any arcade game. It works as a wrapper around [MAME](http://mamedev.org/) to enable your algorithm to step through gameplay while recieving the frame data and internal memory address values for tracking the games state, along with sending actions to interact with the game.

## Street Fighter Random Agent Demo
The toolkit has currently been applied to Street Fighter III Third Strike: Fight for the Future, which will be will now be demonstrated.
```python
import random
from Main.SF_Environment.Environment import Environment

env = Environment(difficulty=5, frame_ratio=3, frames_per_step=3)
env.start()
while True:
    move_action = random.randint(0, 8)
    attack_action = random.randint(0, 9)
    frames, reward, round_done, stage_done = env.step(move_action, attack_action)
    if stage_done:
        env.next_game()
    elif round_done:
        env.next_round()
```

## Example Function Calls
It doesn't take much to interact with the emulator itself with this toolkit, however the challenge comes from finding the memory address values associated with the internal state you care about, and tracking sais state with your environment class.
The internal memory states of a game can be tracked using the [MAME Cheat Debugger](http://docs.mamedev.org/debugger/cheats.html), which allows you to track how the memory address values of the game change over time.
To create an emulation of the game you must first have the ROM for the game you are emulating and know the game ID used by MAME. Once you have these and have determined the memory addresses you wish to track you can start the emulation:
```python
from MAMEToolkit import Emulator

game_id = "sfiii3n"
memory_addresses = {
        "fighting": Address('0x0200EE44', 'u8'),
        "winsP1": Address('0x02011383', 'u8'),
        "winsP2": Address('0x02011385', 'u8'),
        "healthP1": Address('0x02068D0B', 's8'),
        "healthP2": Address('0x020691A3', 's8')
    }
emulator = Emulator("sfiii3n", memory_addresses)
```
This will immediately start the emulation and halt it when it toolkit has linked to the emulator process. Once the toolkit is linked, you can step the emulator along using the step function:
```python
data = emulator.step([])

frame = data["frame"]
is_fighting = data["fighting"]
player1_wins = data["winsP1"]
player2_wins = data["winsP2"]
player1_health = data["healthP1"]
player2_health = data["healthP2"]
```
The step function returns the frame data as a NumPy matrix, along with all of the memory address integer values from that timestep.

To send actions to the emulator you also need to determine which input ports the game supports and along with the fields for each port. For example, with street fighter to insert a coin the following code is required:
```python
from MAMEToolkit import Action

insert_coin = Action(':INPUTS', 'Coin 1')
data = emulator.step([insert_coin])
```
To identify which ports are availble use the list actions command:
```python
from MAMEToolkit import list_actions

game_id = "sfiii3n"
print(list_actions(game_id))
```
which for street fighter returns a list with all the ports and fields required to perform an action in the step function:
```python
[
    {'port': ':scsi:1:cdrom:SCSI_ID', 'field': 'SCSI ID'}, 
    {'port': ':INPUTS', 'field': 'P2 Jab Punch'}, 
    {'port': ':INPUTS', 'field': 'P1 Left'}, 
    {'port': ':INPUTS', 'field': 'P2 Fierce Punch'}, 
    {'port': ':INPUTS', 'field': 'P1 Down'}, 
    {'port': ':INPUTS', 'field': 'P2 Down'}, 
    {'port': ':INPUTS', 'field': 'P2 Roundhouse Kick'}, 
    {'port': ':INPUTS', 'field': 'P2 Strong Punch'}, 
    {'port': ':INPUTS', 'field': 'P1 Strong Punch'}, 
    {'port': ':INPUTS', 'field': '2 Players Start'}, 
    {'port': ':INPUTS', 'field': 'Coin 1'}, 
    {'port': ':INPUTS', 'field': '1 Player Start'}, 
    {'port': ':INPUTS', 'field': 'P2 Right'}, 
    {'port': ':INPUTS', 'field': 'Service 1'}, 
    {'port': ':INPUTS', 'field': 'Coin 2'}, 
    {'port': ':INPUTS', 'field': 'P1 Jab Punch'}, 
    {'port': ':INPUTS', 'field': 'P2 Up'}, 
    {'port': ':INPUTS', 'field': 'P1 Up'}, 
    {'port': ':INPUTS', 'field': 'P1 Right'}, 
    {'port': ':INPUTS', 'field': 'Service Mode'}, 
    {'port': ':INPUTS', 'field': 'P1 Fierce Punch'}, 
    {'port': ':INPUTS', 'field': 'P2 Left'}, 
    {'port': ':EXTRA', 'field': 'P2 Short Kick'}, 
    {'port': ':EXTRA', 'field': 'P2 Forward Kick'}, 
    {'port': ':EXTRA', 'field': 'P1 Forward Kick'}, 
    {'port': ':EXTRA', 'field': 'P1 Roundhouse Kick'}, 
    {'port': ':EXTRA', 'field': 'P1 Short Kick'}
]
```
We advise you to create an enum of all the possible actions, then send their action values to the emulator, see [the example Actions Enum](https://github.com/BombayCinema/MAMEToolkit/blob/master/Actions.py)

There is also the problem of transitioning games between non-learnable gameplay screens such as the title screen and character select. To see how this can be implemented please look at the provided [Steps script](https://github.com/BombayCinema/MAMEToolkit/blob/master/Steps.py) and the [Example Street Fighter III Third Strike: Fight for the Future Environment Implementation](https://github.com/BombayCinema/MAMEToolkit/blob/master/Environment.py)

## Library Performance Benchmarks with PC Specs
