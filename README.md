# The MAME Reinforcement Learning Training Toolkit
This toolkit has the to potential to train your reinforcement learning algorithm on almost any arcade game. It works as a wrapper around [MAME](http://mamedev.org/) to enable your algorithm to step through gameplay while recieving the frame data and internal memory address values for tracking the games state, along with sending actions to interact with the game.

# PUBLICATION PENDING...

## About

## Example Function Calls

### [Example Street Fighter III Third Strike: Fight for the Future Implementation](https://github.com/BombayCinema/MAMEToolkit/blob/master/Environment.py)

## Street Fighter Random Agent Demo
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

## Library Performance Benchmarks with PC Specs
