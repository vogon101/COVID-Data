#!/bin/sh
echo "Running"
cd /home/freddie/playground/COVID-Data
python3 create_graphs.py
python3 run_model.py
