#!/bin/bash

# send "red" command to MwillCU towerlight server

echo "red" | nc -w 1 127.0.0.1 10007

