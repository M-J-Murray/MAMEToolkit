from multiprocessing import Process, freeze_support, set_start_method
import random
from MAMEToolkit.sf_environment import Environment

mame_path = "/Users/rojo/Desktop/mame0267-arm64"  # Replace this with the path to your MAME installation.
workers = 8 # The number of emulators to run

def run_env(worker_id, mame_path):
    env = Environment(f"env{worker_id}", mame_path)
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

if __name__ == '__main__':
    freeze_support()
    set_start_method('spawn')
    threads = [Process(target=run_env, args=(i, mame_path)) for i in range(workers)]
    [thread.start() for thread in threads]
