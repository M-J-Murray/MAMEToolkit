from MAMEToolkit.pacman_environment.Actions import Actions

def start_game(frame_ratio):
    return [
        {"wait": int(10/frame_ratio), "actions": [Actions.COIN1]},
        {"wait": int(200/frame_ratio), "actions": [Actions.ONE_PLAYER_START]},
    ]
