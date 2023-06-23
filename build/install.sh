#!/bin/bash

# initialize directory
mkdir text-dungeon ; cd text-dungeon ; touch text-dungeon.desktop

# download needed files
echo Downloading executable...
curl -#fL -o text-dungeon https://github.com/Masbender/text-dungeon/releases/download/v1.0/text-dungeon-linux
echo Downloading icon...
curl -#fLO https://raw.githubusercontent.com/Masbender/text-dungeon/main/build/icon.png

# allow binary to launch
sudo chmod +x text-dungeon text-dungeon.desktop

# generate desktop entry
echo "" > text-dungeon.desktop
echo [Desktop Entry] >> text-dungeon.desktop
echo Name=Text Dungeon >> text-dungeon.desktop
echo Type=Application >> text-dungeon.desktop
echo Comment=suffer alone in your terminal! >> text-dungeon.desktop
echo Icon=$(pwd)/icon.png >> text-dungeon.desktop
echo Exec=$(pwd)/text-dungeon >> text-dungeon.desktop
echo Terminal=true >> text-dungeon.desktop

# copy .desktop file to ~/.local/share/applications
cp text-dungeon.desktop ~/.local/share/applications/
