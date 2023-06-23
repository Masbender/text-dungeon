#!/bin/bash

# initialize directory
mkdir text-dungeon ; cd text-dungeon ; touch text-dungeon.desktop

# download needed files
echo Downloading executable...
curl -#fL -o text-dungeon https://github.com/Masbender/text-dungeon/releases/download/v0.01/text-dungeon
echo Downloading icon...
curl -#fL -o logo.jpg https://raw.githubusercontent.com/Masbender/text-dungeon/main/logo.jpg

# allow binary to launch
sudo chmod +x text-dungeon text-dungeon.desktop

# generate desktop entry
echo "" > text-dungeon.desktop
echo [Desktop Entry] >> text-dungeon.desktop
echo Name=Text Dungeon >> text-dungeon.desktop
echo Type=Application >> text-dungeon.desktop
echo Comment=A cool text dungeon game in your terminal! >> text-dungeon.desktop
echo Icon=$(pwd)/logo.jpg >> text-dungeon.desktop
echo Exec=$(pwd)/text-dungeon >> text-dungeon.desktop
echo Terminal=true >> text-dungeon.desktop

# copy .desktop file to ~/.local/share/applications
cp text-dungeon.desktop ~/.local/share/applications/
