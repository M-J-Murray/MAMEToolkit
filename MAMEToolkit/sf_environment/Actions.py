from enum import Enum
from MAMEToolkit.emulator.Action import Action


# An enumerable class used to specify which actions can be used to interact with a game
# Specifies the Lua engine port and field names required for performing an action
class Actions(Enum):
    # Starting
    SERVICE =   Action(':INPUTS', 'Service Mode')

    COIN_P1 =   Action(':INPUTS', 'Coin 1')
    COIN_P2 =   Action(':INPUTS', 'Coin 2')

    P1_START =  Action(':INPUTS', '1 Player Start')
    P2_START =  Action(':INPUTS', '2 Players Start')

    # Movement
    P1_UP =     Action(':INPUTS', 'P1 Up')
    P1_DOWN =   Action(':INPUTS', 'P1 Down')
    P1_LEFT =   Action(':INPUTS', 'P1 Left')
    P1_RIGHT =  Action(':INPUTS', 'P1 Right')

    P2_UP =     Action(':INPUTS', 'P2 Up')
    P2_DOWN =   Action(':INPUTS', 'P2 Down')
    P2_LEFT =   Action(':INPUTS', 'P2 Left')
    P2_RIGHT =  Action(':INPUTS', 'P2 Right')

    # Fighting
    P1_JPUNCH = Action(':INPUTS', 'P1 Jab Punch')
    P1_SPUNCH = Action(':INPUTS', 'P1 Strong Punch')
    P1_FPUNCH = Action(':INPUTS', 'P1 Fierce Punch')
    P1_SKICK =  Action(':EXTRA', 'P1 Short Kick')
    P1_FKICK =  Action(':EXTRA', 'P1 Forward Kick')
    P1_RKICK =  Action(':EXTRA', 'P1 Roundhouse Kick')

    P2_JPUNCH = Action(':INPUTS', 'P2 Jab Punch')
    P2_SPUNCH = Action(':INPUTS', 'P2 Strong Punch')
    P2_FPUNCH = Action(':INPUTS', 'P2 Fierce Punch')
    P2_SKICK =  Action(':EXTRA', 'P2 Short Kick')
    P2_FKICK =  Action(':EXTRA', 'P2 Forward Kick')
    P2_RKICK =  Action(':INPUTS', 'P2 Roundhouse Kick')
