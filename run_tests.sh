#!/bin/bash

# Any test starting with "test_" is considered Blender-independent. Run these tests first.
echo "Running general tests..."
python -m unittest discover -v

# If tests fail, exit here with appropriate error code.
if [ $? -ne 0 ]; then
    exit 1
else
    echo "Running Blender tests..."
    # This test suite must be run from within Blender. Output is noisy, so redirect it.
    blender -b -P tests/blender_tests.py -noaudio 1> /dev/null
fi
