### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from enum import Enum
import UI as GUI


## CLASSES ##
class CommandTypes(Enum):
    Vibrate = 1
    Shock = 0

class ZapManager:
    ## VARIABLES ##
    PiShockURL = "https://do.pishock.com/api/apioperate/"

    ## FUNCTIONS ##
    def SendCommandToPiShock(Command: CommandTypes, Intensity: int, Duration: float):
        print(f"[INFO] >> Sending \"{Command.name}\" command with intensity of {Intensity}% and duration of {Duration}s...")