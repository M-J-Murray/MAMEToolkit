# The MAME RL Algorithm Training Toolkit

## About
This Python library will allow you to train your reinforcement learning algorithm on almost any arcade game. It is currently available on Linux systems and works as a wrapper around [MAME](http://mamedev.org/). The toolkit allows your algorithm to step through gameplay while recieving the frame data and internal memory address values for tracking the games state, along with sending actions to interact with the game.

## Requirements:
- Operating system: Vast majority of desktop and server Linux distributions
- Instruction set: amd64 (this includes intel CPUs)
- Python version: 3.6 or greater

**NOTE**: If you are using an uncommon linux distribution or a CPU with a different instruction set, see section [Compiling custom MAME](#Compiling-custom-MAME).

## Installation
You can use `pip` to install the library, just run:
```bash
pip install MAMEToolkit
```

**DISCLAIMER: We are unable to provide you with any game ROMs. It is the users own legal responsibility to acquire a game ROM for emulation. This library should only be used for non-commercial research purposes.**

There are some free ROMs available at: https://www.mamedev.org/roms/

## Sponsorship & Future Development :heart:
I have just joined the [Github Sponsors](https://github.com/sponsors/M-J-Murray) program and would appreciate any donations towards future development on this project. There are a plans to extend and improve upon this library, and with your help we can make this happen. If you would like to show your appreciation or request a new game environment/feature be added, feel free to go to https://github.com/sponsors/M-J-Murray and become a sponsor today!

The sponsor page also outlines future plans and optimisations which will help improve the library for everyone.


## Street Fighter Random Agent Demo
The toolkit has currently been applied to Street Fighter III Third Strike: Fight for the Future (Japan 990608, NO CD), but can modified for any game available on MAME. The following demonstrates how a random agent can be written for a street fighter environment.
```python
import random
from MAMEToolkit.sf_environment import Environment

roms_path = "roms/"  # Replace this with the path to your ROMs
env = Environment("env1", roms_path)
env.start()
while True:
    move_action = random.randint(0, 8)
    attack_action = random.randint(0, 9)
    frames, reward, round_done, stage_done, game_done = env.step(move_action, attack_action)
    if game_done:
        env.new_game()
    elif stage_done:
        env.next_stage()
    elif round_done:
        env.next_round()
```

The toolkit also supports hogwild training:
```python
from multiprocessing import Process
import random
from MAMEToolkit.sf_environment import Environment


def run_env(worker_id, roms_path):
    env = Environment(f"env{worker_id}", roms_path)
    env.start()
    while True:
        move_action = random.randint(0, 8)
        attack_action = random.randint(0, 9)
        frames, reward, round_done, stage_done, game_done = env.step(move_action, attack_action)
        if game_done:
            env.new_game()
        elif stage_done:
            env.next_stage()
        elif round_done:
            env.next_round()


workers = 8
# Environments must be created outside of the threads
roms_path = "roms/"  # Replace this with the path to your ROMs
threads = [Process(target=run_env, args=(i, roms_path)) for i in range(workers)]
[thread.start() for thread in threads]
```

![](pics/hogwild3.gif "Hogwild Random Agents")

## Setting Up Your Own Game Environment

**Game ID's**<br>
To create an emulation of the game you must first have the ROM for the game you are emulating and know the game ID used by MAME, for example for this version of street fighter it is 'sfiii3n'. 
The id of your game can be found by running:
```python
from src.MAMEToolkit.emulator import see_games
see_games()
```
This will bring up the MAME emulator. You can search through the list of games to find the one you want. The id of the game is always in brackets at the end of the game title.

**Memory Addresses**<br>
It doesn't take much to interact with the emulator itself using the toolkit, however the challenge comes from finding the memory address values associated with the internal state you care about, and tracking said state with your environment class.
The internal memory states of a game can be tracked using the [MAME Cheat Debugger](http://docs.mamedev.org/debugger/cheats.html), which allows you to track how the memory address values of the game change over time.


The cheat debugger can be run using the following:
```python
from src.MAMEToolkit.emulator import run_cheat_debugger
roms_path = "roms/" # Replace this with the path to your ROMs
game_id = "sfiii3n"
run_cheat_debugger(roms_path, game_id)
```
For information about using the debugger, see the Memory dump section of the following [tutorial](http://bzztbomb.com/blog/2013/03/23/use-mames-debugger-to-reverse-engineer-and-extend-old-games/)


Once you have determined the memory addresses you wish to track you can start the emulation using:
```python
from src.MAMEToolkit.emulator import Emulator
from src.MAMEToolkit.emulator import Address

roms_path = "roms/"  # Replace this with the path to your ROMs
game_id = "sfiii3n"
memory_addresses = {
        "fighting": Address('0x0200EE44', 'u8'),
        "winsP1": Address('0x02011383', 'u8'),
        "winsP2": Address('0x02011385', 'u8'),
        "healthP1": Address('0x02068D0B', 's8'),
        "healthP2": Address('0x020691A3', 's8')
    }
    
emulator = Emulator("env1", roms_path, game_id, memory_addresses)
```
This will immediately start the emulation and halt it when the toolkit has linked to the emulator process. 

**Stepping the emulator**<br>
Once the toolkit is linked, you can step the emulator along using the step function:
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

**Sending inputs**
To send actions to the emulator you also need to determine which input ports and fields the game supports. For example, with street fighter to insert a coin the following code is required:
```python
from src.MAMEToolkit.emulator import Action

insert_coin = Action(':INPUTS', 'Coin 1')
data = emulator.step([insert_coin])
```
To identify which ports are availble use the list actions command:
```python
from src.MAMEToolkit.emulator import list_actions

roms_path = "roms/"  # Replace this with the path to your ROMs
game_id = "sfiii3n"
print(list_actions(roms_path, game_id))
```
which for street fighter returns the list with all the ports and fields available for sending actions to the step function:
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
We advise you to create an enum of all the possible actions, then send their action values to the emulator, see [the example Actions Enum](src/MAMEToolkit/sf_environment/Actions.py)

There is also the problem of transitioning games between non-learnable gameplay screens such as the title screen and character select. To see how this can be implemented please look at the provided [Steps script](src/MAMEToolkit/sf_environment/Steps.py) and the [Example Street Fighter III Third Strike: Fight for the Future Environment Implementation](src/MAMEToolkit/sf_environment/Environment.py)

The emulator class also has a frame_ratio argument which can be used for adjusting the frame rate seen by your algorithm. By default MAME generates frames at 60 frames per second, however, this may be too many frames for your algorithm. The toolkit by default will use a frame_ratio of 3, which means that 1 in 3 frames are sent through the toolkit, this converts the frame rate to 20 frames per second. Using a higher frame_ratio also increases the performance of the toolkit.
```Python
from src.MAMEToolkit.emulator import Emulator

emulator = Emulator(env_id, roms_path, game_id, memory_addresses, frame_ratio=3)
```

## Running The Library Without A Screen / On A Linux Server
If you are running a linux server or a docker instance then you will need to add some extra code to your python script to enable MAME to run.
To achieve this we will be using the [Xvfb library](https://en.wikipedia.org/wiki/Xvfb), which will simulate an instance of the X display server. 
Simply install the `Xvfb` library for your relevant linux distro. Then add to the following two lines to the top of your main Python script.
```python
import os
os.system("Xvfb :0 -screen 0 800x600x16 +extension RANDR &")
os.environ["DISPLAY"] = ":0"
```
This will simulate a 800x600 resolution screen with 16-bit colour. Feel free to change the parameters to suit your needs.


## Library Performance Benchmarks with PC Specs
The development and testing of this toolkit have been completed on an 8-core AMD FX-8300 3.3GHz CPU along with a 3GB GeForce GTX 1060 GPU.
With a single random agent, the street fighter environment can be run at 600%+ the normal gameplay speed. And For hogwild training with 8 random agents, the environment can be run at 300%+ the normal gameplay speed.

## Simple ConvNet Agent
To ensure that the toolkit is able to train algorithms, a simple 5 layer ConvNet was setup with minimal tuning. The algorithm was able to successfully learn some simple mechanics of Street Fighter, such as combos and blocking. The Street Fighter gameplay works by having the player fight different opponents across 10 stages of increasing difficulty. Initially, the algorithm would reach stage 2 on average, but eventually could reach stage 5 on average after 2200 episodes of training. The learning rate was tracked using the net damage done vs damage taken of a single playthough for each episode.

![](pics/chart.png "ConvNet Results")

## MAME Changes
The library acts as a wrapper around a modified MAME implementation.
The following changes were made:
* Updated the lua console to allow for the retrieval of the format of frame data
* Update the lua console to allow for the retrieval of the current frames data
* Disabled game start warnings

The following files are affected:
* src/emu/machine.cpp
* src/emu/video.cpp
* src/emu/video.h
* src/frontend/mame/luaengine.cpp
* src/frontend/mame/ui/ui.cpp
* src/osd/sdl/window.cpp

**The modified MAME implementation can be found at [https://github.com/M-J-Murray/mame]**

## Compiling custom MAME
Unfortunately this library doesn't work with every single OS or CPU instruction set. This is because it uses a custom precompiled instance of MAME that is specific to the OS and CPU it was compiled on.
However, if you are using a different linux distribution or instruction set, this does not mean you are out of options, it just means that your path to using this library is a little more complicated.
Your only remaining option is to compile the custom instance of MAME yourself. To achieve this you just need a linux distribution with a GUI. Other operating systems will not work, as the library relies heavily on linux fifo pipes.

### Compilation steps
To compile your own custom instance of MAME run the following commands in your terminal:
```bash
git clone git@github.com:M-J-Murray/mame.git
cd mame
make SUBTARGET=arcade -j4
```
Adjust `j` to match the amount of virtual cores your CPU supports, as this could take several hours depending on your computer.

Once the compilation has completed you should have an executable file called `mamearcade64`, or something along those lines.
Now you can either use the binary_path keyword argument on your emulator method calls to point at your custom binary, or you can rename said executable to `mame` and replace the precompiled MAME instance in your python MAMEToolkit directory with your new file.
You should be able to find the MAMEToolkit directory by going to your python environment directory, and then going to `site-packages`.

### Troubleshooting
This section describes what to do if your `make` command fails with some kind of error message describing an incorrect/missing library.
As different linux distributions implement different libraries by default it is likely that you will not have the correct libraries installed by default. These libraries will also need to be specific to your CPU instruction set.
Writing all the library installation commands for all linux distributions and instruction sets would be extremely difficult, however, I can outline the libraries that MAME requires. The list is as follows:
* libdl
* librt
* libSDL2-2.0
* libpthread
* libutil
* libGL
* libasound
* libQt5Widgets
* libQt5Gui
* libQt5Core
* libX11
* libSDL2_ttf-2.0
* libfontconfig
* libstdc++
* libm
* libgcc_s
* libc
 
Your error message should indicate that at least one of these libraries is missing. To install said library you will need to look online and find out how to install/update the library for your relevant linux distribution and instruction set. 
Use the following as a google search template: "{linux distribution} {CPU instruction set} install {missing library}"
Just replace the curly brackets with the information relevant to you. Hopefully you should be able to find the relevant install command on a forum. If the missing library isn't available for your distro/cpu then the MAMEToolkit will not work for you.

Once you have installed your library just run `make` again and it will continue where it left off, you will not lose your compilation progress.
