from Main.SF_Environment.Actions import Actions


def set_difficulty(frame_ratio, difficulty):  
    steps = [
        {"wait": 0, "actions": [Actions.SERVICE]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]}]
    if (difficulty % 8) < 3: 
        steps += [{"wait": int(30/frame_ratio), "actions": [Actions.P1_LEFT]} for i in range(3-(difficulty % 8))]
    else:  
        steps += [{"wait": int(30/frame_ratio), "actions": [Actions.P1_RIGHT]} for i in range((difficulty % 8)-3)]
    steps += [
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_DOWN]},
        {"wait": int(30/frame_ratio), "actions": [Actions.P1_JPUNCH]}]
    return steps


def start_game(frame_ratio):
    return [
        {"wait": 180, "actions": [Actions.COIN_P1]},
        {"wait": 1, "actions": [Actions.COIN_P1]},
        {"wait": int(60/frame_ratio), "actions": [Actions.P1_START]},
        {"wait": int(80/frame_ratio), "actions": [Actions.P1_LEFT, Actions.P1_JPUNCH]},
        {"wait": int(60/frame_ratio), "actions": [Actions.P1_JPUNCH]},
        {"wait": int(60/frame_ratio), "actions": [Actions.P1_JPUNCH]}]


def reset_game(frame_ratio, wins):
    steps = []
    if wins["P1"] == 2:
        steps += [
            {"wait": int(60/frame_ratio), "actions": [Actions.P1_JPUNCH]}
        ]
        steps += [{"wait": 0, "actions": [Actions.P1_JPUNCH]} for i in range(int(180/frame_ratio))]
        steps += [{"wait": int(60/frame_ratio), "actions": [Actions.P1_JPUNCH]}]
    elif wins["P2"] == 2:
        steps += [{"wait": 0, "actions": [Actions.SERVICE]},
            {"wait": int(30 / frame_ratio), "actions": [Actions.P1_UP]},
            {"wait": int(30 / frame_ratio), "actions": [Actions.P1_JPUNCH]},
            {"wait": 180, "actions": [Actions.COIN_P1]},
            {"wait": 1, "actions": [Actions.COIN_P1]},
            {"wait": int(60 / frame_ratio), "actions": [Actions.P1_START]},
            {"wait": int(80 / frame_ratio), "actions": [Actions.P1_LEFT, Actions.P1_JPUNCH]},
            {"wait": int(60 / frame_ratio), "actions": [Actions.P1_JPUNCH]},
            {"wait": int(60 / frame_ratio), "actions": [Actions.P1_JPUNCH]}]
    else:
        raise EnvironmentError("ERROR: Asked to restart gameplay without winner")
    return steps
