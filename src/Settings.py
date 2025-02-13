### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
import traceback
import Globals
import time
import sys
import os


## CLASSES ##
class SettingsManager:
    ## VARIABLES ##
    MODULE_REF_PISHOCKMANAGER = None
    MODULE_REF_IMGUI = None
    MODULE_REF_UI = None
    SettingsFilePath = os.path.join(Globals.MainProgramPath, "Settings.cfg")


    ## FUNCTIONS ##
    def PassReferences(PiShockManager: __module__, IMGUI: __module__, UI: __module__):
        SettingsManager.MODULE_REF_PISHOCKMANAGER = PiShockManager
        SettingsManager.MODULE_REF_IMGUI = IMGUI
        SettingsManager.MODULE_REF_UI = UI

    def LoadSettings(Debug=False):
        SettingsPropertyList = []
        
        if os.path.exists(SettingsManager.SettingsFilePath) == False:
            print(f"[INFO] >> The settings file \"{SettingsManager.SettingsFilePath}\" does not yet exist.")
            return
        
        print(f"[INFO] >> Loading settings from \"{SettingsManager.SettingsFilePath}\"...")

        with open(SettingsManager.SettingsFilePath, 'r') as SettingsFile:
            for Line in SettingsFile.readlines():
                SanitizedLine = Line.replace("\n", "")
                
                if len(SanitizedLine) <= 0 or SanitizedLine.startswith("["):
                    continue

                SettingsPropertyList.append({SanitizedLine.split("=")[0]: SanitizedLine.split("=")[1]})

        for KeyValuePair in SettingsPropertyList:
            for Key, Value in KeyValuePair.items():
                if Debug == True:
                    print(f"[DEBUG] >> Read key value pair {{\"{Key}\" -> \"{Value}\"}}")

                if "Username" in Key:
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{Key.replace("Username", "")}UsernameInput", Value)

                elif Key == "ChessGameURL":
                    SettingsManager.MODULE_REF_IMGUI.set_value("GameURLInput", Value)

                elif Key == "StockfishPath":
                    SettingsManager.MODULE_REF_IMGUI.set_value("StockfishPathInput", Value.replace("<THIS_DIR>", Globals.MainProgramPath).replace("|", Globals.PathSeparator) + (".exe" if sys.platform == "win32" else ""))
                    Globals.StockfishPath = SettingsManager.MODULE_REF_IMGUI.get_value("StockfishPathInput")

                elif "Piece_" in Key:
                    PieceSettings = Value.replace("[", "").replace("]", "").split(", ")
                    PieceName = Key.replace("Piece_", "")

                    assert len(PieceSettings) == 4, f"There needs to be at least four values in \"[Enabled/Disabled, Mode, Intensity, Duration]\" format for setting\"{Key}\"."

                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}EnableCheckbox", PieceSettings[0] == "Enabled")
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}ActionComboBox", PieceSettings[1])
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}IntensityInput", int(PieceSettings[2]))
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}DurationInput", float(PieceSettings[3]))

                elif Key == "APIKey":
                    SettingsManager.MODULE_REF_IMGUI.set_value("PiShockAPIKeyInput", Value)

                elif Key == "Sharecode":
                    SettingsManager.MODULE_REF_IMGUI.set_value("PiShockSharecodeInput", Value)

                else:
                    print(f"[WARN] >> There is no setting named \"{Key}\".")

        print("[INFO] >> Updating PiShock configuration with new settings...")
        SettingsManager.MODULE_REF_PISHOCKMANAGER.ZapManager.SetConfig(
            SettingsManager.MODULE_REF_IMGUI.get_value("PiShockSharecodeInput"),
            SettingsManager.MODULE_REF_IMGUI.get_value("PiShockUsernameInput"),
            SettingsManager.MODULE_REF_IMGUI.get_value("PiShockAPIKeyInput")
        )

    def SaveSettings(Debug=False):
        print(f"[INFO] >> Saving settings to file \"{SettingsManager.SettingsFilePath}\"...")

        with open(SettingsManager.SettingsFilePath, 'w') as SettingsFile:
            SettingsFile.write("[CHESS]\n")
            SettingsFile.write(f"ChessUsername={SettingsManager.MODULE_REF_IMGUI.get_value("ChessUsernameInput")}\n")
            SettingsFile.write(f"ChessGameURL={SettingsManager.MODULE_REF_IMGUI.get_value("GameURLInput")}\n")
            SettingsFile.write(f"StockfishPath={os.path.splitext(SettingsManager.MODULE_REF_IMGUI.get_value("StockfishPathInput").replace(Globals.MainProgramPath, "<THIS_DIR>").replace(Globals.PathSeparator, "|"))[0]}\n")

            for PieceName in ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]:
                    EnabledDisabled = "Enabled" if SettingsManager.MODULE_REF_IMGUI.get_value(f"{PieceName}EnableCheckbox") == True else "Disabled"
                    SettingsFile.write(f"Piece_{PieceName}=[{EnabledDisabled}, {SettingsManager.MODULE_REF_IMGUI.get_value(f"{PieceName}ActionComboBox")}, {SettingsManager.MODULE_REF_IMGUI.get_value(f"{PieceName}IntensityInput")}, {SettingsManager.MODULE_REF_IMGUI.get_value(f"{PieceName}DurationInput")}]\n")

            SettingsFile.write("\n[PISHOCK]\n")
            SettingsFile.write(f"PiShockUsername={SettingsManager.MODULE_REF_IMGUI.get_value("PiShockUsernameInput")}\n")
            SettingsFile.write(f"Sharecode={SettingsManager.MODULE_REF_IMGUI.get_value("PiShockSharecodeInput")}\n")
            SettingsFile.write(f"APIKey={SettingsManager.MODULE_REF_IMGUI.get_value("PiShockAPIKeyInput")}")

    def ResetSettings():
        if SettingsManager.MODULE_REF_UI.GUIHelpers.DisplayYesNoPrompt("WARNING - Settings", "This will ERASE ALL of your settings! Are you really sure you want to do that?") == True:
            print(f"[INFO] >> Checking if settings file \"{SettingsManager.SettingsFilePath}\" exists...")            

            try:
                SettingsManager.MODULE_REF_IMGUI.set_value("StockfishPathInput", "<THIS_DIR>|Stockfish|stockfish-x86-64".replace("<THIS_DIR>", Globals.MainProgramPath).replace("|", Globals.PathSeparator) + (".exe" if sys.platform == "win32" else ""))
                SettingsManager.MODULE_REF_IMGUI.set_value("ChessUsernameInput", "")
                SettingsManager.MODULE_REF_IMGUI.set_value("PiShockUsernameInput", "")
                SettingsManager.MODULE_REF_IMGUI.set_value("GameURLInput", "")
                SettingsManager.MODULE_REF_IMGUI.set_value("PiShockAPIKeyInput", "")
                SettingsManager.MODULE_REF_IMGUI.set_value("PiShockSharecodeInput", "")

                for PieceName in ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]:
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}EnableCheckbox", True)
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}ActionComboBox", "Shock")
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}IntensityInput", 1)
                    SettingsManager.MODULE_REF_IMGUI.set_value(f"{PieceName}DurationInput", 0.1)
                    
                time.sleep(0.1)

                NewMessageBox = SettingsManager.MODULE_REF_UI.MessageBox()
                NewMessageBox.Title = "Information - Settings"
                NewMessageBox.Message = "All settings have been reset."
                NewMessageBox.Buttons = SettingsManager.MODULE_REF_UI.MessageBoxButtons.Close

                SettingsManager.MODULE_REF_UI.GUIHelpers.DisplayMessageBoxObject(NewMessageBox)
                
            except Exception as EX:
                print(f"[ERROR] >> {EX}")
                traceback.print_exc()
                time.sleep(0.1)
                SettingsManager.MODULE_REF_UI.GUIHelpers.DisplayMessageBox("Error - Settings", f"An error occurred while clearing settings: {EX}")