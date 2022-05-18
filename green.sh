#!/bin/bash

# send "green" command to MwillCU towerlight server

echo "green" | nc -w 1 127.0.0.1 10007

