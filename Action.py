from enum import Enum


# An enumerable class used to specify which actions can be used to interact with a game
# Specifies the Lua engine port and field names required for performing an action
class Action(Enum):
    # Starting
    SERVICE =   {"port": ':INPUTS', "field": 'Service Mode'}

    COIN_P1 =   {"port": ':INPUTS', "field": 'Coin 1'}
    COIN_P2 =   {"port": ':INPUTS', "field": 'Coin 2'}

    P1_START =  {"port": ':INPUTS', "field": '1 Player Start'}
    P2_START =  {"port": ':INPUTS', "field": '2 Players Start'}

    # Movement
    P1_UP =     {"port": ':INPUTS', "field": 'P1 Up'}
    P1_DOWN =   {"port": ':INPUTS', "field": 'P1 Down'}
    P1_LEFT =   {"port": ':INPUTS', "field": 'P1 Left'}
    P1_RIGHT =  {"port": ':INPUTS', "field": 'P1 Right'}

    P2_UP =     {"port": ':INPUTS', "field": 'P2 Up'}
    P2_DOWN =   {"port": ':INPUTS', "field": 'P2 Down'}
    P2_LEFT =   {"port": ':INPUTS', "field": 'P2 Left'}
    P2_RIGHT =  {"port": ':INPUTS', "field": 'P2 Right'}

    # Fighting
    P1_JPUNCH = {"port": ':INPUTS', "field": 'P1 Jab Punch'}
    P1_SPUNCH = {"port": ':INPUTS', "field": 'P1 Strong Punch'}
    P1_FPUNCH = {"port": ':INPUTS', "field": 'P1 Fierce Punch'}
    P1_SKICK =  {"port": ':EXTRA', "field": 'P1 Short Kick'}
    P1_FKICK =  {"port": ':EXTRA', "field": 'P1 Forward Kick'}
    P1_RKICK =  {"port": ':EXTRA', "field": 'P1 Roundhouse Kick'}

    P2_JPUNCH = {"port": ':INPUTS', "field": 'P2 Jab Punch'}
    P2_SPUNCH = {"port": ':INPUTS', "field": 'P2 Strong Punch'}
    P2_FPUNCH = {"port": ':INPUTS', "field": 'P2 Fierce Punch'}
    P2_SKICK =  {"port": ':EXTRA', "field": 'P2 Short Kick'}
    P2_FKICK =  {"port": ':EXTRA', "field": 'P2 Forward Kick'}
    P2_RKICK =  {"port": ':INPUTS', "field": 'P2 Roundhouse Kick'}
