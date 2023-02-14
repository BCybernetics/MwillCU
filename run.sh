#!/bin/bash

python3 MwillCU.py &

./checkIdle.sh &

./checkCamera.sh &

