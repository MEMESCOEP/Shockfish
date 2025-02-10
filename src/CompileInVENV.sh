#!/bin/bash
## VARIABLES ##
DELETE_VENV="False"
VENV_DIR=".compile_venv"


## MAIN CODE ##
if [ "$DELETE_VENV" == "True" ]; then
    echo "[INFO] >> Removing VENV at \"$VENV_DIR\"..."
    rm -rf $VENV_DIR
fi

echo "[INFO] >> Creating VENV at \"$VENV_DIR\"..."
python3 -m venv $VENV_DIR

echo "[INFO] >> Entering VENV..."
source $VENV_DIR/bin/activate

echo "[INFO] >> Installing PIP packages..."
pip3 install -r CompilerRequirements.txt
pip3 install -r MainRequirements.txt

echo "[INFO] >> Running python compilation script..."
echo
echo
python3 CreateExecutable.py

echo "[INFO] >> Leaving VENV..."
deactivate