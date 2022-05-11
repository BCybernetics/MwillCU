#!/bin/bash

# send "yellow" command to MwillCU towerlight server

echo "yellow" | nc -w 1 127.0.0.1 10007

