### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
import traceback
import time
import UI
import os


## CLASSES ##
class SettingsManager:
    ## VARIABLES ##
    SettingsFilePath = os.path.join(os.getcwd(), "Settings.cfg")


    ## FUNCTIONS ##
    def ResetSettings():
        if UI.GUIHelpers.DisplayYesNoPrompt("WARNING - Settings", "This will ERASE ALL of your settings! Are you really sure you want to do that?") == True:
            print(f"[INFO] >> Checking if settings file \"{SettingsManager.SettingsFilePath}\" exists...")            

            try:
                if os.path.exists(SettingsManager.SettingsFilePath):
                    print("[INFO] >> Clear to delete, file exists.")
                    os.remove(SettingsManager.SettingsFilePath)
                
                else:
                    print("[INFO] >> Settings file does not exist.")
                    
                time.sleep(0.1)

                NewMessageBox = UI.MessageBox()
                NewMessageBox.Title = "Information - Settings"
                NewMessageBox.Message = "All settings have been reset."
                NewMessageBox.Buttons = UI.MessageBoxButtons.Close

                UI.GUIHelpers.DisplayMessageBoxObject(NewMessageBox)
                
            except Exception as EX:
                print(f"[ERROR] >> {EX}")
                traceback.print_exc()
                time.sleep(0.1)
                UI.GUIHelpers.DisplayMessageBox("Error - Settings", f"An error occurred while clearing settings: {EX}")