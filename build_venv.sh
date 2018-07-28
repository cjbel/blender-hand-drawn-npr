#!/bin/bash

# Create and activate the local dev environment.
python -m venv venv
source venv/bin/activate

# Install required packages to local dev environment (for development & testing outside of Blender).
pip install -r requirements.txt
# Link blender modules (use for IDE code completion only).
ln -s /usr/share/blender/2.79/scripts/modules/bpy ~/workspace/blender-hand-drawn-npr/venv/lib/python3.6/site-packages/
ln -s /usr/share/blender/2.79/scripts/modules/bpy_extras ~/workspace/blender-hand-drawn-npr/venv/lib/python3.6/site-packages/

# Install required packages to Blender python environment (for use inside of Blender).
sudo pip install -r requirements.txt --target=/usr/share/blender/2.79/scripts/modules
