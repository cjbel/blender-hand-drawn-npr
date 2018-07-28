#!/bin/bash

# Test suite must be run from within Blender. Output is noisy, so redirect it.
blender -b -P tests/tests.py -noaudio 1> /dev/null
