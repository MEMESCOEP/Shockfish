### SHOCKFISH ###
# By MEMESCOEP


## IMPORTS ##
import multiprocessing
import platform
import time
import sys
import os


## VARIABLES ##
LastIMGUICommunication = multiprocessing.Value("d", time.time())
MainViewportIsOpen = multiprocessing.Value("b", False)
DebugStatsInterval = multiprocessing.Value("d", 30.0)
DebugChartInterval = multiprocessing.Value("d", 0.5)
GUIInitFinished = multiprocessing.Value("b", False)
CurrentPlatform = platform.system().lower().replace("linux", "ubuntu").replace("darwin", "macos")
MainProgramPath = os.path.dirname(os.path.abspath(sys.argv[0]))
CurrentCWDPath = sys._MEIPASS if hasattr(sys, "_MEIPASS") and sys._MEIPASS != None else os.getcwd()
StockfishPath = os.path.join(MainProgramPath, "Stockfish/stockfish-x86-64")
SFArchivePath = os.path.join(MainProgramPath, "Stockfish.<ARCHIVE_TYPE>")
StockfishURL = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-<OS>-x86-64.<ARCHIVE_TYPE>"
AllocatedMEM = multiprocessing.Value("d", 0.0)
WindowSize = [750, 440]
BootTime = time.time()
CPUUsage = multiprocessing.Value("d", 0.0)
MEMUsage = multiprocessing.Value("d", 0.0)


## FUNCTIONS ##
# Update the stockfish path based on the current platform
def UpdateStockfishPathFromPlatform(CurrentPlatform):
    global StockfishPath
    
    if CurrentPlatform == "windows":
        print("[INFO] >> Running on windows, updating stockfish path...")
        StockfishPath = StockfishPath.replace("/", "\\") + ".exe"