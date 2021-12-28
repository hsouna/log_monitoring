#!/bin/bash

source ./venv/bin/activate
python app.py &
python log_analysis.py --file_path aaa &