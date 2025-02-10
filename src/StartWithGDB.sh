#!/bin/sh
echo "[INFO] >> Starting Main.py with GDB and \"--Debug\"..."
gdb -x .gdbinit --ex "run" -ex "bt" --args python3 Main.py --Debug --DebugStatsInterval 10
