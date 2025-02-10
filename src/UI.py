### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from enum import Enum
import dearpygui.dearpygui as IMGUI
import dearpygui_extend as IMGUI_E
import Settings as SettingsManager
import ChessManager
import webbrowser
import Globals
import string
import time
import os


## CLASSES ##
class MessageBoxButtons(Enum):
    NoButtons = 0
    Close = 1
    YesNo = 2
    Ok = 3

class MessageBox:
    ## VARIABLES ##
    MessageBoxShown = False
    MBClosed = False
    Buttons = MessageBoxButtons.Close
    Message = "No message."
    Actions = {True: None, False: None}
    Window = None
    Title = "Shockfish - Message box"


    ## FUNCTIONS ##
    def Destroy(self):
        self.MBClosed = True
        IMGUI.hide_item(self.Window)
        time.sleep(0.05)
        IMGUI.delete_item(self.Window)
        IMGUI.delete_item(self)

class FileDialog:
    ## FUNCTIONS ##
    # Initialise the file dialog
    # Parameters are:
    #   Title (str) -> the title of the dialog window
    #   StartingDirectory (str) -> the directory the dialog should open and show
    #   ValidExstensions (array) -> only files with one these extensions will be displayed, EX: [{'label': 'All files', 'formats': ['*']}, {'label': 'Text files', 'formats': ['txt']}]
    #   DefaultExtension (int) -> the index of the extension in ValidExstensions that should be selected by default
    def __init__(self, Title="Shockfish - File Dialog", StartingDirectory=Globals.MainProgramPath, ValidExstensions=[{'label': 'All files', 'formats': ['*']}], DefaultExtension=0):
        self.FileSelectedAction = None
        self.DefaultExtension = DefaultExtension
        self.ExtensionFilter = ValidExstensions
        self.Directory = StartingDirectory
        self.PassDebug = False
        self.DGClosed = False
        self.DGWindow = None
        self.Filename = None
        self.UIDrawn = False
        self.Title = Title

    def UpdateFilename(self, Sender, Files, CancelPressed):
        if CancelPressed == True or len(Files) > 0:
            IMGUI.delete_item(self.DGWindow)

            if CancelPressed == False:
                self.Filename = Files[0]

                if self.FileSelectedAction != None:
                    if callable(self.FileSelectedAction) == True:
                        if self.PassDebug == True:
                            self.FileSelectedAction(Files[0], Debug=True)

                        else:
                            self.FileSelectedAction(Files[0])

                    else:
                        print("[ERROR] >> The assigned file selection action is not callable.")

    # Creates a new window with a file browser inside of it. This function should only be called once until the file dialog is closed.
    def Show(self):
        self.UIDrawn = False
        self.DGWindow = IMGUI.add_window(label=self.Title, pos=(0, 0), width=680, height=370, modal=True, no_collapse=True, no_resize=True)
        time.sleep(0.1)
        IMGUI_E.add_file_browser(
            tag=None,
            label=('Choose files', self.Title),
            filetype_filter=self.ExtensionFilter,
            filetype_filter_default=self.DefaultExtension,
            width=680,
            height=355,
            pos=None,
            default_path=self.Directory,
            collapse_sequences=False,
            collapse_sequences_checkbox=False,
            sequence_padding='#',
            show_hidden_files=True,
            path_input_style=1,
            add_filename_tooltip=False,
            tooltip_min_length=100,
            icon_size=1.0,
            allow_multi_selection=False,
            allow_drag=False,
            allow_create_new_folder=True,
            dirs_only=False,
            show_as_window=False,
            modal_window=True,
            show_ok_cancel=True,
            show_nav_icons=True,
            user_data=None,
            parent=self.DGWindow,
            callback=lambda Sender, Files, CancelPressed: self.UpdateFilename(Sender, Files, CancelPressed),
        )

class GUIHelpers:
    ## FUNCTIONS ##
    def UpdateWindowOnResize():
        GUI.WindowResized = True

    def UpdateChessPieces(Debug=False):
        time.sleep(0.1)

        if Debug == True:
            print("[DEBUG] >> Redrawing chess board...")

        for Image in GUI.DrawnPieces:
            if Debug == True:
                print(f"[DEBUG] >> Deleting image \"{Image}\"...")

            IMGUI.delete_item(Image)

        GUI.DrawnPieces.clear()

        for State in ChessManager.ChessManager.CurrentBoardState:
            PosRect = ChessManager.ChessManager.BoardPieceLocations[int(State["Pos"][1:]) - 1][string.ascii_uppercase.index(State["Pos"][:1])]

            if Debug == True:
                print(f"[DEBUG] >> Drawing new \"{State["Piece"]}\" at \"{State["Pos"]}\" (Position rect = {PosRect})...")

            NewImage = IMGUI.draw_image(texture_tag=State["Piece"], pmin=PosRect[0], pmax=PosRect[1], parent="ChessBoardGraphic")
            GUI.DrawnPieces.append(NewImage)

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

    # Show and hide an element with a boolean. True shows, and False hides.
    def ShowHideItemWithBoolean(ShowHide, ItemName):
        if ShowHide == True:
            IMGUI.show_item(ItemName)

        else:
            IMGUI.hide_item(ItemName)

    # Display a message box window in the middle of the main viewport, using the MessageBox class
    def DisplayMessageBoxObject(MessageBox, ForceRender=False):
        with IMGUI.window(label=MessageBox.Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False, no_close=True) as MsgBoxWindow:
            MessageBox.Window = MsgBoxWindow

            with IMGUI.child_window(width=-1, height=76, border=False):
                IMGUI.add_text(MessageBox.Message, wrap=325)

            match MessageBox.Buttons:
                case MessageBoxButtons.Close:
                    IMGUI.add_button(label="Close", tag="MBCloseButton", width=48)

                case MessageBoxButtons.YesNo:
                    IMGUI.add_button(label="Yes", tag="MBYesButton", width=48)
                    IMGUI.add_button(label="No", tag="MBNoButton", width=48)

                case MessageBoxButtons.Ok:
                    IMGUI.add_button(label="Ok", tag="MBOkButton", width=48)

        match MessageBox.Buttons:
            case MessageBoxButtons.NoButtons:
                MessageBox.MBClosed = True

            case MessageBoxButtons.Close:
                CloseButtonState = IMGUI.get_item_state("MBCloseButton")['active']

                while CloseButtonState == False:
                    MsgBoxSize = [IMGUI.get_item_width(MsgBoxWindow), IMGUI.get_item_height(MsgBoxWindow)]
                    CloseButtonState = IMGUI.get_item_state("MBCloseButton")['active']

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        IMGUI.render_dearpygui_frame()

                    IMGUI.set_item_pos("MBCloseButton", [(MsgBoxSize[0] / 2) - 28, MsgBoxSize[1] - 30])
                    time.sleep(0.01)

                if MessageBox.Actions[CloseButtonState] != None:
                    MessageBox.Actions[CloseButtonState]()

            case MessageBoxButtons.YesNo:
                YesButtonState = IMGUI.get_item_state("MBYesButton")['active']
                NoButtonState = IMGUI.get_item_state("MBNoButton")['active']

                while YesButtonState == False and NoButtonState == False:
                    MsgBoxSize = [IMGUI.get_item_width(MsgBoxWindow), IMGUI.get_item_height(MsgBoxWindow)]
                    YesButtonState = IMGUI.get_item_state("MBYesButton")['active']
                    NoButtonState = IMGUI.get_item_state("MBNoButton")['active']

                    IMGUI.set_item_pos("MBYesButton", [(MsgBoxSize[0] / 2) - 52, MsgBoxSize[1] - 30])
                    IMGUI.set_item_pos("MBNoButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        IMGUI.render_dearpygui_frame()

                    time.sleep(0.01)

                if MessageBox.Actions[YesButtonState] != None:
                    MessageBox.Actions[YesButtonState]()

            case MessageBoxButtons.Ok:
                OkButtonState = IMGUI.get_item_state("MBOkButton")['active']

                while OkButtonState == False:
                    MsgBoxSize = [IMGUI.get_item_width(MsgBoxWindow), IMGUI.get_item_height(MsgBoxWindow)]
                    OkButtonState = IMGUI.get_item_state("MBOkButton")['active']

                    IMGUI.set_item_pos("MBOkButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        IMGUI.render_dearpygui_frame()

                    time.sleep(0.01)

                if MessageBox.Actions[True] != None:
                    MessageBox.Actions[True]()

            case _:
                raise NotImplementedError(f"Unrecognized or unimplemented button(s) of type \"{MessageBox.Buttons}\"")

        if MessageBox.Buttons != MessageBoxButtons.NoButtons:
            MessageBox.Destroy()

    # Display a message box window in the middle of the main viewport
    def DisplayMessageBox(Title, Message):
        with IMGUI.window(label=Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False) as MsgBoxWindow:
            IMGUI.add_text(Message, wrap=345)

    # Display a messagebox window in the middle of the main viewport, with yes and no options
    def DisplayYesNoPrompt(Title, Message, UpdateWhileWaitingForResponse=False):
        with IMGUI.window(label=Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False, no_close=True) as MsgBoxWindow:
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

    def RemakeMoveTable():
        IMGUI.add_table_column(label="Move", parent="MoveListTable")
        IMGUI.add_table_column(label="Color", parent="MoveListTable")
        IMGUI.add_table_column(label="Player", parent="MoveListTable")
        IMGUI.add_table_column(label="From", parent="MoveListTable")
        IMGUI.add_table_column(label="To", parent="MoveListTable")
        IMGUI.add_table_column(label="Quality", parent="MoveListTable")

    def CommunicateWithStatsThread():
        Globals.LastIMGUICommunication.value = time.time()


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

    ForcedUpdateInterval = 0.025
    DebugXAxisTimeValues = [0]
    ChessboardColors = [[205, 176, 131], [85, 52, 43], [133, 121, 87]] # Checker 1, checker 2, board border
    DefaultFontPath = os.path.join(Globals.CurrentCWDPath, "UI/Fonts/Aileron-Regular.ttf")
    PieceIconPaths = os.path.join(Globals.CurrentCWDPath, "UI/ChessPieces/")
    WindowIconPath = os.path.join(Globals.CurrentCWDPath, "UI/Icon.bmp")
    WindowResized = True
    MovesUpdated = False
    LastMousePos = [0, 0]
    MessageBoxes = []
    DrawnPieces = []
    MainWindow = None
    ResetBoard = True
    BoardSize = 256
    MoveList = []
    CPUData = [0.0]
    MEMData = [0.0]


    ## FUNCTIONS ##
    def InitUI(IMGUIWindowSize, ProgramVersion, SelectableGameModes, Debug=False):
        print("[INFO] >> Creating DearPyGUI context...")
        IMGUI.create_context()

        print("[INFO] >> Creating viewport and setting its properties...")
        if Globals.CurrentPlatform == "windows":
            IMGUIWindowSize[1] += 16

        IMGUI.setup_dearpygui()
        IMGUI.create_viewport(title='Shockfish', width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], clear_color=[0, 0, 0, 255])
        IMGUI.set_viewport_large_icon(GUI.WindowIconPath)
        IMGUI.set_viewport_small_icon(GUI.WindowIconPath)
        IMGUI.set_viewport_min_width(IMGUIWindowSize[0])
        IMGUI.set_viewport_min_height(IMGUIWindowSize[1])
        IMGUI.set_viewport_resize_callback(GUIHelpers.UpdateWindowOnResize)
        IMGUI.show_viewport()

        print(f"[INFO] >> Loading UI font \"{GUI.DefaultFontPath}\"...")
        with IMGUI.font_registry():
            UIFont = IMGUI.add_font(GUI.DefaultFontPath, 16)

        IMGUI.bind_font(UIFont)

        StopSearchingForIcons = False
        print("[INFO] >> Checking if chess piece icons exist and loading them...")

        for PieceColor in ChessManager.ChessManager.ChessPieceColors:
            if StopSearchingForIcons == True:
                break

            if Debug == True:
                print(f"[DEBUG] >> Checking for \"{PieceColor}\" piece images...")

            for PieceMapping in GUI.ChessPieceFSMappings:
                if Debug == True:
                    print(f"[DEBUG] >> Checking for \"{PieceMapping[0]}\" piece mapping image...")

                IconPath = os.path.join(GUI.PieceIconPaths, f"{PieceColor}{PieceMapping[0]}")

                if os.path.exists(IconPath) == False:
                    print(f"[ERROR] >> Chess piece icon \"{IconPath}\" was not found.")

                    if GUIHelpers.DisplayYesNoPrompt("Error - UI Manager", f"The icon \"{IconPath}\" was not found!\n\nWould you like to keep Shockfish open for debugging?", UpdateWhileWaitingForResponse=True) == False:
                        raise FileNotFoundError(f"Chess piece icon \"{IconPath}\" was not found!")

                    else:
                        print("[INFO] >> App will stay open for debugging.")
                        StopSearchingForIcons = True
                        break

                else:
                    Width, Height, Channels, Data = IMGUI.load_image(IconPath)

                    with IMGUI.texture_registry():
                        IMGUI.add_static_texture(Width, Height, Data, tag=f"{PieceColor}{PieceMapping[0].split(".")[0]}")

                    if Debug == True:
                        print(f"[DEBUG] >> Added static texture with tag \"{PieceColor}{PieceMapping[0].split(".")[0]}\" ({Channels} channels, Dimensions are {Width}x{Height}, Size is {len(Data)})...")

        print("[INFO] >> Defining UI...")
        with IMGUI.window(label="MainWindow", tag="MainWindow", width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], pos=(0, 0), no_title_bar=True, no_move=True, no_resize=True, no_collapse=True) as GUI.MainWindow:
            # Main tab bar
            with IMGUI.tab_bar(label='MainTabBar', tag="MainTabBar", reorderable=True):
                # Game tab
                BorderThickness = 4
                InnerBoardSize = GUI.BoardSize - BorderThickness
                InnerBoxSize = InnerBoardSize / 8
                CurrentColor = 1

                if Debug == True:
                    print(f"[DEBUG] >> Chess board has total size of {GUI.BoardSize}x{GUI.BoardSize}, with inner dimensions being {InnerBoardSize}x{InnerBoardSize}. Border thickness is {BorderThickness}, and the inner square size is {InnerBoxSize}x{InnerBoxSize}.")

                with IMGUI.tab(label="Game", tag="GameTab"):
                    IMGUI.add_spacer()

                    with IMGUI.group(horizontal=True, indent=2, tag="ChessBoardGroup"):
                        with IMGUI.drawlist(width=GUI.BoardSize, height=GUI.BoardSize + 20, tag="ChessBoardGraphic"):
                            with IMGUI.draw_layer():
                                for Y in range(8):
                                    CurrentColor = not CurrentColor
                                    RowPositions = []

                                    for X in range(8):
                                        CurrentColor = not CurrentColor
                                        XChange = X * InnerBoxSize - (BorderThickness / 2)
                                        YChange = Y * InnerBoxSize - (BorderThickness / 2)
                                        Rect = [
                                            [XChange + BorderThickness, YChange + BorderThickness],
                                            [XChange + InnerBoxSize + BorderThickness, YChange + InnerBoxSize + BorderThickness]
                                        ]

                                        IMGUI.draw_rectangle(
                                            pmin=Rect[0], pmax=Rect[1],
                                            color=GUI.ChessboardColors[CurrentColor], fill=GUI.ChessboardColors[CurrentColor]
                                        )

                                        if GUI.ResetBoard == True:
                                            PiecePos = [(XChange + BorderThickness, YChange + BorderThickness), (XChange + InnerBoxSize + BorderThickness, YChange + InnerBoxSize + BorderThickness)]
                                            RowPositions.append(PiecePos)

                                    ChessManager.ChessManager.BoardPieceLocations.append(RowPositions)

                            IMGUI.draw_rectangle(pmin=[0, 0], pmax=[GUI.BoardSize, GUI.BoardSize], color=GUI.ChessboardColors[2], thickness=BorderThickness)

                            with IMGUI.draw_layer():
                                IMGUI.draw_line([0, 275], [258, 275], color=[96, 96, 96])

                        # Add the moves table
                        with IMGUI.table(label="Move list", tag="MoveListTable", header_row=True, borders_innerH=True, borders_outerH=True, borders_outerV=True, row_background=True, scrollX=True, scrollY=True, resizable=True):
                            GUIHelpers.RemakeMoveTable()

                    IMGUI.add_combo(items=SelectableGameModes, default_value="Select game mode", width=220, pos=[12, 325])
                    IMGUI.add_button(label="?", tag="GamemodeHelpButton", width=24, pos=[240, 325], callback=lambda: GUIHelpers.DisplayMessageBox("Help - Game Modes",
                        """There are 2 game modes to chose from: Realtime and Game Over. Here's a quick breakdown of each.

Realtime mode:\n\tAll moves from both players are tracked in\n\trealtime. You'll know you messed up as soon\n\tas you make a mistake. Note that this mode\n\tonly works with daily games.

Game Over mode:\n\tAll moves will be processed after the game\n\tends, which means you may not know you made\n\ta mistake until it's too late. You'll still\n\tbe punished for each and every error, so\n\tplay wisely!"""))
                    IMGUI.add_button(label="Connect to game", tag="ConDisconButton", width=252, pos=[12, 355])
                    IMGUI.add_button(label="Open a saved game (PGN file)", tag="OpenPGNButton", width=252, pos=[12, 385], callback=lambda: ChessManager.ChessManager.UILoadPGN(Debug))

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

                        # Stockfish settings
                        IMGUI.add_spacer()

                        with IMGUI.collapsing_header(label="Stockfish", indent=12):
                            with IMGUI.group(horizontal=True, indent=8):
                                IMGUI.add_text("Stockfish path: ")
                                IMGUI.add_input_text(default_value=Globals.StockfishPath, tag="StockfishPathInput", width=-1)

                            IMGUI.add_spacer()

                        # Chess piece settings
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

                # Debugging UI
                if Debug == True:
                    with IMGUI.tab(label="Debug", tag="DebugTab"):
                        IMGUI.add_spacer()
                        
                        with IMGUI.collapsing_header(label="Resource stats", default_open=True):
                            with IMGUI.group(horizontal=True):
                                with IMGUI.plot(label="CPU Usage", tag="CPUUsageGraph", width=(Globals.WindowSize[0] / 2) - 12):
                                    XAxis = IMGUI.add_plot_axis(axis=IMGUI.mvXAxis, label="Time (seconds)", tag="CPUUsageXAxis")
                                    YAxis = IMGUI.add_plot_axis(axis=IMGUI.mvYAxis, label="Usage (%)", tag="CPUUsageYAxis")
                                    
                                    IMGUI.add_shade_series(x=[0], y1=[0], parent=YAxis, tag="CPUUsageLine")
                                    IMGUI.set_axis_limits(axis=YAxis, ymin=0, ymax=100)
                                    IMGUI.set_axis_limits_auto(XAxis)

                                with IMGUI.plot(label="Memory Usage", tag="MEMUsageGraph", width=(Globals.WindowSize[0] / 2) - 12):
                                    XAxis = IMGUI.add_plot_axis(axis=IMGUI.mvXAxis, label="Time (seconds)", tag="MEMUsageXAxis")
                                    YAxis = IMGUI.add_plot_axis(axis=IMGUI.mvYAxis, label="Usage (KB)", tag="MEMUsageYAxis")
                                    
                                    IMGUI.add_shade_series(x=[0], y1=[0], parent=YAxis, tag="MEMUsageLine")
                                    IMGUI.set_axis_limits_auto(XAxis)

                            IMGUI.add_spacer()
                            IMGUI.add_spacer()

                        with IMGUI.collapsing_header(label="Chess engine properties", default_open=True):
                            IMGUI.add_text(f"Stockfish version: \"{ChessManager.ChessManager.EngineData[0]}\"", tag="DebugSFVersion", indent=12)
                            IMGUI.add_text(f"Chess module version: \"{ChessManager.ChessManager.EngineData[1]}\"", tag="DebugChessVersion", indent=12)

            # Draw a black square until the app finished loading
            with IMGUI.window(width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], tag="BlackWindow", pos=[0, 0], no_title_bar=True, no_resize=True):
                with IMGUI.theme() as IntroFadeTempTheme:
                    with IMGUI.theme_component(IMGUI.mvAll):
                        IMGUI.add_theme_color(IMGUI.mvThemeCol_WindowBg, [0, 0, 0, 255], tag="IntroFadeTempBGColor")

                IMGUI.bind_item_theme("BlackWindow", IntroFadeTempTheme)

        if Debug == True:
            print(f"[DEBUG] >> Chess board piece locations: {ChessManager.ChessManager.BoardPieceLocations}")

        Globals.GUIInitFinished.value = True

    # Main window loop, akin to Tkinter's mainloop
    def Mainloop(Debug=False):
        Globals.MainViewportIsOpen.value = True
        LastDebugPlotUpdateTime = 0
        LastUpdateTime = time.time()

        # Fade in the UI
        FadeSteps = 8
        FadeTime = 0.0005
        BGColor = [0, 0, 0, 255]
        FadeRM = 255 / FadeSteps

        with IMGUI.theme() as IntroFadeTheme:
            with IMGUI.theme_component(IMGUI.mvAll):
                IntroFadeBG = IMGUI.add_theme_color(IMGUI.mvThemeCol_WindowBg, BGColor, tag="IntroFadeBGColor")

        IMGUI.bind_item_theme("BlackWindow", IntroFadeTheme)

        for I in range(FadeSteps):
            IMGUI.set_value(IntroFadeBG, BGColor)
            IMGUI.render_dearpygui_frame()
            time.sleep(FadeTime)

            BGColor[3] -= FadeRM

        IMGUI.delete_item("BlackWindow")

        SettingsTabID = IMGUI.get_alias_id("SettingsTab")
        GameTabID = IMGUI.get_alias_id("GameTab")

        if Debug == True:
            IMGUI.set_value("DebugSFVersion", f"Stockfish version: \"{ChessManager.ChessManager.EngineData[0]}\"")
            IMGUI.set_value("DebugChessVersion", f"Chess module version: {ChessManager.ChessManager.EngineData[1]}")

        while IMGUI.is_dearpygui_running():
            # Only update the UI when the mouse moves, this reduces CPU usage
            if IMGUI.get_mouse_pos() != GUI.LastMousePos or time.time() - LastUpdateTime >= GUI.ForcedUpdateInterval:
                CurrentTab = IMGUI.get_value("MainTabBar")
                LastUpdateTime = time.time()

                # Get the window size and automatically calculate the size of widgets
                Globals.WindowSize = [IMGUI.get_viewport_client_width(), IMGUI.get_viewport_client_height()]
                GUI.LastMousePos = IMGUI.get_mouse_pos()

                if GUI.ResetBoard == True:
                    ChessManager.ChessManager.CurrentBoardState = ChessManager.ChessManager.DefaultBoardState
                    GUIHelpers.UpdateChessPieces(Debug)
                    GUI.ResetBoard = False

                # Resize widgets if the window's size was changed
                if GUI.WindowResized == True:
                    ScrollbarSubtraction = Globals.WindowSize[0] - IMGUI.get_item_state("SettingsTab")['content_region_avail'][0]
                    SliderAutoSizes = [Globals.WindowSize[0] - ScrollbarSubtraction - 186, Globals.WindowSize[0] - ScrollbarSubtraction - 207]
                    GUI.WindowResized = False

                    IMGUI.set_item_width(GUI.MainWindow, Globals.WindowSize[0])
                    IMGUI.set_item_height(GUI.MainWindow, Globals.WindowSize[1])
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
                    IMGUI.set_item_height("MoveListTable", Globals.WindowSize[1] - 48)

                    if Debug == True:
                        IMGUI.set_item_width("CPUUsageGraph", (Globals.WindowSize[0] / 2) - 12)
                        IMGUI.set_item_width("MEMUsageGraph", (Globals.WindowSize[0] / 2) - 12)
                        IMGUI.set_item_height("CPUUsageGraph", Globals.WindowSize[1] - 192)
                        IMGUI.set_item_height("MEMUsageGraph", Globals.WindowSize[1] - 192)

                # Show piece property settings if their checkboxes are checked
                if CurrentTab == SettingsTabID:
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("PawnEnableCheckbox"), "PawnProperties")
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("KnightEnableCheckbox"), "KnightProperties")
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("BishopEnableCheckbox"), "BishopProperties")
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("RookEnableCheckbox"), "RookProperties")
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("QueenEnableCheckbox"), "QueenProperties")
                    GUIHelpers.ShowHideItemWithBoolean(IMGUI.get_value("KingEnableCheckbox"), "KingProperties")

                # Add the moves to the move list table
                if CurrentTab == GameTabID and GUI.MovesUpdated == True:
                    GUI.MovesUpdated = False

                    if len(GUI.MoveList) > 0:
                        IMGUI.delete_item("MoveListTable", children_only=True)
                        GUIHelpers.RemakeMoveTable()

                    for Move in reversed(GUI.MoveList):
                        with IMGUI.table_row(parent="MoveListTable"):
                            IMGUI.add_text(Move["MoveNumber"])
                            IMGUI.add_text(Move["Color"])
                            IMGUI.add_text(Move["Player"])
                            IMGUI.add_text(Move["FromPos"])
                            IMGUI.add_text(Move["ToPos"])
                            IMGUI.add_text(Move["Quality"])

                    GUIHelpers.UpdateChessPieces(Debug)

                # Show message boxes
                for MB in GUI.MessageBoxes:
                    if MB.MessageBoxShown == False:
                        MB.MessageBoxShown = True

                        GUIHelpers.DisplayMessageBoxObject(MB, True)

                    if MB.MBClosed == True:
                        GUI.MessageBoxes.remove(MB)

                IMGUI.render_dearpygui_frame()
            
            else:
                time.sleep(GUI.ForcedUpdateInterval)

            if Debug == True:
                if IMGUI.get_frame_count() % 60 == 0:
                    GUIHelpers.CommunicateWithStatsThread()

                if LastDebugPlotUpdateTime == 0 or time.time() - LastDebugPlotUpdateTime >= Globals.DebugChartInterval.value:
                    LastDebugPlotUpdateTime = time.time()
                    GUI.DebugXAxisTimeValues.append(LastDebugPlotUpdateTime - Globals.BootTime)
                    GUI.CPUData.append(Globals.CPUUsage.value)
                    GUI.MEMData.append(Globals.MEMUsage.value)

                    if len(GUI.CPUData) >= 10:
                        GUI.DebugXAxisTimeValues = GUI.DebugXAxisTimeValues[1:]
                        GUI.CPUData = GUI.CPUData[1:]
                        GUI.MEMData = GUI.MEMData[1:]

                    IMGUI.set_axis_limits(axis="MEMUsageYAxis", ymin=0, ymax=Globals.AllocatedMEM.value)
                    IMGUI.configure_item("CPUUsageLine", x=GUI.DebugXAxisTimeValues)
                    IMGUI.configure_item("CPUUsageLine", y1=GUI.CPUData)
                    IMGUI.configure_item("MEMUsageLine", x=GUI.DebugXAxisTimeValues)
                    IMGUI.configure_item("MEMUsageLine", y1=GUI.MEMData)
                    IMGUI.fit_axis_data("CPUUsageXAxis")
                    IMGUI.fit_axis_data("MEMUsageXAxis")

        print("[INFO] >> Destroying IMGUI context...")
        IMGUI.destroy_context()

        print("[INFO] >> Viewport closed.")
        Globals.MainViewportIsOpen.value = False