### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from tkinter.filedialog import askopenfilename
from enum import Enum
import tkinter as Tk
import UI as GUI
import sys
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
    CurrentPGN = ""


    ## FUNCTIONS ##
    def LoadPGNFromFile():
        try:
            # Create the TK window which is necessary to prevent X server request failure errors
            RootTK = Tk.Tk()
            RootTK.withdraw()

            Filename = askopenfilename(title="Open a saved chess game (PGN)", filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")])

            # Check if the cancel button was pressed or the dialog was closed
            if isinstance(Filename, tuple) or len(Filename) <= 0:
                return

            # Double check that the file actually exists            
            if os.path.exists(Filename):
                print(f"[INFO] >> Loading PGN from file \"{Filename}\"...")
                
                try:
                    with open(Filename, 'r') as PGNFile:
                        ChessManager.CurrentPGN = PGNFile.read()

                    print(f"[INFO] >> Finished loading PGN with size of ~{(sys.getsizeof(ChessManager.CurrentPGN) / 1024):.2f} KB.")
                    ChessManager.ParsePGN(ChessManager.CurrentPGN, True)

                except Exception as EX:
                    GUI.GUIHelpers.DisplayMessageBox("Error - Chess Manager", f"Failed to read from or open the PGN file: {EX}")

            else:
                GUI.GUIHelpers.DisplayMessageBox("Error - Chess Manager", f"The PGN file does not exist at the specified path: \"{Filename}\"")

        except Exception as EX:
            GUI.GUIHelpers.DisplayMessageBox("Error - Chess Manager", f"Failure: {EX}")

    # Parse a PGN string to determine the state of the game
    def ParsePGN(PGNString, DisplayMessgae=False):
        print("[INFO] >> Parsing PGN string...")

        if DisplayMessgae == True:
            GUI.GUIHelpers.DisplayMessageBox("Information - Chess Manager", "Parsing PGN data, please be patient...")