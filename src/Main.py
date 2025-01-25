### SHOCKFISH ###
# By MEMESCOEP


## IMPORTS ##
from chessdotcom import ChessDotComClient, Client, get_player_game_archives
import PiShockManager as PiShockManager
import UI as GUI
import multiprocessing
import tracemalloc
import traceback
import requests
import pishock
import psutil
import chess.engine
import chess.pgn
import chess
import time
import sys
import io
import os


## CLASSES ##
class Tee:
    def __init__(self, *file_objects):
        self.file_objects = file_objects

    def write(self, message):
        # Check if the message ends with a newline (this is the behavior of print())
        # We'll handle the newline behavior separately for console and file
        for file in self.file_objects:
            if file is sys.stdout:
                # For stdout (console), we allow the print's behavior with the newline
                sys.__stdout__.write(message)  # console output
            else:
                # For files, strip the newline (so we don't add extra newlines in the file)
                file.write(message)

    def flush(self):
        for file in self.file_objects:
            file.flush()
        sys.__stdout__.flush()


## VARIABLES ##
SelectableGameModes = ["Realtime", "GameOver"]
ArchivesRequestURL = "https://api.chess.com/pub/player/<USERNAME>/games/archives"
ShockersToControl = 1
CurrentGameMode = SelectableGameModes[1]
DefaultWinSize = [750, 440]
RequestHeaders = {"User-Agent": "Shockfish/1.0"}
PlayerUsername = "memescoep"
ProgramVersion = "0.1"
GTKUIFilePath = os.path.join(os.getcwd(), "UI/Shockfish.ui")
StockfishPath = os.path.join(os.getcwd(), "Stockfish/stockfish-x86-64")
OutputLogPath = os.path.join(os.getcwd(), "Logs/Latest.log")
SkipIteration = False
ThreadsToKill = []
ChessClient = None
ChessEngine = None
ChessBoard = chess.Board()
ExitCode = 0
GameID = "758151527"
Debug = False


## FUNCTIONS ##
# Get a player's profile information using a Chess.com client and a username
def GetProfileInfo(Client, Username):
    return Client.get_player_profile(Username)

# Search through the player's played games to find the PGN of a specific game given its ID
def GetGamePGN(GameID, Username):
    print(f"[INFO] >> Searching in {Username}'s played games for one with ID {GameID}...")

    for YearArchive in requests.get(ArchivesRequestURL.replace("<USERNAME>", Username), headers=RequestHeaders).json()['archives']:
        for Game in requests.get(YearArchive, headers=RequestHeaders).json()['games']:
            if Game['url'].split("/")[-1] == GameID:
                print(f"[INFO] >> URL of game with ID {GameID} is \"{Game['url']}\".")
                return io.StringIO(Game['pgn'])

    print(f"[ERROR] >> Could not find game with ID {GameID}.")
    return None

def StatsThread(DebugInterval=5.0, InDepthMessages=False, InDepthMessageCount=10):
    print(f"[DEBUG] >> Memory statistics will be printed every {DebugInterval} seconds.")
    time.sleep(1.0)

    ParentProcess = psutil.Process(os.getpid())
    
    while True:
        ParentChildren = ParentProcess.children(recursive=True)
        ChildMem = 0

        print(f"[DEBUG] >> Root program CPU usage: {ParentProcess.cpu_percent()}%")
        print(f"[DEBUG] >> Root program mem usage: {ParentProcess.memory_info().rss / 1024} KB")

        if len(ParentChildren) > 0:
            for Child in ParentChildren:
                print(f"[DEBUG] >> CPU usage of child {Child.pid}: {Child.cpu_percent()}")
                ChildMem += Child.memory_info().rss

            print(f"[DEBUG] >> Mem usage of ({len(ParentChildren)}) child processes: {ChildMem / 1024} KB")

        if InDepthMessages == True:
            for Stat in tracemalloc.take_snapshot().statistics('lineno')[:InDepthMessageCount]:
                print(f"  {Stat}")

            print()

        time.sleep(DebugInterval)


## MAIN CODE ##
if __name__ == "__main__":
    print("[== SHOCKFISH ==]")

    for Arg in sys.argv[1:]:
        ArgIndex = sys.argv.index(Arg)

        if SkipIteration == True:
            SkipIteration = False
            continue

        match Arg:
            case "--Debug":
                Debug = True

            case "--Version":
                print(f"Shockfish {ProgramVersion}")
                sys.exit(-998)

            case "--PiShockURL":
                if ArgIndex > len(sys.argv) - 2 or sys.argv[ArgIndex + 1].startswith("--"):
                    print("[ERROR] >> Argument \"--PiShockURL\" requires a URL.")
                    sys.exit(-997)

                SkipIteration = True
                PiShockManager.ZapManager.PiShockURL = sys.argv[ArgIndex + 1]
                
                print(f"[INFO] >> PiShock URL has been changed to \"{PiShockManager.ZapManager.PiShockURL}\".")

            case "--help" | _:
                print("Available arguments:\n1. --Debug: enables debug mode\n2. --Version: shows the program version and exits\n3. --PiShockURL <url>: sets the API url that Shockfish will try to communicate with\n")
                sys.exit(-999)

    print(f"[INFO] >> Debugging has been set to {Debug}.")
    print(f"[INFO] >> Setting up STDOUT for file output to log file \"{OutputLogPath}\"...")
    sys.stdout = Tee(sys.stdout, open(OutputLogPath, "w"))

    if Debug == True:
        print("[DEBUG] >> Initializing tracemalloc...")
        tracemalloc.start()

        print("[DEBUG] >> Initializing statistics thread...")
        StatsProc = multiprocessing.Process(target=StatsThread, args=(5.0, True))
        ThreadsToKill.append(StatsProc)
        StatsProc.start()
    
    try:
        # Check if stockfish exists on the disk
        print(f"[INFO] >> Checking if stockfish engine exists (\"{StockfishPath}\")...")

        if os.path.exists(StockfishPath) == False or os.path.isfile(StockfishPath) == False:
            raise Exception("Stockfish doesn't exist at the specified path, or it exists but isn't a file.")
            
        print("[INFO] >> Initializing stockfish...")
        ChessEngine = chess.engine.SimpleEngine.popen_uci(StockfishPath)

        # Initialize the Chess.com client and its headers
        print("[INFO] >> Setting up Chess.com client...")
        ChessClient = ChessDotComClient(user_agent = "Shockfish")

        Client.request_config["headers"]["User-Agent"] = (
            "Shockfish"
            "Contact me at xxxmemescoepxxx@gmail.com"
        )

        # Initialize and set up the GUI
        print("[INFO] >> Initializing DearPyGui (IMGUI)...")
        GUI.GUI.InitUI(DefaultWinSize, ProgramVersion, SelectableGameModes, Debug)

        print("[INFO] >> DearPyGui (IMGUI) init finished, mainloop starting...")
        GUI.GUI.Mainloop(Debug)

        """match CurrentGameMode:
            # This mode is selected if the game status should be checked in real time.
            # A shock should be administered if the user makes a bad move or loses a piece.
            # The intensity and/or duration of the shock will be adjusted based on the move's
            # rating or the value of the piece.
            case "Realtime":
                print("[INFO] >> Game mode is Realtime.")
                pass

            # This mode is selected if the game status should be checked after someone wins.
            # It can also be run on any previous game that the user has played.
            # A shock should be administered if the user loses the game
            case "GameOver":
                print("[INFO] >> Game mode is GameOver.")

                # Get the PGN of a specific game and determine who won
                GamePGN = GetGamePGN(GameID, PlayerUsername)
                assert GamePGN != None, f"Invalid game ID {GameID}."

                CRG = chess.pgn.read_game(GamePGN)
                WinReason = CRG.headers['Termination'].split(" ")[3]
                Winner = CRG.headers['Termination'].split(" ")[0]
                UserWon = Winner == PlayerUsername
                
                print(f"[INFO] >> {Winner} won the game, {'NO' if UserWon else 'a'} shock will be administered because {PlayerUsername} {'WON' if UserWon else 'LOST'}.")

            case _:
                print(f"[ERROR] >> Unknown game mode \"{CurrentGameMode}\". Valid options are: {', '.join(SelectableGameModes)}.")"""

    except Exception as EX:
        print(f"[ERROR] >> {EX}")
        traceback.print_exc()
        ExitCode = hex(id(EX))

    print(f"[INFO] >> Stopping threads ands exiting with code {ExitCode}...")

    for Thread in ThreadsToKill:
        Thread.terminate()

    ChessEngine.quit()
    sys.exit(ExitCode)