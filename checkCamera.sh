#!/bin/sh

# every CHECKTIME seconds, check time since user was last active
# (ie. time since last keypress or mouse movement etc)
# if user has been idle for longer than TIMEOUT seconds, then
# then tell the towerlight server that the user is idleing
# otherwise tell the server that user is still active

CHECKTIME=10
TIMEOUT=600
 
until false
do
  NUMCAMERAS=$(livecameras)
  echo $NUMCAMERAS
  
  if [[ $NUMCAMERAS -gt 0 ]]
  
  then
     # send "idle" command to MwillCU towerlight server
     echo "videoOn" | nc -w 1 127.0.0.1 10007
  else
     echo "videoOff" | nc -w 1 127.0.0.1 10007
  fi
  sleep $CHECKTIME
done
