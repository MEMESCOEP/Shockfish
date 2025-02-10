### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from chessdotcom import ChessDotComClient, Client, get_player_game_archives
from zipfile import ZipFile
from enum import Enum
import dearpygui.dearpygui as IMGUI
import multiprocessing
import traceback
import requests
import Globals
import tarfile
import chess.engine
import chess.pgn
import time
import sys
import UI
import io
import os


## CLASSES ##
class ChessPieces(Enum):
    Bishop = 3
    Knight = 3
    Queen = 9
    King = 10
    Pawn = 1
    Rook = 5

class ChessManager:
    ## VARIABLES ##
    BoardPieceLocations = []
    CurrentBoardState = []
    DefaultBoardState = []
    ChessPieceColors = ["White", "Black"]
    ScoreThresholds = [75, -75, -150] # Good, bad, terrible. Neutral will be seen as anything between good and bad
    BoardPosNames = [
        ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'],
        ['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2'],
        ['A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3'],
        ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4'],
        ['A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5'],
        ['A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6'],
        ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7'],
        ['A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8'],
    ]

    AnalysisThreadMultiplier = 1.5
    AnalysisThreadCount = int(multiprocessing.cpu_count() * AnalysisThreadMultiplier)
    AnalysisDepthLimit = 10
    AnalyseTimeLimit = 0.1
    ChessClient = None
    ChessEngine = None
    ChessBoard = chess.Board()
    CurrentPGN = ""
    EngineData = ["Unknown", "Unknown"]


    ## FUNCTIONS ##
    def Init(Debug=True):
        CurrentColor = 1

        # Initialize the Chess.com client and its headers
        print("[INFO] >> Setting up Chess.com client...")
        ChessManager.ChessClient = ChessDotComClient(user_agent = "Shockfish")

        # Set up the Chess.com client's request headers (required for requests to work)
        Client.request_config["headers"]["User-Agent"] = (
            "Shockfish"
            "Contact me at xxxmemescoepxxx@gmail.com"
        )

        # Check if Stockfish exists on the disk
        if ChessManager.DoesStockfishExist(Globals.StockfishPath) == False:
            print(f"[ERROR] >> Failed to find Stockfish at \"{Globals.StockfishPath}\".")
            NewMessageBox = UI.MessageBox()
            NewMessageBox.Title = "Error - Chess manager"
            NewMessageBox.Message = f"Stockfish wasn't found at \"{Globals.StockfishPath}\".\n\nWould you like to download the latest stockfish release now?"
            NewMessageBox.Buttons = UI.MessageBoxButtons.YesNo
            NewMessageBox.Actions[False] = lambda: (_ for _ in ()).throw(FileNotFoundError("Stockfish doesn't exist at the specified path, or it exists but isn't a file."))

            UI.GUIHelpers.DisplayMessageBoxObject(NewMessageBox, ForceRender=True)

            # The download should happen in this thread, we can't use a messagebox action for that
            with IMGUI.window(label="Downloading and extracting stockfish...", tag="DLEWindow", pos=((IMGUI.get_viewport_width() / 2) - 160, (IMGUI.get_viewport_height() / 2) - 50), width=320, height=50, no_close=True, no_collapse=True, no_move=True, no_resize=True):
                IMGUI.add_text("Please wait while stockfish is downloaded and\nextracted, it shouldn't take too long..")
                IMGUI.add_progress_bar(tag="DLEProgressBar", overlay="0%", default_value=0.0, width=-1)
            
            IMGUI.render_dearpygui_frame()
            
            ArchiveType = "zip" if Globals.CurrentPlatform == "windows" else "tar"
            DownloadURL = Globals.StockfishURL.replace("<ARCHIVE_TYPE>", ArchiveType).replace("<OS>", Globals.CurrentPlatform)
            ArchivePath = Globals.SFArchivePath.replace("<ARCHIVE_TYPE>", ArchiveType)
            OldEXEName = DownloadURL.split("/")[-1].split(".")[0] + (".exe" if Globals.CurrentPlatform == "windows" else "")
            
            print(f"[INFO] >> Downloading stockfish from \"{DownloadURL}\", to file \"{ArchivePath}\"...")
            with requests.get(DownloadURL, stream=True) as response:
                if response.status_code == 200:
                    ArchiveSize = int(response.headers.get('Content-Length', 0))
                    Downloaded = 0
                    Progress = 0

                    with open(ArchivePath, 'wb') as ArchiveFile:
                        for Chunk in response.iter_content(chunk_size=1024):
                            if Chunk:
                                ArchiveFile.write(Chunk)
                                Downloaded += len(Chunk)
                                Progress = round((Downloaded / ArchiveSize) * 100, 2)

                                IMGUI.set_value("DLEProgressBar", Progress / 100)
                                IMGUI.configure_item("DLEProgressBar", overlay=f"Downloading ({Progress}%)")
                                IMGUI.focus_item("DLEWindow")

                                if Progress % 0.5 == 0:
                                    IMGUI.render_dearpygui_frame()

            if Globals.CurrentPlatform == "windows":
                with ZipFile(ArchivePath, 'r') as ArchiveFile:
                    FilesToExtract = ArchiveFile.namelist()
                    ExtractedCount = 0
                    ExtractPath = os.path.dirname(Globals.StockfishPath)
                    FileInZIP = ""
                    FileCount = len(FilesToExtract)

                    print(f"[INFO] >> Extracting {FileCount} file(s) to \"{ExtractPath}\"...")

                    for File in FilesToExtract:
                        if File.endswith('/'):
                            continue

                        if File.startswith('stockfish/'):
                            FileInZIP = File[len('stockfish/'):]

                        else:
                            FileInZIP = File

                        ExtractedFilePath = os.path.join(ExtractPath, FileInZIP)
                        os.makedirs(os.path.dirname(ExtractedFilePath.capitalize()), exist_ok=True)

                        with ArchiveFile.open(File) as OpFile:
                            with open(ExtractedFilePath, 'wb') as OutFile:
                                OutFile.write(OpFile.read())

                        ExtractedCount += 1
                        Progress = round((ExtractedCount / FileCount) * 100, 2)

                        IMGUI.set_value("DLEProgressBar", Progress / 100)
                        IMGUI.configure_item("DLEProgressBar", overlay=f"Extracting ({Progress}%)")
                        IMGUI.focus_item("DLEWindow")
                        IMGUI.render_dearpygui_frame()

            else:
                with tarfile.open(ArchivePath, 'r') as ArchiveFile:
                    FilesToExtract = ArchiveFile.getmembers()
                    ExtractedCount = 0
                    ExtractPath = os.path.dirname(Globals.StockfishPath)
                    FileCount = len(FilesToExtract)

                    print(f"[INFO] >> Extracting {FileCount} file(s) to \"{ExtractPath}\"...")

                    for File in FilesToExtract:
                        ArchiveFile.extract(File, path=".")

                        ExtractedCount += 1
                        Progress = round((ExtractedCount / FileCount) * 100, 2)

                        IMGUI.set_value("DLEProgressBar", Progress / 100)
                        IMGUI.configure_item("DLEProgressBar", overlay=f"Extracting ({Progress}%)")
                        IMGUI.focus_item("DLEWindow")
                        IMGUI.render_dearpygui_frame()

                os.rename("stockfish", "Stockfish")

            os.rename(f"Stockfish/{OldEXEName}", f"Stockfish/{OldEXEName.replace('-' + Globals.CurrentPlatform, '')}")            
            os.remove(ArchivePath)
            IMGUI.delete_item("DLEWindow")

        print("[INFO] >> Initializing stockfish...")
        print(f"[INFO] >> Chess engine board analysis can take a maximum of {ChessManager.AnalyseTimeLimit} seconds, has a max depth of {ChessManager.AnalysisDepthLimit}, and will use {ChessManager.AnalysisThreadCount} thread(s).")
        ChessManager.ChessEngine = chess.engine.SimpleEngine.popen_uci(Globals.StockfishPath)
        ChessManager.ChessEngine.configure({"Threads": ChessManager.AnalysisThreadCount})
        ChessManager.ChessEngine.configure({"Hash": 8})
        ChessManager.EngineData = [ChessManager.ChessEngine.id['name'], chess.__version__, chess.__spec__]

        for Y in range(8):
            PieceColorIndex = 0 if Y > 4 else 1
            CurrentColor = not CurrentColor
            
            for X in range(8):
                CurrentColor = not CurrentColor

                if Y == 1 or Y == 6:
                    ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}Pawn", "Pos": ChessManager.BoardPosNames[Y][X]})

                elif Y == 0 or Y == 7:
                    if X == 0 or X == 7:
                        ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}Rook", "Pos": ChessManager.BoardPosNames[Y][X]})

                    elif X == 1 or X == 6:
                        ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}Knight", "Pos": ChessManager.BoardPosNames[Y][X]})

                    elif X == 2 or X == 5:
                        ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}Bishop", "Pos": ChessManager.BoardPosNames[Y][X]})

                    elif X == 3:
                        ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}Queen", "Pos": ChessManager.BoardPosNames[Y][X]})

                    elif X == 4:
                        ChessManager.DefaultBoardState.append({"Piece": f"{ChessManager.ChessPieceColors[PieceColorIndex]}King", "Pos": ChessManager.BoardPosNames[Y][X]})

    # Check if Stockfish exists on the disk
    def DoesStockfishExist(StockfishPath):
        print(f"[INFO] >> Checking if stockfish engine exists at path \"{StockfishPath}\"...")

        return os.path.exists(StockfishPath) and os.path.isfile(StockfishPath)
    
    # Load a game fro ma PGN file. Call this function as a callback of a button
    def UILoadPGN(Debug=False):
        NewFileDialog = UI.FileDialog(Title="Open PGN File", ValidExstensions=[{'label': 'All files', 'formats': ['*']}, {'label': 'PGN files', 'formats': ['pgn']}], DefaultExtension=1)
        NewFileDialog.FileSelectedAction = ChessManager.LoadPGNFromFile
        NewFileDialog.PassDebug = Debug
        NewFileDialog.Show()

    # Load game data from a PGN file
    def LoadPGNFromFile(Filename, Debug=False):
        try:
            # Double check that the file actually exists
            print(f"[INFO] >> Loading PGN from file \"{Filename}\"...")
            with open(Filename, 'r') as PGNFile:
                ChessManager.CurrentPGN = PGNFile.read()

            print(f"[INFO] >> Finished loading PGN with size of ~{(sys.getsizeof(ChessManager.CurrentPGN) / 1024):.2f} KB, clear to begin parsing.")
            ChessManager.ParsePGN(ChessManager.CurrentPGN, Debug)

        except Exception as EX:
            UI.GUIHelpers.DisplayMessageBox("Error - Chess Manager", f"Failed to open the PGN file: {EX}")

            if Debug == True:
                traceback.print_exc()

    # Determine the quality of a move based on its CP score.
    # Color should be -1 for white and 1 for black
    # Returns "Good", "Neutral", "Bad", or "Terrible"
    def GetQualityOfMove(Color, PreviousCPScore, CurrentCPScore, Debug=False):
        ScoreDifference = Color * (CurrentCPScore - PreviousCPScore)

        if Debug == True:
            print(f"[DEBUG] >> Move evaluation: {Color} * ({CurrentCPScore} - {PreviousCPScore}) = {ScoreDifference}")

        if ScoreDifference >= ChessManager.ScoreThresholds[0]:
            return "Good"
        
        elif ScoreDifference > ChessManager.ScoreThresholds[1] and ScoreDifference < ChessManager.ScoreThresholds[0]:
            return "Neutral"
        
        elif ScoreDifference <= ChessManager.ScoreThresholds[2]:
            return "Terrible"
        
        elif ScoreDifference <= ChessManager.ScoreThresholds[1]:
            return "Bad"

    # Parse a PGN string to determine the state of the game
    def ParsePGN(PGNString, Debug=False):
        print("[INFO] >> Parsing PGN string...")

        with IMGUI.window(label="Parsing PGN string...", tag="PGNWindow", width=320, height=50, pos=((IMGUI.get_viewport_width() / 2) - 160, (IMGUI.get_viewport_height() / 2) - 50), no_move=True, no_resize=True, no_close=True, no_collapse=True):
            IMGUI.add_text("Please wait while the PGN string is parsed, it\nshouldn't take too long...")
            IMGUI.add_progress_bar(tag="PGNProgressBar", default_value=0.0, width=-1)

        if PGNString == None or len(PGNString) <= 0:
            if Debug == True:
                print("[DEBUG] >> PGN string is null or empty.")

            ChessManager.CurrentBoardState = ChessManager.DefaultBoardState
            return
        
        else:
            if Debug == True:
                print("[DEBUG] >> Clearing move list, resetting chess board, and clearing current board state...")

            try:
                UI.GUI.MoveList.clear()
                ChessManager.ChessBoard.reset()
                ChessManager.CurrentBoardState.clear()

                PGNIO = io.StringIO(PGNString)
                Game = chess.pgn.read_game(PGNIO)

                if Debug == True:
                    print(f"[DEBUG] >> PGN headers: {Game.headers}")

                PreviousWhiteScore = 0
                PreviousBlackScore = 0
                CurrentWhiteScore = 0
                CurrentBlackScore = 0
                PositionsChecked = 0
                MoveQuality = "Neutral"
                MoveNumber = 0
                MoveCount = len(list(Game.mainline_moves()))

                if Debug == True:
                    print(f"[DEBUG] >> There are {MoveCount} move(s) to process.")

                for Move in Game.mainline_moves():
                    MoveNumber += 1

                    if Move in ChessManager.ChessBoard.legal_moves:
                        if Debug == True:
                            print(f"[DEBUG] >> Processing move \"{Move}\"...")

                        CurrentDepth = min(min(ChessManager.AnalysisDepthLimit, PositionsChecked // (MoveCount // ChessManager.AnalysisDepthLimit)), ChessManager.AnalysisDepthLimit)
                        Piece = ChessManager.ChessBoard.piece_at(Move.from_square)
                        
                        ChessManager.ChessBoard.push(Move)
                        
                        if Debug == True:
                            print(f"[DEBUG] >> Analyzing board (DEPTH={CurrentDepth})...")

                        BoardAnalysis = ChessManager.ChessEngine.analyse(ChessManager.ChessBoard, chess.engine.Limit(time=ChessManager.AnalyseTimeLimit, depth=CurrentDepth))
                        CurrentWhiteScore = BoardAnalysis['score'].white().score()
                        CurrentBlackScore = BoardAnalysis['score'].black().score()

                        if BoardAnalysis['score'].is_mate() == False and CurrentWhiteScore != None and CurrentBlackScore != None:
                            if Piece.color == 0:
                                MoveQuality = ChessManager.GetQualityOfMove(-1, CurrentWhiteScore, PreviousWhiteScore, Debug)

                            else:
                                MoveQuality = ChessManager.GetQualityOfMove(1, CurrentBlackScore, PreviousBlackScore, Debug)

                        else:
                            MoveQuality = "Neutral"

                        UI.GUI.MoveList.append({
                            "MoveNumber": str(MoveNumber),
                            "Color": ChessManager.ChessPieceColors[not Piece.color],
                            "Player": Game.headers.get(ChessManager.ChessPieceColors[not Piece.color], "Unknown"),
                            "FromPos": chess.square_name(Move.from_square).capitalize(),
                            "ToPos": chess.square_name(Move.to_square).capitalize(),
                            "Quality": MoveQuality
                        })

                        if Debug == True:
                            print(f"[DEBUG] >> {ChessManager.ChessPieceColors[not Piece.color]} piece moved from \"{chess.square_name(Move.from_square).capitalize()}\" to \"{chess.square_name(Move.to_square).capitalize()}\", by \"{Game.headers.get(ChessManager.ChessPieceColors[not Piece.color], "Unknown")}\".")
                            print(f"[DEBUG] >> Analysis result: {BoardAnalysis}")

                    else:
                        print(f"[ERROR] >> Skipping illegal move \"{Move}\"...")

                    PositionsChecked += 1
                    Progress = round((PositionsChecked / MoveCount) * 100, 2)

                    if BoardAnalysis['score'].is_mate() == False and CurrentWhiteScore != None and CurrentBlackScore != None:
                        PreviousWhiteScore = CurrentWhiteScore
                        PreviousBlackScore = CurrentBlackScore

                    else:
                        PreviousWhiteScore = 0
                        PreviousBlackScore = 0

                    IMGUI.focus_item("PGNWindow")
                    IMGUI.set_value("PGNProgressBar", (Progress / 100) * 0.5)
                    IMGUI.configure_item("PGNProgressBar", overlay=f"{round(Progress * 0.5, 2)}%")
                    
                PositionsChecked = 0

                for Row in range(8):
                    for Column in range(8):
                        PieceIndex = 8 * Row + (7 - Column)

                        if Debug == True:
                            print(f"[DEBUG] >> Finding piece at board position {PieceIndex} ([{Row}, {Column}], {round((PositionsChecked / 63) * 100, 2)}% complete)...")

                        Piece = ChessManager.ChessBoard.piece_at(PieceIndex)
                        
                        if Piece != None:
                            if Debug == True:
                                print(f"[DEBUG] >> {ChessManager.ChessPieceColors[not Piece.color]}{chess.piece_name(Piece.piece_type).capitalize()} is at position \"{ChessManager.BoardPosNames[Row][Column]}\".")

                            ChessManager.CurrentBoardState.append({
                                "Piece": f"{ChessManager.ChessPieceColors[not Piece.color]}{chess.piece_name(Piece.piece_type).capitalize()}", 
                                "Pos": ChessManager.BoardPosNames[Row][Column]
                            })

                        elif Debug == True:
                            print(f"[DEBUG] >> No piece is at board position {PieceIndex}.")

                        PositionsChecked += 1
                        Progress = round((PositionsChecked / MoveCount) * 100, 2)

                        IMGUI.focus_item("PGNWindow")
                        IMGUI.set_value("PGNProgressBar", ((Progress / 100) * 0.5) + 50)
                        IMGUI.configure_item("PGNProgressBar", overlay=f"{round((Progress * 0.5) + 50, 2)}%")

                UI.GUI.MovesUpdated = True

            except Exception as EX:
                print(f"[ERROR] >> {EX}")

                if Debug == True:
                    traceback.print_exc()

                ErrorMessageBox = UI.MessageBox()
                ErrorMessageBox.Buttons = UI.MessageBoxButtons.Close
                ErrorMessageBox.Title = "Error - Chess Manager"
                ErrorMessageBox.Message = f"Failed to parse PGN data:\n\n{EX}"
                ErrorMessageBox.MessageBoxShown = False

                UI.GUI.MessageBoxes.append(ErrorMessageBox)
            
            IMGUI.set_value("PGNProgressBar", 1.0)
            IMGUI.configure_item("PGNProgressBar", overlay="100%")
            time.sleep(0.25)
            IMGUI.delete_item("PGNWindow")        