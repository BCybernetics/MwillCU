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
  IDLETIME=$((`ioreg -c IOHIDSystem | sed -e '/HIDIdleTime/ !{ d' -e 't' -e '}' -e 's/.* = //g' -e 'q'` / 1000000000))
  echo $IDLETIME
  sleep $CHECKTIME
  if [[ $IDLETIME -gt $TIMEOUT ]]
  
  then
     # send "idle" command to MwillCU towerlight server
     echo "idle" | nc -w 1 127.0.0.1 10007
  else
     echo "active" | nc -w 1 127.0.0.1 10007
  fi
done
