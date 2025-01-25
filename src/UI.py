### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
import dearpygui.dearpygui as IMGUI
import Settings as SettingsManager
import ChessManager
import webbrowser
import time
import os


## CLASSES ##
class GUIHelpers:
    ## FUNCTIONS ##
    # Create a button that acts as a clickable link. This will open a URL in the default web browser.
    def DisplayButtonHyperlink(Text, Address):
        HLButton = IMGUI.add_button(label=Text, callback=lambda:webbrowser.open(Address))
        IMGUI.bind_item_theme(HLButton, "__demo_hyperlinkTheme")

    # Create a settings option for 
    def CreatePieceDropdown(PieceName, PointValue):
        if type(PointValue) == int:
            PointStr = f"{PointValue} point{'s' if PointValue != 1 else ''}"

        else:
            PointStr = PointValue

        with IMGUI.collapsing_header(label=f"{PieceName} ({PointStr})", indent=12):
            IMGUI.add_checkbox(label="Enable shocker control for this piece", tag=f"{PieceName}EnableCheckbox", default_value=True, indent=12)

            with IMGUI.group(tag=f"{PieceName}Properties"):
                IMGUI.add_combo(items=["Shock", "Vibrate"], default_value="Vibrate", width=-1, tag=f"{PieceName}ActionComboBox", indent=12)

                with IMGUI.group(horizontal=True, indent=12):
                    IMGUI.add_text("Intensity: ")
                    IMGUI.add_slider_int(default_value=5, min_value=1, max_value=100, format="%d%%", tag=f"{PieceName}IntensityInput")
                    IMGUI.add_button(label="-", repeat=True, width=24, callback=lambda: IMGUI.set_value(f"{PieceName}IntensityInput", IMGUI.get_value(f"{PieceName}IntensityInput") - 1))
                    IMGUI.add_button(label="+", repeat=True, width=24, callback=lambda: IMGUI.set_value(f"{PieceName}IntensityInput", IMGUI.get_value(f"{PieceName}IntensityInput") + 1))

                with IMGUI.group(horizontal=True, indent=12):
                    IMGUI.add_text("Duration (S): ")
                    IMGUI.add_slider_float(default_value=0.5, min_value=0.1, max_value=15, format="%.1f second(s)", tag=f"{PieceName}DurationInput")
                    IMGUI.add_button(label="-", repeat=True, width=24, callback=lambda: IMGUI.set_value(f"{PieceName}DurationInput", IMGUI.get_value(f"{PieceName}DurationInput") - 0.1))
                    IMGUI.add_button(label="+", repeat=True, width=24, callback=lambda: IMGUI.set_value(f"{PieceName}DurationInput", IMGUI.get_value(f"{PieceName}DurationInput") + 0.1))

            IMGUI.add_spacer()
            IMGUI.add_spacer()

    # Show and hide an element with a boolean. True shows, and False hfilenamedes.
    def ShowHideItemWithBoolean(ShowHide, ItemName):
        if ShowHide == True:
            IMGUI.show_item(ItemName)

        else:
            IMGUI.hide_item(ItemName)

    # Display a messagebox window in the middle of the main viewport
    def DisplayMessageBox(Title, Message):
        WinSize = [IMGUI.get_viewport_client_width(), IMGUI.get_viewport_client_height()]

        with IMGUI.window(label=Title, width=360, height=150, pos=[(WinSize[0] // 2) - 180, (WinSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False) as MsgBoxWindow:
            IMGUI.add_text(Message, wrap=345)

    # Display a messagebox window in the middle of the main viewport, with yes and no options
    def DisplayYesNoPrompt(Title, Message, UpdateWhileWaitingForResponse=False):
        WinSize = [IMGUI.get_viewport_client_width(), IMGUI.get_viewport_client_height()]

        with IMGUI.window(label=Title, width=360, height=150, pos=[(WinSize[0] // 2) - 180, (WinSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False, no_close=True) as MsgBoxWindow:
            IMGUI.add_text(Message, wrap=345)
            IMGUI.add_button(label="Yes", tag="YNYesButton", width=48)
            IMGUI.add_button(label="No", tag="YNNoButton", width=48)

        YesButtonState = IMGUI.get_item_state("YNYesButton")['active']
        NoButtonState = IMGUI.get_item_state("YNNoButton")['active']

        while YesButtonState == False and NoButtonState == False:
            MsgBoxSize = [IMGUI.get_item_width(MsgBoxWindow), IMGUI.get_item_height(MsgBoxWindow)]
            YesButtonState = IMGUI.get_item_state("YNYesButton")['active']
            NoButtonState = IMGUI.get_item_state("YNNoButton")['active']

            IMGUI.set_item_pos("YNYesButton", [(MsgBoxSize[0] / 2) - 52, MsgBoxSize[1] - 30])
            IMGUI.set_item_pos("YNNoButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

            if UpdateWhileWaitingForResponse == True:
                IMGUI.render_dearpygui_frame()

            time.sleep(0.01)

        IMGUI.delete_item(MsgBoxWindow)
        return YesButtonState

class GUI:
    ## VARIABLES ##
    ChessPieceFSMappings = [
        ("Bishop.png", ChessManager.ChessPieces.King),
        ("Knight.png", ChessManager.ChessPieces.Knight),
        ("Queen.png", ChessManager.ChessPieces.Queen),
        ("King.png", ChessManager.ChessPieces.King),
        ("Pawn.png", ChessManager.ChessPieces.Pawn),
        ("Rook.png", ChessManager.ChessPieces.Rook)
    ]

    ChessPieceColors = ["White", "Black"]
    ChessboardColors = [[205, 176, 131], [85, 52, 43], [133, 121, 87]] # Checker 1, checker 2, board border
    PieceIconPaths = os.path.join(os.getcwd(), "UI/Assets/ChessPieces/")
    WindowconPath = os.path.join(os.getcwd(), "UI/Assets/Icon.bmp")
    SquareSize = 32
    MoveList = []
    MainWindow = None
    ResetBoard = True


    ## FUNCTIONS ##
    def InitUI(IMGUIWindowSize, ProgramVersion, SelectableGameModes, Debug=False):
        print("[INFO] >> Creating DearPyGUI context...")
        IMGUI.create_context()

        print("[INFO] >> Creating viewport and setting its properties...")
        IMGUI.create_viewport(title='Shockfish', width=IMGUIWindowSize[0], height=IMGUIWindowSize[1])
        IMGUI.set_viewport_large_icon(GUI.WindowconPath)
        IMGUI.set_viewport_small_icon(GUI.WindowconPath)
        IMGUI.set_viewport_min_width(IMGUIWindowSize[0])
        IMGUI.set_viewport_min_height(IMGUIWindowSize[1])

        StopSearchingForIcons = False
        print("[INFO] >> Checking if chess piece icons exist and loading them...")

        for PieceColor in GUI.ChessPieceColors:
            if StopSearchingForIcons == True:
                break

            if Debug == True:
                print(f"[INFO] >> Checking for \"{PieceColor}\" piece images...")

            for PieceMapping in GUI.ChessPieceFSMappings:
                print(f"[INFO] >> Checking for \"{PieceMapping[0]}\" piece mapping image...")

                IconPath = os.path.join(GUI.PieceIconPaths, f"{PieceColor}{PieceMapping[0]}")

                if os.path.exists(IconPath) == False:
                    if GUIHelpers.DisplayYesNoPrompt("Error - UI Manager", f"The icon \"{IconPath}\" was not found!\n\nWould you like to keep Shockfish open for debugging?", UpdateWhileWaitingForResponse=True) == False:
                        raise FileNotFoundError(f"Chess piece icon \"{IconPath}\" was not found!")
                    
                    else:
                        print("[INFO] >> App will stay open for debugging.")
                        StopSearchingForIcons = True
                        break
                
                else:
                    print(f"[INFO] >> Piece mapping image exists, loading it now (Tag=\"{PieceColor}{PieceMapping[0].split(".")[0]}\")...")
                    Width, Height, Channels, Data = IMGUI.load_image(IconPath)

                    with IMGUI.texture_registry():
                        IMGUI.add_static_texture(Width, Height, Data, tag=f"{PieceColor}{PieceMapping[0].split(".")[0]}")

        print("[INFO] >> Defining UI...")
        with IMGUI.window(label="MainWindow", tag="MainWindow", width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], pos=(0, 0), no_title_bar=True, no_move=True, no_resize=True, no_collapse=True) as GUI.MainWindow:            
            # Main tab bar
            with IMGUI.tab_bar(label='MainTabBar', tag="MainTabBar", reorderable=True):
                # Game tab
                CurrentColor = 1

                with IMGUI.tab(label="Game"):
                    IMGUI.add_spacer()

                    with IMGUI.group(horizontal=True, indent=2):
                        InnerBoardOffset = 1
                        HalfSquareSize = GUI.SquareSize // 2
                        BoardSize = (GUI.SquareSize * 8) + (InnerBoardOffset * 2)
                        
                        # Draw the chess board
                        with IMGUI.drawlist(width=BoardSize, height=BoardSize + 20, tag="ChessBoardGraphic"):
                            with IMGUI.draw_layer():
                                for Y in range(8):
                                    CurrentColor = not CurrentColor
                                    
                                    for X in range(8):
                                        XChange = X * GUI.SquareSize
                                        YChange = Y * GUI.SquareSize
                                        CurrentColor = not CurrentColor

                                        IMGUI.draw_rectangle(pmin=[XChange - InnerBoardOffset, YChange - InnerBoardOffset], pmax=[GUI.SquareSize + XChange - InnerBoardOffset, GUI.SquareSize + YChange - InnerBoardOffset], color=GUI.ChessboardColors[CurrentColor], fill=GUI.ChessboardColors[CurrentColor])
                                        
                                        if GUI.ResetBoard == True:
                                            if Y == 6:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}Pawn", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 1:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}Pawn", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 0 and (X == 0 or X == 7):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}Rook", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 7 and (X == 0 or X == 7):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}Rook", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 0 and (X == 1 or X == 6):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}Knight", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 7 and (X == 1 or X == 6):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}Knight", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 0 and (X == 2 or X == 5):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}Bishop", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 7 and (X == 2 or X == 5):
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}Bishop", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 0 and X == 3:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}Queen", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 7 and X == 3:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}Queen", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 0 and X == 4:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[1]}King", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                            elif Y == 7 and X == 4:
                                                IMGUI.draw_image(f"{GUI.ChessPieceColors[0]}King", (XChange, YChange), (XChange + GUI.SquareSize, YChange + GUI.SquareSize))

                                        
                                IMGUI.draw_rectangle(pmin=[0, 0], pmax=[GUI.SquareSize + XChange + 1, GUI.SquareSize + YChange + 1], color=GUI.ChessboardColors[2], thickness=5)
                                GUI.ResetBoard = False

                            with IMGUI.draw_layer():
                                IMGUI.draw_line([0, 275], [258, 275], color=[96, 96, 96])

                        # Add the moves table
                        with IMGUI.table(label="Move list", tag="MoveListTable", header_row=True, borders_innerH=True, borders_outerH=True, borders_outerV=True, row_background=True):
                            IMGUI.add_table_column(label="Move Number")
                            IMGUI.add_table_column(label="Color")
                            IMGUI.add_table_column(label="Player")
                            IMGUI.add_table_column(label="From")
                            IMGUI.add_table_column(label="To")

                            with IMGUI.table_row(label="1"):
                                IMGUI.add_text("No moves yet")
                                IMGUI.add_text("")
                                IMGUI.add_text("")
                                IMGUI.add_text("")
                                IMGUI.add_text("")

                    IMGUI.add_combo(items=SelectableGameModes, default_value="Select game mode", width=220, pos=[12, 325])
                    IMGUI.add_button(label="?", tag="GamemodeHelpButton", width=24, pos=[240, 325], callback=lambda: GUIHelpers.DisplayMessageBox("Help - Game Modes",
                        """There are 2 game modes to chose from: Realtime and Game Over. Here's a quick breakdown of each.

Realtime mode:\n\tAll moves from both players are tracked in\n\trealtime. You'll know you messed up as soon\n\tas you make a mistake.

Game Over mode:\n\tAll moves will be processed after the game\n\tends, which means you may not know you made\n\ta mistake until it's too late. You'll still\n\tbe punished for each and every error, so\n\tplay wisely!"""))
                    IMGUI.add_button(label="Connect to game", tag="ConDisconButton", width=252, pos=[12, 355])
                    IMGUI.add_button(label="Open a saved game (PGN file)", tag="OpenPGNButton", width=252, pos=[12, 385], callback=lambda: ChessManager.ChessManager.LoadPGNFromFile())

                # Settings tab
                with IMGUI.tab(label="Settings", tag="SettingsTab"):
                    IMGUI.add_spacer()

                    # Chess game settings
                    with IMGUI.collapsing_header(label="Chess", default_open=True):
                        with IMGUI.group(horizontal=True, indent=12):
                            IMGUI.add_text("Chess.com Username: ")
                            IMGUI.add_input_text(hint="Enter Chess.com username", width=-1, tag="ChessUsernameInput")

                        with IMGUI.group(horizontal=True, indent=12):
                            IMGUI.add_text("Game URL: ")
                            IMGUI.add_input_text(hint="Enter URL", width=-1, tag="GameURLInput")

                        # Chess piece settings
                        IMGUI.add_spacer()

                        with IMGUI.collapsing_header(label="Pieces", default_open=True, indent=12):
                            with IMGUI.group(horizontal=True, indent=8):
                                IMGUI.add_button(label="Enable shocker control for all pieces", tag="EnableAllShockerControlButton")
                                IMGUI.add_button(label="Disable shocker control for all pieces", tag="DisableAllShockerControlButton")

                            IMGUI.add_spacer() 
                            GUIHelpers.CreatePieceDropdown("Pawn", 1)
                            GUIHelpers.CreatePieceDropdown("Knight", 3)
                            GUIHelpers.CreatePieceDropdown("Bishop", 3)
                            GUIHelpers.CreatePieceDropdown("Rook", 5)
                            GUIHelpers.CreatePieceDropdown("Queen", 9)
                            GUIHelpers.CreatePieceDropdown("King", "Invaluable")

                        IMGUI.add_spacer()
                        IMGUI.add_spacer()

                    # PiShock settings                    
                    with IMGUI.collapsing_header(label="PiShock", default_open=True):
                        with IMGUI.group(horizontal=True, indent=12):
                            IMGUI.add_text("PiShock Username: ")
                            IMGUI.add_input_text(hint="Enter PiShock username (EX: puppy73)", width=-1, tag="PiShockUsernameInput")

                        with IMGUI.group(horizontal=True, indent=12):
                            IMGUI.add_text("Sharecode: ")
                            IMGUI.add_input_text(hint="Enter PiShock sharecode (EX: 17519CD8GAP)", width=-1, tag="PiShockSharecodeInput")

                        with IMGUI.group(horizontal=True, indent=12):
                            IMGUI.add_text("API Key: ")
                            IMGUI.add_input_text(hint="Enter API key (EX: 5c678926-d19e-4f86-42ad-21f5a76126db)", width=-1, tag="PiShockAPIKeyInput")

                        IMGUI.add_spacer()
                        IMGUI.add_spacer()

                    # Danger zone (settings reset)
                    with IMGUI.collapsing_header(label="Danger zone"):
                        IMGUI.add_button(label="Reset settings to defaults", width=-1, callback=SettingsManager.SettingsManager.ResetSettings)

                # About Shockfish
                with IMGUI.tab(label="About"):
                    IMGUI.add_separator(label=f"Shockfish {ProgramVersion}")
                    IMGUI.add_text("Written by MEMESCOEP, and released under the MIT License.", indent=12)

                    with IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Github Repository", "https://www.github.com/MEMESCOEP/Shockfish")
                        GUIHelpers.DisplayButtonHyperlink("MIT License", "https://opensource.org/license/mit")

                    for I in range(5):
                        IMGUI.add_spacer()

                    IMGUI.add_separator(label=f"DearPyGUI {IMGUI.get_dearpygui_version()}")

                    with IMGUI.group(horizontal=True, indent=12):
                        IMGUI.add_text("Written by Jonathan Hoffstadt and Preston Cothren, and used under the MIT License.")

                    with IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Github Repository", "https://github.com/hoffstadt/DearPyGui")
                        GUIHelpers.DisplayButtonHyperlink("Documentation", "https://dearpygui.readthedocs.io/en/latest/")
                        GUIHelpers.DisplayButtonHyperlink("MIT License", "https://opensource.org/license/mit")

                    for I in range(5):
                        IMGUI.add_spacer()

                    IMGUI.add_separator(label=f"Green Chess Piece Images")

                    with IMGUI.group(horizontal=True, indent=12):
                        IMGUI.add_text("Created by Green Chess, and used under the CC BY-SA 3.0 License.")

                    with IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Website", "https://greenchess.net/info.php?item=downloads")
                        GUIHelpers.DisplayButtonHyperlink("CC BY-SA 3.0 License", "https://creativecommons.org/licenses/by-sa/3.0/deed.en")

        IMGUI.setup_dearpygui()
        IMGUI.show_viewport()

    # Main window loop, akin to Tkinter's mainloop
    def Mainloop(Debug=False):
        while IMGUI.is_dearpygui_running():
            # Get the window size and automatically calculate the size of widgets
            WinSize = [IMGUI.get_viewport_client_width(), IMGUI.get_viewport_client_height()]
            ScrollbarSubtraction = WinSize[0] - IMGUI.get_item_state("SettingsTab")['content_region_avail'][0]
            SliderAutoSizes = [WinSize[0] - ScrollbarSubtraction - 186, WinSize[0] - ScrollbarSubtraction - 207]

            # Resize widgets
            IMGUI.set_item_width(GUI.MainWindow, WinSize[0])
            IMGUI.set_item_height(GUI.MainWindow, WinSize[1])
            IMGUI.set_item_width("PawnIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("PawnDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_width("KnightIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("KnightDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_width("BishopIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("BishopDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_width("RookIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("RookDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_width("QueenIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("QueenDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_width("KingIntensityInput", SliderAutoSizes[0])
            IMGUI.set_item_width("KingDurationInput", SliderAutoSizes[1])
            IMGUI.set_item_height("MoveListTable", WinSize[1] - 48)

            # Show piece property settings if their checkboxes are checked
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("PawnEnableCheckbox"), "PawnProperties")
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("KnightEnableCheckbox"), "KnightProperties")
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("BishopEnableCheckbox"), "BishopProperties")
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("RookEnableCheckbox"), "RookProperties")
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("QueenEnableCheckbox"), "QueenProperties")
            GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("KingEnableCheckbox"), "KingProperties")

            # Add the moves to the move list table
            if len(GUI.MoveList) > 0:
                IMGUI.delete_item("MoveListTable", children_only=True)
                IMGUI.add_table_column(label="Move Number", parent="MoveListTable")
                IMGUI.add_table_column(label="Color", parent="MoveListTable")
                IMGUI.add_table_column(label="Player", parent="MoveListTable")
                IMGUI.add_table_column(label="From", parent="MoveListTable")
                IMGUI.add_table_column(label="To", parent="MoveListTable")

            for Move in reversed(GUI.MoveList):
                with IMGUI.table_row(label="1", parent="MoveListTable"):
                    IMGUI.add_text(str(GUI.MoveList.index(Move)))
                    IMGUI.add_text(Move.Color)
                    IMGUI.add_text(Move.Player)
                    IMGUI.add_text(Move.FromPos)
                    IMGUI.add_text(Move.ToPos)

            # Render the frame
            IMGUI.render_dearpygui_frame()
        
        IMGUI.destroy_context()