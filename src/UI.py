### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from enum import Enum
import dearpygui_extend as IMGUI_E
import webbrowser
import Globals
import string
import time
import os


## CLASSES ##
class ModuleReferences:
    ## VARIABLES ##
    MODULE_REF_SETTINGSMANAGER = None
    MODULE_REF_PISHOCKMANAGER = None
    MODULE_REF_CHESSMANAGER = None


    ## FUNCTIONS ##
    def PassReferences(SettingsManager: __module__, PiShockManager: __module__, ChessManager: __module__, IMGUI: __module__):
        ModuleReferences.MODULE_REF_SETTINGSMANAGER = SettingsManager
        ModuleReferences.MODULE_REF_PISHOCKMANAGER = PiShockManager
        ModuleReferences.MODULE_REF_CHESSMANAGER = ChessManager
        ModuleReferences.MODULE_REF_IMGUI = IMGUI

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
        ModuleReferences.MODULE_REF_IMGUI.hide_item(self.Window)
        time.sleep(0.05)
        ModuleReferences.MODULE_REF_IMGUI.delete_item(self.Window)
        ModuleReferences.MODULE_REF_IMGUI.delete_item(self)

class FileDialog:
    ## FUNCTIONS ##
    # Initialise the file dialog
    # Parameters are:
    #   Title (str) -> the title of the dialog window
    #   StartingDirectory (str) -> the directory the dialog should open and show
    #   ValidExstensions (array) -> only files with one these extensions will be displayed, EX: [{'label': 'All files', 'formats': ['*']}, {'label': 'Text files', 'formats': ['txt']}]
    #   DefaultExtension (int) -> the index of the extension in ValidExstensions that should be selected by default
    def __init__(self, Title="Shockfish - File Dialog", StartingDirectory=None, ValidExstensions=[{'label': 'All files', 'formats': ['*']}], DefaultExtension=0):
        if StartingDirectory == None:
            StartingDirectory = Globals.MainProgramPath
        
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
            ModuleReferences.MODULE_REF_IMGUI.delete_item(self.DGWindow)

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
        self.DGWindow = ModuleReferences.MODULE_REF_IMGUI.add_window(label=self.Title, pos=(0, 0), width=680, height=370, modal=True, no_collapse=True, no_resize=True)
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

            ModuleReferences.MODULE_REF_IMGUI.delete_item(Image)

        GUI.DrawnPieces.clear()

        for State in ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.CurrentBoardState:
            PosRect = ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.BoardPieceLocations[int(State["Pos"][1:]) - 1][string.ascii_uppercase.index(State["Pos"][:1])]

            if Debug == True:
                print(f"[DEBUG] >> Drawing new \"{State["Piece"]}\" at \"{State["Pos"]}\" (Position rect = {PosRect})...")

            NewImage = ModuleReferences.MODULE_REF_IMGUI.draw_image(texture_tag=State["Piece"], pmin=PosRect[0], pmax=PosRect[1], parent="ChessBoardGraphic")
            GUI.DrawnPieces.append(NewImage)

    # Create a button that acts as a clickable link. This will open a URL in the default web browser.
    def DisplayButtonHyperlink(Text, Address):
        HLButton = ModuleReferences.MODULE_REF_IMGUI.add_button(label=Text, callback=lambda:webbrowser.open(Address))
        ModuleReferences.MODULE_REF_IMGUI.bind_item_theme(HLButton, "__demo_hyperlinkTheme")

    # Create a settings option for
    def CreatePieceDropdown(PieceName, PointValue):
        if type(PointValue) == int:
            PointStr = f"{PointValue} point{'s' if PointValue != 1 else ''}"

        else:
            PointStr = PointValue

        with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label=f"{PieceName} ({PointStr})", indent=12):
            ModuleReferences.MODULE_REF_IMGUI.add_checkbox(label="Enable shocker control for this piece", tag=f"{PieceName}EnableCheckbox", default_value=True, indent=12)

            with ModuleReferences.MODULE_REF_IMGUI.group(tag=f"{PieceName}Properties"):
                ModuleReferences.MODULE_REF_IMGUI.add_combo(items=["Shock", "Vibrate"], default_value="Vibrate", width=-1, tag=f"{PieceName}ActionComboBox", indent=12)

                with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                    ModuleReferences.MODULE_REF_IMGUI.add_text("Intensity: ")
                    ModuleReferences.MODULE_REF_IMGUI.add_slider_int(default_value=5, min_value=1, max_value=100, format="%d%%", tag=f"{PieceName}IntensityInput")
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="-", repeat=True, width=24, callback=lambda: ModuleReferences.MODULE_REF_IMGUI.set_value(f"{PieceName}IntensityInput", ModuleReferences.MODULE_REF_IMGUI.get_value(f"{PieceName}IntensityInput") - 1))
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="+", repeat=True, width=24, callback=lambda: ModuleReferences.MODULE_REF_IMGUI.set_value(f"{PieceName}IntensityInput", ModuleReferences.MODULE_REF_IMGUI.get_value(f"{PieceName}IntensityInput") + 1))

                with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                    ModuleReferences.MODULE_REF_IMGUI.add_text("Duration (S): ")
                    ModuleReferences.MODULE_REF_IMGUI.add_slider_float(default_value=0.5, min_value=0.1, max_value=15, format="%.1f second(s)", tag=f"{PieceName}DurationInput")
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="-", repeat=True, width=24, callback=lambda: ModuleReferences.MODULE_REF_IMGUI.set_value(f"{PieceName}DurationInput", ModuleReferences.MODULE_REF_IMGUI.get_value(f"{PieceName}DurationInput") - 0.1))
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="+", repeat=True, width=24, callback=lambda: ModuleReferences.MODULE_REF_IMGUI.set_value(f"{PieceName}DurationInput", ModuleReferences.MODULE_REF_IMGUI.get_value(f"{PieceName}DurationInput") + 0.1))

            ModuleReferences.MODULE_REF_IMGUI.add_spacer()
            ModuleReferences.MODULE_REF_IMGUI.add_spacer()

    # Show and hide an element with a boolean. True shows, and False hides.
    def ShowHideItemWithBoolean(ShowHide, ItemName):
        if ShowHide == True:
            ModuleReferences.MODULE_REF_IMGUI.show_item(ItemName)

        else:
            ModuleReferences.MODULE_REF_IMGUI.hide_item(ItemName)

    # Display a message box window in the middle of the main viewport, using the MessageBox class
    def DisplayMessageBoxObject(MessageBox, ForceRender=False):
        with ModuleReferences.MODULE_REF_IMGUI.window(label=MessageBox.Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False, no_close=True) as MsgBoxWindow:
            MessageBox.Window = MsgBoxWindow

            with ModuleReferences.MODULE_REF_IMGUI.child_window(width=-1, height=76, border=False):
                ModuleReferences.MODULE_REF_IMGUI.add_text(MessageBox.Message, wrap=325)

            match MessageBox.Buttons:
                case MessageBoxButtons.Close:
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Close", tag="MBCloseButton", width=48)

                case MessageBoxButtons.YesNo:
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Yes", tag="MBYesButton", width=48)
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="No", tag="MBNoButton", width=48)

                case MessageBoxButtons.Ok:
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Ok", tag="MBOkButton", width=48)

        match MessageBox.Buttons:
            case MessageBoxButtons.NoButtons:
                MessageBox.MBClosed = True

            case MessageBoxButtons.Close:
                CloseButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBCloseButton")['active']

                while CloseButtonState == False:
                    MsgBoxSize = [ModuleReferences.MODULE_REF_IMGUI.get_item_width(MsgBoxWindow), ModuleReferences.MODULE_REF_IMGUI.get_item_height(MsgBoxWindow)]
                    CloseButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBCloseButton")['active']

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()

                    ModuleReferences.MODULE_REF_IMGUI.set_item_pos("MBCloseButton", [(MsgBoxSize[0] / 2) - 28, MsgBoxSize[1] - 30])
                    time.sleep(0.01)

                if MessageBox.Actions[CloseButtonState] != None:
                    MessageBox.Actions[CloseButtonState]()

            case MessageBoxButtons.YesNo:
                YesButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBYesButton")['active']
                NoButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBNoButton")['active']

                while YesButtonState == False and NoButtonState == False:
                    MsgBoxSize = [ModuleReferences.MODULE_REF_IMGUI.get_item_width(MsgBoxWindow), ModuleReferences.MODULE_REF_IMGUI.get_item_height(MsgBoxWindow)]
                    YesButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBYesButton")['active']
                    NoButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBNoButton")['active']

                    ModuleReferences.MODULE_REF_IMGUI.set_item_pos("MBYesButton", [(MsgBoxSize[0] / 2) - 52, MsgBoxSize[1] - 30])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_pos("MBNoButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()

                    time.sleep(0.01)

                if MessageBox.Actions[YesButtonState] != None:
                    MessageBox.Actions[YesButtonState]()

            case MessageBoxButtons.Ok:
                OkButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBOkButton")['active']

                while OkButtonState == False:
                    MsgBoxSize = [ModuleReferences.MODULE_REF_IMGUI.get_item_width(MsgBoxWindow), ModuleReferences.MODULE_REF_IMGUI.get_item_height(MsgBoxWindow)]
                    OkButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("MBOkButton")['active']

                    ModuleReferences.MODULE_REF_IMGUI.set_item_pos("MBOkButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

                    if Globals.GUIInitFinished.value == False or ForceRender == True:
                        ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()

                    time.sleep(0.01)

                if MessageBox.Actions[True] != None:
                    MessageBox.Actions[True]()

            case _:
                raise NotImplementedError(f"Unrecognized or unimplemented button(s) of type \"{MessageBox.Buttons}\"")

        if MessageBox.Buttons != MessageBoxButtons.NoButtons:
            MessageBox.Destroy()

    # Display a message box window in the middle of the main viewport
    def DisplayMessageBox(Title, Message):
        with ModuleReferences.MODULE_REF_IMGUI.window(label=Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False) as MsgBoxWindow:
            ModuleReferences.MODULE_REF_IMGUI.add_text(Message, wrap=345)

    # Display a messagebox window in the middle of the main viewport, with yes and no options
    def DisplayYesNoPrompt(Title, Message, UpdateWhileWaitingForResponse=False):
        with ModuleReferences.MODULE_REF_IMGUI.window(label=Title, width=360, height=150, pos=[(Globals.WindowSize[0] // 2) - 180, (Globals.WindowSize[1] // 2) - 75], no_move=True, no_resize=True, no_collapse=True, modal=True, no_scrollbar=False, no_close=True) as MsgBoxWindow:
            ModuleReferences.MODULE_REF_IMGUI.add_text(Message, wrap=345)
            ModuleReferences.MODULE_REF_IMGUI.add_button(label="Yes", tag="YNYesButton", width=48)
            ModuleReferences.MODULE_REF_IMGUI.add_button(label="No", tag="YNNoButton", width=48)

        YesButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("YNYesButton")['active']
        NoButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("YNNoButton")['active']

        while YesButtonState == False and NoButtonState == False:
            MsgBoxSize = [ModuleReferences.MODULE_REF_IMGUI.get_item_width(MsgBoxWindow), ModuleReferences.MODULE_REF_IMGUI.get_item_height(MsgBoxWindow)]
            YesButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("YNYesButton")['active']
            NoButtonState = ModuleReferences.MODULE_REF_IMGUI.get_item_state("YNNoButton")['active']

            ModuleReferences.MODULE_REF_IMGUI.set_item_pos("YNYesButton", [(MsgBoxSize[0] / 2) - 52, MsgBoxSize[1] - 30])
            ModuleReferences.MODULE_REF_IMGUI.set_item_pos("YNNoButton", [(MsgBoxSize[0] / 2) + 8, MsgBoxSize[1] - 30])

            if UpdateWhileWaitingForResponse == True:
                ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()

            time.sleep(0.01)

        ModuleReferences.MODULE_REF_IMGUI.delete_item(MsgBoxWindow)
        return YesButtonState

    def RemakeMoveTable():
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="Move", parent="MoveListTable")
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="Color", parent="MoveListTable")
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="Player", parent="MoveListTable")
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="From", parent="MoveListTable")
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="To", parent="MoveListTable")
        ModuleReferences.MODULE_REF_IMGUI.add_table_column(label="Quality", parent="MoveListTable")

    def CommunicateWithStatsThread():
        Globals.LastIMGUICommunication.value = time.time()


class GUI:
    ## VARIABLES ##
    ForcedUpdateInterval = 0.05
    DebugXAxisTimeValues = [0]
    ChessboardColors = [[205, 176, 131], [85, 52, 43], [133, 121, 87]] # Checker 1, checker 2, board border
    DefaultFontPath = os.path.join(Globals.CurrentCWDPath, "UI", "Fonts", "Aileron-Regular.ttf")
    PieceIconPaths = os.path.join(Globals.CurrentCWDPath, "UI", f"ChessPieces{Globals.PathSeparator}")
    WindowIconPath = os.path.join(Globals.CurrentCWDPath, "UI", "Icon.bmp")
    WindowResized = True
    ForceUIRender = False
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
    FPSData = [0.0]


    ## FUNCTIONS ##
    def ScrollHandler():
        GUI.ForceUIRender = True

    def InitUI(IMGUIWindowSize, ProgramVersion, SelectableGameModes, Debug=False):
        print("[INFO] >> Creating DearPyGUI context...")
        ModuleReferences.MODULE_REF_IMGUI.create_context()

        print("[INFO] >> Creating viewport and setting its properties...")
        if Globals.CurrentPlatform == "windows":
            IMGUIWindowSize[1] += 16

        ModuleReferences.MODULE_REF_IMGUI.setup_dearpygui()
        ModuleReferences.MODULE_REF_IMGUI.create_viewport(title='Shockfish', width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], clear_color=[0, 0, 0, 255])
        ModuleReferences.MODULE_REF_IMGUI.set_viewport_large_icon(GUI.WindowIconPath)
        ModuleReferences.MODULE_REF_IMGUI.set_viewport_small_icon(GUI.WindowIconPath)
        ModuleReferences.MODULE_REF_IMGUI.set_viewport_min_width(IMGUIWindowSize[0])
        ModuleReferences.MODULE_REF_IMGUI.set_viewport_min_height(IMGUIWindowSize[1])
        ModuleReferences.MODULE_REF_IMGUI.set_viewport_resize_callback(GUIHelpers.UpdateWindowOnResize)
        ModuleReferences.MODULE_REF_IMGUI.show_viewport()

        print(f"[INFO] >> Loading UI font \"{GUI.DefaultFontPath}\"...")
        with ModuleReferences.MODULE_REF_IMGUI.font_registry():
            UIFont = ModuleReferences.MODULE_REF_IMGUI.add_font(GUI.DefaultFontPath, 16)

        ModuleReferences.MODULE_REF_IMGUI.bind_font(UIFont)

        StopSearchingForIcons = False
        print("[INFO] >> Checking if chess piece icons exist and loading them...")

        for PieceColor in ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.ChessPieceColors:
            if StopSearchingForIcons == True:
                break

            if Debug == True:
                print(f"[DEBUG] >> Checking for \"{PieceColor}\" piece images...")

            for PieceMapping in ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.ChessPieceFSMappings:
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
                    Width, Height, Channels, Data = ModuleReferences.MODULE_REF_IMGUI.load_image(IconPath)

                    with ModuleReferences.MODULE_REF_IMGUI.texture_registry():
                        ModuleReferences.MODULE_REF_IMGUI.add_static_texture(Width, Height, Data, tag=f"{PieceColor}{PieceMapping[0].split(".")[0]}")

                    if Debug == True:
                        print(f"[DEBUG] >> Added static texture with tag \"{PieceColor}{PieceMapping[0].split(".")[0]}\" ({Channels} channels, Dimensions are {Width}x{Height}, Size is {len(Data)})...")

        print("[INFO] >> Defining UI...")
        with ModuleReferences.MODULE_REF_IMGUI.window(label="MainWindow", tag="MainWindow", width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], pos=(0, 0), no_title_bar=True, no_move=True, no_resize=True, no_collapse=True) as GUI.MainWindow:
            # Main tab bar
            with ModuleReferences.MODULE_REF_IMGUI.tab_bar(label='MainTabBar', tag="MainTabBar", reorderable=True):
                # Game tab
                BorderThickness = 4
                InnerBoardSize = GUI.BoardSize - BorderThickness
                InnerBoxSize = InnerBoardSize / 8
                CurrentColor = 1

                if Debug == True:
                    print(f"[DEBUG] >> Chess board has total size of {GUI.BoardSize}x{GUI.BoardSize}, with inner dimensions being {InnerBoardSize}x{InnerBoardSize}. Border thickness is {BorderThickness}, and the inner square size is {InnerBoxSize}x{InnerBoxSize}.")

                with ModuleReferences.MODULE_REF_IMGUI.tab(label="Game", tag="GameTab"):
                    ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=2, tag="ChessBoardGroup"):
                        with ModuleReferences.MODULE_REF_IMGUI.drawlist(width=GUI.BoardSize, height=GUI.BoardSize + 20, tag="ChessBoardGraphic"):
                            with ModuleReferences.MODULE_REF_IMGUI.draw_layer():
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

                                        ModuleReferences.MODULE_REF_IMGUI.draw_rectangle(
                                            pmin=Rect[0], pmax=Rect[1],
                                            color=GUI.ChessboardColors[CurrentColor], fill=GUI.ChessboardColors[CurrentColor]
                                        )

                                        if GUI.ResetBoard == True:
                                            PiecePos = [(XChange + BorderThickness, YChange + BorderThickness), (XChange + InnerBoxSize + BorderThickness, YChange + InnerBoxSize + BorderThickness)]
                                            RowPositions.append(PiecePos)

                                    ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.BoardPieceLocations.append(RowPositions)

                            ModuleReferences.MODULE_REF_IMGUI.draw_rectangle(pmin=[0, 0], pmax=[GUI.BoardSize, GUI.BoardSize], color=GUI.ChessboardColors[2], thickness=BorderThickness)

                            with ModuleReferences.MODULE_REF_IMGUI.draw_layer():
                                ModuleReferences.MODULE_REF_IMGUI.draw_line([0, 275], [258, 275], color=[96, 96, 96])

                        # Add the moves table
                        with ModuleReferences.MODULE_REF_IMGUI.table(label="Move list", tag="MoveListTable", header_row=True, borders_innerH=True, borders_outerH=True, borders_outerV=True, row_background=True, scrollX=True, scrollY=True, resizable=True):
                            GUIHelpers.RemakeMoveTable()

                    ModuleReferences.MODULE_REF_IMGUI.add_combo(items=SelectableGameModes, default_value="Select game mode", width=220, pos=[12, 325])
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="?", tag="GamemodeHelpButton", width=24, pos=[240, 325], callback=lambda: GUIHelpers.DisplayMessageBox("Help - Game Modes",
                        """There are 2 game modes to chose from: Realtime and Game Over. Here's a quick breakdown of each.

Realtime mode:\n\tAll moves from both players are tracked in\n\trealtime. You'll know you messed up as soon\n\tas you make a mistake. Note that this mode\n\tonly works with daily games.

Game Over mode:\n\tAll moves will be processed after the game\n\tends, which means you may not know you made\n\ta mistake until it's too late. You'll still\n\tbe punished for each and every error, so\n\tplay wisely!"""))
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Connect to game", tag="ConDisconButton", width=252, pos=[12, 355], callback=lambda: ModuleReferences.MODULE_REF_PISHOCKMANAGER.ZapManager.SendCommandToPiShock(ModuleReferences.MODULE_REF_PISHOCKMANAGER.PiShockCommandTypes.Shock, 1, 1.0, Debug))
                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Open a saved game (PGN file)", tag="OpenPGNButton", width=252, pos=[12, 385], callback=lambda: ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.UILoadPGN(Debug))

                # Settings tab
                with ModuleReferences.MODULE_REF_IMGUI.tab(label="Settings", tag="SettingsTab"):
                    with ModuleReferences.MODULE_REF_IMGUI.child_window(width=-1, height=-1):
                        # Chess game settings
                        with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Chess", default_open=True):
                            with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                                ModuleReferences.MODULE_REF_IMGUI.add_text("Chess.com Username: ")
                                ModuleReferences.MODULE_REF_IMGUI.add_input_text(hint="Enter Chess.com username", width=-1, tag="ChessUsernameInput")

                            with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                                ModuleReferences.MODULE_REF_IMGUI.add_text("Game URL: ")
                                ModuleReferences.MODULE_REF_IMGUI.add_input_text(hint="Enter URL", width=-1, tag="GameURLInput")

                            # Stockfish settings
                            ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                            with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Stockfish", indent=12):
                                with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=8):
                                    ModuleReferences.MODULE_REF_IMGUI.add_text("Stockfish path: ")
                                    ModuleReferences.MODULE_REF_IMGUI.add_input_text(default_value=Globals.StockfishPath, tag="StockfishPathInput", width=-1)

                                ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                            # Chess piece settings
                            with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Pieces", default_open=True, indent=12):
                                with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=8):
                                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Enable shocker control for all pieces", tag="EnableAllShockerControlButton")
                                    ModuleReferences.MODULE_REF_IMGUI.add_button(label="Disable shocker control for all pieces", tag="DisableAllShockerControlButton")

                                ModuleReferences.MODULE_REF_IMGUI.add_spacer()
                                GUIHelpers.CreatePieceDropdown("Pawn", 1)
                                GUIHelpers.CreatePieceDropdown("Knight", 3)
                                GUIHelpers.CreatePieceDropdown("Bishop", 3)
                                GUIHelpers.CreatePieceDropdown("Rook", 5)
                                GUIHelpers.CreatePieceDropdown("Queen", 9)
                                GUIHelpers.CreatePieceDropdown("King", "Invaluable")

                            ModuleReferences.MODULE_REF_IMGUI.add_spacer()
                            ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                        # PiShock settings
                        with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="PiShock", default_open=True):
                            with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                                ModuleReferences.MODULE_REF_IMGUI.add_text("PiShock Username: ")
                                ModuleReferences.MODULE_REF_IMGUI.add_input_text(hint="Enter PiShock username (EX: puppy73)", width=-1, tag="PiShockUsernameInput", callback=lambda: ModuleReferences.MODULE_REF_PISHOCKMANAGER.ZapManager.SetConfig(
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockSharecodeInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockUsernameInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockAPIKeyInput")
                                ))

                            with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                                ModuleReferences.MODULE_REF_IMGUI.add_text("Sharecode: ")
                                ModuleReferences.MODULE_REF_IMGUI.add_input_text(hint="Enter PiShock sharecode (EX: 17519CD8GAP)", width=-1, tag="PiShockSharecodeInput", callback=lambda: ModuleReferences.MODULE_REF_PISHOCKMANAGER.ZapManager.SetConfig(
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockSharecodeInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockUsernameInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockAPIKeyInput")
                                ))

                            with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                                ModuleReferences.MODULE_REF_IMGUI.add_text("API Key: ")
                                ModuleReferences.MODULE_REF_IMGUI.add_input_text(hint="Enter API key (EX: 5c678926-d19e-4f86-42ad-21f5a76126db)", width=-1, tag="PiShockAPIKeyInput", callback=lambda: ModuleReferences.MODULE_REF_PISHOCKMANAGER.ZapManager.SetConfig(
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockSharecodeInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockUsernameInput"),
                                    ModuleReferences.MODULE_REF_IMGUI.get_value("PiShockAPIKeyInput")
                                ))

                            ModuleReferences.MODULE_REF_IMGUI.add_spacer()
                            ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                        # Danger zone (settings reset)
                        with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Danger zone"):
                            ModuleReferences.MODULE_REF_IMGUI.add_button(label="Reset settings to defaults", width=-1, callback=ModuleReferences.MODULE_REF_SETTINGSMANAGER.SettingsManager.ResetSettings)

                # About Shockfish
                with ModuleReferences.MODULE_REF_IMGUI.tab(label="About"):
                    ModuleReferences.MODULE_REF_IMGUI.add_separator(label=f"Shockfish {ProgramVersion}")
                    ModuleReferences.MODULE_REF_IMGUI.add_text("Written by MEMESCOEP, and released under the MIT License.", indent=12)

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Github Repository", "https://www.github.com/MEMESCOEP/Shockfish")
                        GUIHelpers.DisplayButtonHyperlink("MIT License", "https://opensource.org/license/mit")

                    for I in range(5):
                        ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                    ModuleReferences.MODULE_REF_IMGUI.add_separator(label=f"DearPyGUI {ModuleReferences.MODULE_REF_IMGUI.get_dearpygui_version()}")

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                        ModuleReferences.MODULE_REF_IMGUI.add_text("Written by Jonathan Hoffstadt and Preston Cothren, and used under the MIT License.")

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Github Repository", "https://github.com/hoffstadt/DearPyGui")
                        GUIHelpers.DisplayButtonHyperlink("Documentation", "https://dearpygui.readthedocs.io/en/latest/")
                        GUIHelpers.DisplayButtonHyperlink("MIT License", "https://opensource.org/license/mit")

                    for I in range(5):
                        ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                    ModuleReferences.MODULE_REF_IMGUI.add_separator(label=f"Green Chess Piece Images")

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                        ModuleReferences.MODULE_REF_IMGUI.add_text("Created by Green Chess, and used under the CC BY-SA 3.0 License.")

                    with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True, indent=12):
                        GUIHelpers.DisplayButtonHyperlink("Website", "https://greenchess.net/info.php?item=downloads")
                        GUIHelpers.DisplayButtonHyperlink("CC BY-SA 3.0 License", "https://creativecommons.org/licenses/by-sa/3.0/deed.en")

                # Debugging UI
                if Debug == True:
                    """SysMonitors = get_monitors()
                    WinPos = ModuleReferences.MODULE_REF_IMGUI.get_viewport_pos()
    
                    # Check which monitor the window is located on based on the viewport position
                    for Monitor in SysMonitors:
                        if Monitor.is_primary:
                            # If the window's position is within the bounds of the primary monitor
                            if (Monitor.x <= WinPos[0] < Monitor.x + Monitor.width) and (Monitor.y <= WinPos[1] < Monitor.y + Monitor.height):
                                print(Monitor)"""

                    with ModuleReferences.MODULE_REF_IMGUI.tab(label="Debug", tag="DebugTab"):
                        with ModuleReferences.MODULE_REF_IMGUI.child_window(tag="DebugTabChildWindow", width=-1, height=-1):
                            with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Resource stats", default_open=True):
                                with ModuleReferences.MODULE_REF_IMGUI.group(horizontal=True):
                                    with ModuleReferences.MODULE_REF_IMGUI.plot(label="CPU Usage", tag="CPUUsageGraph", width=(Globals.WindowSize[0] / 2) - 12):
                                        XAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvXAxis, label="Time (seconds)", tag="CPUUsageXAxis")
                                        YAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvYAxis, label="Usage (%)", tag="CPUUsageYAxis")
                                        
                                        ModuleReferences.MODULE_REF_IMGUI.add_shade_series(x=[0], y1=[0], parent=YAxis, tag="CPUUsageLine")
                                        ModuleReferences.MODULE_REF_IMGUI.set_axis_limits(axis=YAxis, ymin=0, ymax=100)
                                        ModuleReferences.MODULE_REF_IMGUI.set_axis_limits_auto(XAxis)

                                    with ModuleReferences.MODULE_REF_IMGUI.plot(label="Memory Usage", tag="MEMUsageGraph", width=(Globals.WindowSize[0] / 2) - 12):
                                        XAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvXAxis, label="Time (seconds)", tag="MEMUsageXAxis")
                                        YAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvYAxis, label="Usage (KB)", tag="MEMUsageYAxis")
                                        
                                        ModuleReferences.MODULE_REF_IMGUI.add_shade_series(x=[0], y1=[0], parent=YAxis, tag="MEMUsageLine")
                                        ModuleReferences.MODULE_REF_IMGUI.set_axis_limits_auto(XAxis)

                                with ModuleReferences.MODULE_REF_IMGUI.plot(label="FPS", tag="FPSGraph", width=(Globals.WindowSize[0] / 2) - 12):
                                    XAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvXAxis, label="Time (seconds)", tag="FPSXAxis")
                                    YAxis = ModuleReferences.MODULE_REF_IMGUI.add_plot_axis(axis=ModuleReferences.MODULE_REF_IMGUI.mvYAxis, label="FPS", tag="FPSYAxis")
                                    
                                    ModuleReferences.MODULE_REF_IMGUI.add_line_series(x=[0], y=[0], parent=YAxis, tag="FPSLine")
                                    ModuleReferences.MODULE_REF_IMGUI.set_axis_limits_auto(XAxis)
                                    ModuleReferences.MODULE_REF_IMGUI.set_axis_limits_auto(YAxis)

                                ModuleReferences.MODULE_REF_IMGUI.add_spacer()
                                ModuleReferences.MODULE_REF_IMGUI.add_spacer()

                            with ModuleReferences.MODULE_REF_IMGUI.collapsing_header(label="Chess engine properties", default_open=True):
                                ModuleReferences.MODULE_REF_IMGUI.add_text(f"Stockfish version: \"{ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.EngineData[0]}\"", tag="DebugSFVersion", indent=12)
                                ModuleReferences.MODULE_REF_IMGUI.add_text(f"Chess module version: \"{ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.EngineData[1]}\"", tag="DebugChessVersion", indent=12)

            # Draw a black square until the app finished loading
            with ModuleReferences.MODULE_REF_IMGUI.window(width=IMGUIWindowSize[0], height=IMGUIWindowSize[1], tag="BlackWindow", pos=[0, 0], no_title_bar=True, no_resize=True, no_move=True):
                with ModuleReferences.MODULE_REF_IMGUI.theme() as IntroFadeTempTheme:
                    with ModuleReferences.MODULE_REF_IMGUI.theme_component(ModuleReferences.MODULE_REF_IMGUI.mvAll):
                        ModuleReferences.MODULE_REF_IMGUI.add_theme_color(ModuleReferences.MODULE_REF_IMGUI.mvThemeCol_WindowBg, [0, 0, 0, 255], tag="IntroFadeTempBGColor")

                ModuleReferences.MODULE_REF_IMGUI.bind_item_theme("BlackWindow", IntroFadeTempTheme)

        if Debug == True:
            print(f"[DEBUG] >> Chess board piece locations: {ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.BoardPieceLocations}")

        print("[INFO] >> Setting up event handlers...")
        with ModuleReferences.MODULE_REF_IMGUI.handler_registry():
            ModuleReferences.MODULE_REF_IMGUI.add_mouse_wheel_handler(callback=GUI.ScrollHandler)

        if Debug == True:
            ModuleReferences.MODULE_REF_IMGUI.show_metrics()

        AppConfig = ModuleReferences.MODULE_REF_IMGUI.get_app_configuration()
        Globals.GUIInitFinished.value = True
        
        print(f"[INFO] >> UI init done.\n[INFO] >> Running on device \"{AppConfig['device_name']}\" (device index {AppConfig['device']}).")

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

        with ModuleReferences.MODULE_REF_IMGUI.theme() as IntroFadeTheme:
            with ModuleReferences.MODULE_REF_IMGUI.theme_component(ModuleReferences.MODULE_REF_IMGUI.mvAll):
                IntroFadeBG = ModuleReferences.MODULE_REF_IMGUI.add_theme_color(ModuleReferences.MODULE_REF_IMGUI.mvThemeCol_WindowBg, BGColor, tag="IntroFadeBGColor")

        ModuleReferences.MODULE_REF_IMGUI.bind_item_theme("BlackWindow", IntroFadeTheme)

        for I in range(FadeSteps):
            ModuleReferences.MODULE_REF_IMGUI.set_value(IntroFadeBG, BGColor)
            ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()
            time.sleep(FadeTime)

            BGColor[3] -= FadeRM

        ModuleReferences.MODULE_REF_IMGUI.delete_item("BlackWindow")

        SettingsTabID = ModuleReferences.MODULE_REF_IMGUI.get_alias_id("SettingsTab")
        GameTabID = ModuleReferences.MODULE_REF_IMGUI.get_alias_id("GameTab")

        if Debug == True:
            ModuleReferences.MODULE_REF_IMGUI.set_value("DebugSFVersion", f"Stockfish version: \"{ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.EngineData[0]}\"")
            ModuleReferences.MODULE_REF_IMGUI.set_value("DebugChessVersion", f"Chess module version: {ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.EngineData[1]}")

        while ModuleReferences.MODULE_REF_IMGUI.is_dearpygui_running():
            # Only update the UI when the mouse moves (or it the UI should be forced to render), this reduces resource usage
            if GUI.ForceUIRender == True or ModuleReferences.MODULE_REF_IMGUI.get_mouse_pos() != GUI.LastMousePos or time.time() - LastUpdateTime >= GUI.ForcedUpdateInterval:
                GUI.ForceUIRender = False
                LastUpdateTime = time.time()
                CurrentTab = ModuleReferences.MODULE_REF_IMGUI.get_value("MainTabBar")

                # Get the window size and automatically calculate the size of widgets
                Globals.WindowSize = [ModuleReferences.MODULE_REF_IMGUI.get_viewport_client_width(), ModuleReferences.MODULE_REF_IMGUI.get_viewport_client_height()]
                GUI.LastMousePos = ModuleReferences.MODULE_REF_IMGUI.get_mouse_pos()

                if GUI.ResetBoard == True:
                    ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.CurrentBoardState = ModuleReferences.MODULE_REF_CHESSMANAGER.BoardManager.DefaultBoardState
                    GUIHelpers.UpdateChessPieces(Debug)
                    GUI.ResetBoard = False

                # Resize widgets if the window's size was changed
                if GUI.WindowResized == True:
                    ScrollbarSubtraction = Globals.WindowSize[0] - ModuleReferences.MODULE_REF_IMGUI.get_item_state("SettingsTab")['content_region_avail'][0]
                    SliderAutoSizes = [Globals.WindowSize[0] - ScrollbarSubtraction - 186, Globals.WindowSize[0] - ScrollbarSubtraction - 207]
                    GUI.WindowResized = False

                    ModuleReferences.MODULE_REF_IMGUI.set_item_width(GUI.MainWindow, Globals.WindowSize[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_height(GUI.MainWindow, Globals.WindowSize[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("PawnIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("PawnDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("KnightIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("KnightDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("BishopIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("BishopDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("RookIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("RookDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("QueenIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("QueenDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("KingIntensityInput", SliderAutoSizes[0])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_width("KingDurationInput", SliderAutoSizes[1])
                    ModuleReferences.MODULE_REF_IMGUI.set_item_height("MoveListTable", Globals.WindowSize[1] - 48)

                    if Debug == True:
                        ModuleReferences.MODULE_REF_IMGUI.set_item_width("CPUUsageGraph", (Globals.WindowSize[0] / 2) - 12)
                        ModuleReferences.MODULE_REF_IMGUI.set_item_width("MEMUsageGraph", (Globals.WindowSize[0] / 2) - 12)
                        ModuleReferences.MODULE_REF_IMGUI.set_item_height("CPUUsageGraph", Globals.WindowSize[1] - 192)
                        ModuleReferences.MODULE_REF_IMGUI.set_item_height("MEMUsageGraph", Globals.WindowSize[1] - 192)

                # Show piece property settings if their checkboxes are checked
                if CurrentTab == SettingsTabID:
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("PawnEnableCheckbox"), "PawnProperties")
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("KnightEnableCheckbox"), "KnightProperties")
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("BishopEnableCheckbox"), "BishopProperties")
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("RookEnableCheckbox"), "RookProperties")
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("QueenEnableCheckbox"), "QueenProperties")
                    GUIHelpers.ShowHideItemWithBoolean(ModuleReferences.MODULE_REF_IMGUI.get_value("KingEnableCheckbox"), "KingProperties")

                # Add the moves to the move list table
                if CurrentTab == GameTabID and GUI.MovesUpdated == True:
                    GUI.MovesUpdated = False

                    if len(GUI.MoveList) > 0:
                        ModuleReferences.MODULE_REF_IMGUI.delete_item("MoveListTable", children_only=True)
                        GUIHelpers.RemakeMoveTable()

                    for Move in reversed(GUI.MoveList):
                        with ModuleReferences.MODULE_REF_IMGUI.table_row(parent="MoveListTable"):
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["MoveNumber"])
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["Color"])
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["Player"])
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["FromPos"])
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["ToPos"])
                            ModuleReferences.MODULE_REF_IMGUI.add_text(Move["Quality"])

                    GUIHelpers.UpdateChessPieces(Debug)

                # Show message boxes
                for MB in GUI.MessageBoxes:
                    if MB.MessageBoxShown == False:
                        MB.MessageBoxShown = True

                        GUIHelpers.DisplayMessageBoxObject(MB, True)

                    if MB.MBClosed == True:
                        GUI.MessageBoxes.remove(MB)

                ModuleReferences.MODULE_REF_IMGUI.render_dearpygui_frame()
            
            else:
                time.sleep(GUI.ForcedUpdateInterval)

            if Debug == True:
                if ModuleReferences.MODULE_REF_IMGUI.get_frame_count() % 60 == 0:
                    GUIHelpers.CommunicateWithStatsThread()

                if LastDebugPlotUpdateTime == 0 or time.time() - LastDebugPlotUpdateTime >= Globals.DebugChartInterval.value:
                    LastDebugPlotUpdateTime = time.time()
                    GUI.DebugXAxisTimeValues.append(LastDebugPlotUpdateTime - Globals.BootTime)
                    GUI.CPUData.append(Globals.CPUUsage.value)
                    GUI.MEMData.append(Globals.MEMUsage.value)
                    GUI.FPSData.append(ModuleReferences.MODULE_REF_IMGUI.get_frame_rate())

                    if len(GUI.CPUData) >= 10:
                        GUI.DebugXAxisTimeValues = GUI.DebugXAxisTimeValues[1:]
                        GUI.CPUData = GUI.CPUData[1:]
                        GUI.MEMData = GUI.MEMData[1:]
                        GUI.FPSData = GUI.FPSData[1:]

                    ModuleReferences.MODULE_REF_IMGUI.set_axis_limits(axis="MEMUsageYAxis", ymin=0, ymax=Globals.AllocatedMEM.value)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("CPUUsageLine", x=GUI.DebugXAxisTimeValues)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("CPUUsageLine", y1=GUI.CPUData)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("MEMUsageLine", x=GUI.DebugXAxisTimeValues)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("MEMUsageLine", y1=GUI.MEMData)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("FPSLine", x=GUI.DebugXAxisTimeValues)
                    ModuleReferences.MODULE_REF_IMGUI.configure_item("FPSLine", y=GUI.FPSData)
                    ModuleReferences.MODULE_REF_IMGUI.fit_axis_data("CPUUsageXAxis")
                    ModuleReferences.MODULE_REF_IMGUI.fit_axis_data("MEMUsageXAxis")
                    ModuleReferences.MODULE_REF_IMGUI.fit_axis_data("FPSXAxis")
                    ModuleReferences.MODULE_REF_IMGUI.fit_axis_data("FPSYAxis")

        ModuleReferences.MODULE_REF_SETTINGSMANAGER.SettingsManager.SaveSettings(Debug)

        print("[INFO] >> Destroying IMGUI context...")
        ModuleReferences.MODULE_REF_IMGUI.destroy_context()

        print("[INFO] >> Viewport closed.")
        Globals.MainViewportIsOpen.value = False