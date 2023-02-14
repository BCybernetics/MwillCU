"""

Example for Adafruit USB tower light w/alarm
don't forget `pip3 install pyserial`


Usage:

python3 MwillCU.py [<deviceName>]

where optional <deviceName> is the name of the serial port for the towerlight, 
on the mac found in /dev/ listing, eg 'cu.usbserial-4013110'
Serial devices will show up as 2 port entries, 'cu.usbserial-*' and 'tty.usbserial-*'
we want the 'cu.usbserial-*' port, because that is for the "calling out unit"

client processes should: 

1. connect on port 10007, eg. ```nc 127.0.0.1 10007 hello```

2. send commands:

```red``` : turns light RED for kRedTimeOut, then server will automatically switch light  to YELLOW
```yellow``` turns light YELLOW for kYellowTimeOut, then server will automatically switch light to GREEN
```green``` turns light GREEN for kGreenTimeOut, then server will automatically switch light to OFF
```off``` turns light OFF (and never times out)
```active``` tells us that user is active (so keep light going)
```idle```  tell us that user is idle (so turn light off)
```quit``` tells server to turn off light and quit


"""

import serial
import time
import socket
import select
import sys
import glob

kOverallTimeOut = 86400000.0  # quit server after a while so we don't run forever

# serial port settings for USB
#serialPort = 'COM57'  # Change to the serial/COM port of the tower light

# deviceName likely different for every computer/device
# on mac/linux, it will be a /dev path
# can be passed in on command line
deviceName = 'cu.usbserial-4013110'  
baudRate = 9600


# byte commands sent to LED USB device

ALL_OFF = 0x00 # virtual command, translated to sending allOff
RED_ON = 0x11
RED_OFF = 0x21
RED_BLINK = 0x41

YELLOW_ON= 0x12
YELLOW_OFF = 0x22
YELLOW_BLINK = 0x42

GREEN_ON = 0x14
GREEN_OFF = 0x24
GREEN_BLINK = 0x44

BUZZER_ON = 0x18
BUZZER_OFF = 0x28
BUZZER_BLINK = 0x48




 






# ------------------------------------------------------------- #

# server defaults

MAX_LENGTH = 4096
PORT = 10007
HOST = '127.0.0.1'

SELECT_TIMEOUT = 1

# states
kUserOff = 0
kUserGreen  = 1
kUserYellow  = 2
kUserRed  = 3
kActiveGreen  = 4
kIdleOff  = 5
kTimerYellow  = 6
kTimerGreen   = 7
kVideoOn = 8
kVideoOff = 9

kStateColors = [ALL_OFF, GREEN_ON, YELLOW_ON, RED_ON, GREEN_ON, ALL_OFF, YELLOW_ON, GREEN_ON, RED_ON, ALL_OFF]
kStateStrings = [
     "UserOff",
     "UserGreen",
     "UserYellow",
     "UserRed",
     "ActiveGreen",
     "IdleOff",
     "TimerYellow",
     "TimerGreen",
     "VideoOn",
     "VideoOff"
]

# element at [<senderColor> (row),<lastSenderCurrentColor> (column)] is <newSenderNewColor>
kTransitionTable = [
[kUserOff,kUserOff,kUserOff,kUserOff,kUserOff,kUserOff,kUserOff,kUserOff,kUserOff,kUserOff],
[kUserGreen,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kVideoOff],
[kUserYellow,kUserYellow,kUserYellow,kUserYellow,kUserYellow,kUserYellow,kUserYellow,kUserYellow,kUserYellow,kVideoOff],
[kUserRed,kUserRed,kUserRed,kUserRed,kUserRed,kUserRed,kUserRed,kUserRed,kUserRed,kVideoOff],
[kUserOff,kUserGreen,kUserYellow,kUserRed,kActiveGreen,kActiveGreen,kTimerYellow,kActiveGreen,kVideoOn,kVideoOff],
[kUserOff,kUserGreen,kUserYellow,kUserRed,kIdleOff,kIdleOff,kIdleOff,kIdleOff,kVideoOn,kIdleOff],
[kUserOff,kUserGreen,kUserYellow,kUserRed,kTimerYellow,kTimerYellow,kTimerYellow,kTimerGreen,kVideoOn,kVideoOff],
[kUserOff,kUserGreen,kUserYellow,kUserRed,kUserGreen,kUserGreen,kUserGreen,kUserGreen,kVideoOn,kVideoOff],
[kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOn,kVideoOff],
[kUserOff,kUserGreen,kUserYellow,kUserRed,kActiveGreen,kIdleOff,kTimerYellow,kTimerGreen,kTimerYellow,kVideoOff]
]

# ------------------------------------------------------------- #

# length of time that a light is left on before automatically rolling over to next light

kOffTimeOut = 3600 # 60 minutes 
kRedTimeOut = 3300.0 # 55 minutes
kYellowTimeOut = 600.0 # 10 minutes
kGreenTimeOut = 3300.0 # 55 minutes
kUserTimeOut = 3600.0 # 55 minutes

kTimeOuts = [
     [kOffTimeOut,kActiveGreen],
     [kUserTimeOut,kActiveGreen],
     [kUserTimeOut,kActiveGreen],
     [0,kTimerYellow],
     [0,kActiveGreen],
     [0,kIdleOff],
     [kYellowTimeOut,kUserGreen ],
     [kGreenTimeOut,kUserGreen ],
     [0,kVideoOn],
     [0,kVideoOff]
]

# ------------------------------------------------------------- #

# tokens received by server, mapped to new state input
kTokenInputMap = [
     [ b"off",  kUserOff],
     [ b"green",  kUserGreen],
     [ b"yellow",  kUserYellow],
     [ b"red",  kUserRed],
     [ b"active",  kActiveGreen],
     [ b"idle",  kIdleOff],
     [ b"timedY",  kTimerYellow],
     [ b"timedG",  kTimerGreen],
     [ b"videoOn",  kVideoOn],
     [ b"videoOff",  kVideoOff]
]



# ------------------------------------------------------------- #

# the curent LED and when it was started
currentLED = ALL_OFF
currentState = kIdleOff
ledStartTime = 2147483647.0

# ------------------------------------------------------------- #

def sendCommand(serialport, cmd):
    serialport.write(bytes([cmd]))
    
# ------------------------------------------------------------- #

def allOff(serialport):
    sendCommand(serialport, BUZZER_OFF)
    sendCommand(serialport, RED_OFF)
    sendCommand(serialport, YELLOW_OFF)
    sendCommand(serialport, GREEN_OFF)

# ------------------------------------------------------------- #

def setState(serialport,newState):

     global currentState
     global ledStartTime
     
     if (newState != currentState):
          newColor = kStateColors[newState]
          setLED(serialport,newColor)
          currentState = newState
          ledStartTime = time.time();
          print("New state: ", kStateStrings[currentState],"  ", ledStartTime)
          
# ------------------------------------------------------------- #

def transitionToNewState(serialport,newInput):

     global currentState
     global ledStartTime
     
     newState = kTransitionTable[newInput][currentState]
     
     setState(serialport,newState)
     
     

# ------------------------------------------------------------- #

def setLED(serialport,ledColor):

    global currentLED

    # Clean up any old state
    allOff(serialport)
    if (ledColor != ALL_OFF):
        sendCommand(serialport, ledColor)
        
    currentLED = ledColor

    
# ------------------------------------------------------------- #

        
def checkLEDTimer(serialport):
    global currentState
    global currentLED
    global ledStartTime
    global timeOuts
    
    if (kTimeOuts[currentState][0] == 0):
          return
          
    timeNow = time.time();
   # print(currentState, " " , (timeNow - ledStartTime), "  ", kTimeOuts[currentState][0])
    if ((timeNow - ledStartTime) > kTimeOuts[currentState][0]):
        print(currentState, " Timed Out! -> ",kTimeOuts[currentState][1])
        setState(serialport,kTimeOuts[currentState][1])
        print("switched to ", currentState)
               
# ------------------------------------------------------------- #

if __name__ == '__main__':

    
    # set up socketserver
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.setblocking(0)
    serversocket.bind((HOST, PORT))
    serversocket.listen(10) # how many connections requests to queue
    readable = [serversocket];
    
    # use default serial port, almost certainly not correct
    serialPort = '/dev/'+ deviceName
    
    # connect to usb serial device
    if len(sys.argv) >= 2:
          deviceName = sys.argv[1]
          print(deviceName)
          serialPort = '/dev/'+ deviceName
    else:
          servernames = glob.glob('/dev/cu.usbserial-*')
          if (len(servernames) == 1):
               print("Found serial device ", servernames[0])
               serialPort = servernames[0]
          elif (len(servernames) > 1):
               print("\nFound more than one /dev/cu.usbserial-* device,\nso you'll need to specify on invoation\neg: python3 MwillCU.py cu.usbserial-11111")
     
    print("using serial port: ",serialPort,"\n\n")

    mSerial = serial.Serial(serialPort, baudRate)

    # set light to initial state
    allOff(mSerial)
    
    
    # prepare for loop
    startTime = time.time()
    runningFlag = True
    
    
    while runningFlag:
    
        # check if current led color has timed out
        checkLEDTimer(mSerial)
        
        # poll for socket connections
        r,w,e = select.select(readable, [], [], SELECT_TIMEOUT)
        for rs in r:
             if rs is serversocket: # is it the server
                c,a = serversocket.accept()
                # print('\r{}:'.format(a),'connected')
                readable.append(c) # add the client
             else:
                # read from a client, and parse the command
                buf = rs.recv(MAX_LENGTH)
                if not buf:
                    # print('\r{}:'.format(rs.getpeername()),'disconnected')
                    readable.remove(rs)
                    rs.close()
                else:
                    print ("state: ", kStateStrings[currentState], " input: ",buf)
                    if b"quit" in buf:
                          runningFlag = False
                    else:
                         for token in kTokenInputMap:
                              if token[0] in buf:
                                   transitionToNewState(mSerial,token[1])
                                   break
        
        # check if overall timeout (so we don't run forever)
        if ((time.time() - startTime) > kOverallTimeOut):
             runningFlag = False
            

    # clean-up
   #  serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()
    allOff(mSerial)
    mSerial.close()