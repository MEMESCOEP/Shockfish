### SHOCKFISH ###
# By MEMESCOEP


## IMPORTS ##
import dearpygui.dearpygui as IMGUI
import PiShockManager
import multiprocessing
import ChessManager
import faulthandler
import tracemalloc
import traceback
import datetime
import requests
import Globals
import pishock
import psutil
import signal
import chess
import time
import sys
import UI
import io
import os


## CLASSES ##
class Tee:
    def __init__(Self, *FileObjects):
        Self.file_objects = FileObjects

    def write(Self, Message):
        try:
            for File in Self.file_objects:
                # Check if the message should be written to the console or to a file
                if File is sys.stdout:
                    if IsConsoleAvailable == True:
                        sys.__stdout__.write(Message)

                else:
                    File.write(Message)
                    Self.flush()

        except:
            pass

    def flush(Self):
        try:
            sys.__stdout__.flush()

            for File in Self.file_objects:
                File.flush()

        except:
            pass


## VARIABLES ##
SelectableGameModes = ["Realtime", "GameOver"]
RealtimeRequestURL = "https://api.chess.com/pub/player/<USERNAME>/games"
ArchivesRequestURL = f"{RealtimeRequestURL}/archives"
IsConsoleAvailable = sys.stdout.isatty()
ShockersToControl = 1
CurrentGameMode = SelectableGameModes[1]
RequestHeaders = {"User-Agent": "Shockfish/1.0"}
PlayerUsername = "memescoep"
ProgramVersion = "0.1"
OutputLogPath = os.path.join(Globals.MainProgramPath, f"Logs/{datetime.datetime.now().strftime("%m-%d-%Y_%I-%M-%S-%p")}.log")
SkipIteration = False
ThreadsToKill = []
ExitCode = 0
GameID = "758151527"
Debug = False


## FUNCTIONS ##
def QuitApplication(ExitCode = 0):
    if ExitCode == -11:
        sys.exit(ExitCode)

    print(f"[INFO] >> Stopping threads ands exiting with code {ExitCode}...")

    if ChessManager.ChessManager.ChessEngine != None:
        ChessManager.ChessManager.ChessEngine.quit()

    for Thread in ThreadsToKill:
        if Thread == None or isinstance(Thread, multiprocessing.Process) == False:
            print(f"[ERROR] >> Object \"{Thread}\" is not of type \"multiprocessing.Process\", this may lead to threads that don't exit!")
            continue

        Thread.terminate()
        
    sys.stdout.flush()
    sys.exit(ExitCode)

def OSSignalHandler(Signal, Frame):
    print(f"[INFO] >> Received OS signal {Signal} in frame \"{Frame}\"")
    
    Quit = False

    match Signal:
        case 2:
            print("[INFO] >> OS signal is \"SIGINT\", quitting...")
            Quit = True

        case 11:
            print("[INFO] >> OS signal is \"SIGSEGV\", this is a critical error!")
            Quit = True

        case _:
            print("[INFO] >> OS signal is \"UNKNOWN\".")
    
    if Quit == True:
        QuitApplication(Signal)

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

# Log debugging statistics to the console and the log file
def StatsThread(LogFilePath, DebugInterval=5.0, InDepthMessages=False, InDepthMessageCount=10, IMGUITimeout=5.0, LogFlushInterval=2.0):
    print(f"[DEBUG] >> Debug statistics will be printed every {DebugInterval} seconds.")

    while Globals.GUIInitFinished.value == False:
        time.sleep(0.1)

    try:
        print("[DEBUG] >> Getting parent process...")

        ParentProcess = psutil.Process(os.getpid())
        
        print(f"[DEBUG] >> Parent process \"{ParentProcess.name()}\" PID is {ParentProcess.pid}. Clear to enter stats loop.")

        with open(LogFilePath, "a") as LogFile:
            LastFlushTime = time.time()
            LastPrintTime = time.time()

            while True:
                CurrentTime = time.time()
                CPUUsage = ParentProcess.cpu_percent(interval=None)
                MEMUsage = ParentProcess.memory_info().rss / 1024

                if Globals.MainViewportIsOpen.value == True and CurrentTime - Globals.LastIMGUICommunication.value >= IMGUITimeout:
                    print("[DEBUG] >> Stats loop will now exit because IMGUI didn't send an update, it may not running.")
                    break

                if CurrentTime - LastFlushTime >= LogFlushInterval:
                    LastFlushTime = CurrentTime
                    LogFile.flush()

                if CurrentTime - LastPrintTime >= DebugInterval:
                    LastPrintTime = CurrentTime

                    try:
                        ParentChildren = ParentProcess.children(recursive=True)
                        ChildMem = 0

                        print(f"<=====[ DEBUG STATS AT {datetime.datetime.now()} ]=====>")
                        print(f"[DEBUG] >> Root program CPU usage: {CPUUsage}%")
                        print(f"[DEBUG] >> Root program mem usage: {MEMUsage} KB")
                        print(f"[DEBUG] >> GUI responded within {round(IMGUITimeout - (CurrentTime - Globals.LastIMGUICommunication.value), 3)}s of the {IMGUITimeout}s timeout window.\n  Current time: {CurrentTime} || GUI Response time: {Globals.LastIMGUICommunication.value}\n\n[DEBUG] >> Memory stats:")
                        
                        if len(ParentChildren) > 0:
                            for Child in ParentChildren:
                                print(f"[DEBUG] >> CPU usage of child {Child.pid}: {Child.cpu_percent()}")
                                ChildMem += Child.memory_info().rss

                            print(f"[DEBUG] >> Mem usage of ({len(ParentChildren)}) child processes: {ChildMem / 1024} KB")
                            
                        if InDepthMessages == True:
                            SnapStats = tracemalloc.take_snapshot().statistics('lineno')[:InDepthMessageCount]

                            for Stat in SnapStats:
                                print(f"  {Stat}")

                            print()
                            
                    except Exception as EX:
                        print(f"[ERROR] >> {EX}")
                        traceback.print_exc()

                Globals.AllocatedMEM.value = ParentProcess.memory_info().vms / 1024
                Globals.CPUUsage.value = CPUUsage
                Globals.MEMUsage.value = MEMUsage
                time.sleep(0.05)

    except Exception as EX:
        print(f"[ERROR] >> {EX}")
        traceback.print_exc()

def trace_calls(frame, event, arg):
    try:
        # This function will be called on every event
        if event == "call":
            print(f"Calling function: {frame.f_code.co_name}")

        elif event == "line":
            print(f"Executing line {frame.f_lineno}")

        elif event == "return":
            print(f"Returning from function: {frame.f_code.co_name} with value: {arg}")

    except Exception as EX:
        print(f"[ERROR] >> {EX}")
        traceback.print_exc()

    return trace_calls


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

            case "--DebugStatsInterval":
                if ArgIndex > len(sys.argv) - 2 or sys.argv[ArgIndex + 1].startswith("--") or sys.argv[ArgIndex + 1].replace('.','',1).isdigit() == False:
                    print("[ERROR] >> Argument \"--DebugStatsInterval\" requires a decimal value.")
                    sys.exit(-996)

                SkipIteration = True
                Globals.DebugStatsInterval.value = float(sys.argv[ArgIndex + 1])

            case "--Help" | _:
                print("Available arguments:\n1. --Debug: enables debug mode\n2. --Version: shows the program version and exits\n3. --PiShockURL <url>: sets the API url that Shockfish will try to communicate with\n4. --DebugStatsInterval <integer, 0.001, infinity>: Sets the interval at which debug statistics are printed\n")
                sys.exit(-995)

    print(f"[INFO] >> Debugging has been set to {Debug}.")
    print(f"[INFO] >> Setting up STDOUT for text output to both the console and log file \"{OutputLogPath}\"...")
    LogDir = os.path.dirname(OutputLogPath)

    if os.path.exists(LogDir) == False:
        print(f"[INFO] >> Log directory \"{LogDir}\" doesn't yet exist, it will be created now...")
        os.mkdir(LogDir)

    with open(OutputLogPath, "w") as File:
        File.write(f"<=====[ SHOCKFISH {ProgramVersion} LOG {datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")} ]=====>\n")
        File.close()

    sys.stdout = Tee(sys.stdout, open(OutputLogPath, "a"))

    print("[INFO] >> Enabling program code tracing...")
    #sys.settrace(trace_calls)

    print("[INFO] >> Setting up signal handlers (SIGSEGV, SIGINT)...")
    #faulthandler.enable(all_threads=True)
    #signal.signal(signal.SIGSEGV, OSSignalHandler)
    signal.signal(signal.SIGINT, OSSignalHandler)

    # sys._MEIPASS is only created whith pyinstaller, not Nuitka
    if hasattr(sys, "_MEIPASS"):
        print(f"[INFO] >> sys._MEIPASS exists: \"{sys._MEIPASS}\"")
        print("[INFO] >> sys._MEIPASS exists, so pyi_splash will be imported.")
        import pyi_splash

    print(f"[INFO] >> Current CWD: \"{Globals.CurrentCWDPath}\"")
    print(f"[INFO] >> Executable: \"{sys.argv[0]}\"")

    if Debug == True:
        print("[DEBUG] >> Initializing tracemalloc...")
        tracemalloc.start()

        print("[DEBUG] >> Initializing statistics thread...")
        StatsProc = multiprocessing.Process(target=StatsThread, args=(OutputLogPath, Globals.DebugStatsInterval.value, True))
        ThreadsToKill.append(StatsProc)
        StatsProc.start()
    
    try:
        # Initialize and set up the GUI
        print("[INFO] >> Initializing DearPyGui (IMGUI)...")
        UI.GUI.InitUI(Globals.WindowSize, ProgramVersion, SelectableGameModes, Debug)
        IMGUI.render_dearpygui_frame()
        
        if hasattr(sys, "_MEIPASS"):
            pyi_splash.close()

        # Initialize the chess manager
        ChessManager.ChessManager.Init(Debug)

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
            # A shock should be administered if the user loses the game. Note that this mode
            # ONLY works with daily games.
            case "GameOver":
                print("[INFO] >> Game mode is GameOver.")

                # Get the PGN of a specific game and determine who won
                GamePGN = GetGamePGN(GameID, PlayerUsername)
                assert GamePGN != None, f"Invalid game ID {GameID}."

                with open("TestGame.pgn", "w") as PGNFile:
                    PGNFile.write(GamePGN.getvalue())

                CRG = chess.pgn.read_game(GamePGN)
                WinReason = CRG.headers['Termination'].split(" ")[3]
                Winner = CRG.headers['Termination'].split(" ")[0]
                UserWon = Winner == PlayerUsername
                
                print(f"[INFO] >> {Winner} won the game, {'NO' if UserWon == True else 'a'} shock will be administered because {PlayerUsername} {'WON' if UserWon else 'LOST'}.")

            case _:
                print(f"[ERROR] >> Unknown game mode \"{CurrentGameMode}\". Valid options are: {', '.join(SelectableGameModes)}.")"""

        print("[INFO] >> DearPyGui (IMGUI) init finished, mainloop starting...")
        IMGUI.render_dearpygui_frame()
        UI.GUI.Mainloop(Debug)

    except KeyboardInterrupt:
        print(f"[INFO] >> Keyboard interrupt received, Shockfish will now exit.")
        ExitCode = -999

    except Exception as EX:
        print(f"[ERROR] >> {EX}")
        traceback.print_exc()

        ExitCode = hex(id(EX))

    QuitApplication(ExitCode)