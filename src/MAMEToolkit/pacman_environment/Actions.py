from enum import Enum
from MAMEToolkit.emulator import Action


# An enumerable class used to specify which actions can be used to interact with a game
# Specifies the Lua engine port and field names required for performing an action
class Actions(Enum):
    # System setting
    BONUS_LIFE =   Action(':DSW1', 'Bonus Life')
    GHOST_NAMES =   Action(':DSW1', 'Ghost Names')
    COINAGE =   Action(':DSW1', 'Coinage')
    LIVES =  Action(':DSW1', 'Lives')
    DIFFICULTY =  Action(':DSW1', 'Difficulty')
    SERVICE_MODE =  Action(':IN1', 'Service Mode')
    CABINET =  Action(':IN1', 'Cabinet')

    # Coins
    COIN1 = Action(':IN0', 'Coin 1')
    COIN2 = Action(':IN0', 'Coin 2')

    # Start
    ONE_PLAYER_START = Action(':IN1', '1 Player Start')
    TWO_PLAYER_START = Action(':IN1', '2 Player Start')
    
    # Movement
    P1_UP =     Action(':IN0', 'P1 Up')
    P1_DOWN =   Action(':IN0', 'P1 Down')
    P1_LEFT =   Action(':IN0', 'P1 Left')
    P1_RIGHT =  Action(':IN0', 'P1 Right')

    P2_UP =     Action(':IN1', 'P2 Up')
    P2_DOWN =   Action(':IN1', 'P2 Down')
    P2_LEFT =   Action(':IN1', 'P2 Left')
    P2_RIGHT =  Action(':IN1', 'P2 Right')
