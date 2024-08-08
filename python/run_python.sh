#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the Python script with the provided arguments
python3 python/infusion-v1-server.py "$@"