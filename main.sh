#!/bin/bash
python3 src/main.py        # builds into docs/ now
cd docs && python3 -m http.server 8888
