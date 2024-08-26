import random
from MAMEToolkit.sf_environment import Environment

mame_path = "/Users/rojo/Desktop/mame0267-arm64"  # Replace this with the path to your MAME installation.
env = Environment("test2", mame_path, frames_per_step=3)
env.start()
while True:
    move_action = random.randint(0, 8)
    attack_action = random.randint(0, 9)
    frames, reward, round_done, stage_done, game_done = env.step(move_action, attack_action)
    print(f'{reward}\t{round_done}\t{stage_done}\t{game_done}')
    if game_done:
        env.new_game()
    elif stage_done:
        env.next_stage()
    elif round_done:
        env.next_round()