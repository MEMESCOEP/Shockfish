### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from pishock import PiShockAPI
from enum import Enum
import hashlib
import pickle


## CLASSES ##
class PiShockCommandTypes(Enum):
    Vibrate = 1
    Shock = 0

class ZapManager:
    ## VARIABLES ##
    ConfigHash = None
    PSShockers = None
    PiShockURL = "https://do.pishock.com/api/apioperate/"
    Config = {'ShareCode': None, 'Username': None, 'APIKey': None}
    PSAPI = PiShockAPI("InvalidUNAME", "InvalidKEY")

    ## FUNCTIONS ##
    def SendCommandToPiShock(Command: PiShockCommandTypes, Intensity: int, Duration: float, Debug=False):
        for ConfigValue in ZapManager.Config.items():
            if ConfigValue[1] == None or isinstance(ConfigValue[1], str) == False or ConfigValue[1].isspace() == True or len(ConfigValue[1]) <= 0:
                print(f"[ERROR] >> Config value \"{ConfigValue[0]}\" is not configured!")
                return

        print(f"[INFO] >> Sending \"{Command.name}\" command with intensity of {Intensity}% and duration of {Duration}s...")
        ZapManager.PSAPI.username = ZapManager.Config['Username']
        ZapManager.PSAPI.api_key = ZapManager.Config['APIKey']

        CurrentConfigHash = hashlib.md5(pickle.dumps(ZapManager.Config)).hexdigest()

        if ZapManager.ConfigHash != CurrentConfigHash:
            if Debug == True:
                print(f"[DEBUG] >> Configuration was changed: \"{ZapManager.ConfigHash}\" -> \"{CurrentConfigHash}\"")
                print("[DEBUG] >> Getting shocker(s) for new share code...")

            ZapManager.PSShockers = ZapManager.PSAPI.shocker(ZapManager.Config['ShareCode'])
            ZapManager.ConfigHash = CurrentConfigHash
        
        match Command:
            case PiShockCommandTypes.Vibrate:
                ZapManager.PSShockers.vibrate(duration=Duration, intensity=Intensity)

            case PiShockCommandTypes.Shock:
                ZapManager.PSShockers.shock(duration=Duration, intensity=Intensity)

            case _:
                print(f"[ERROR] >> Invalid command: \"{Command.name}\"")

    def SetConfig(ShareCode, Username, APIKey):
        ZapManager.Config['ShareCode'] = ShareCode
        ZapManager.Config['Username'] = Username
        ZapManager.Config['APIKey'] = APIKey

        