"""

Example for Adafruit USB tower light w/alarm
don't forget `pip3 install pyserial`


Usage:

python3 MwillCU.python [<deviceName>]

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

kOverallTimeOut = 86400000.0  # quit server after a while so we don't run forever

# serial port settings for USB
#serialPort = 'COM57'  # Change to the serial/COM port of the tower light

# deviceName likely different for every computer/device
# on mac/linux, it will be a /dev path
# can be passed in on command line
deviceName = 'cu.usbserial-4013110'  
baudRate = 9600

# byte commands sent to LED USB device
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


# index to LED states
kOff = 0
kRed = 1
kYellow = 2
kGreen = 3


# the curent LED and when it was started
currentLED = kOff
ledStartTime = 2147483647.0

# length of time that a light is left on before automatically rolling over to next light
# note: off remains in that state forever

kOffTimeOut = 2147483647.0 # never time out
kRedTimeOut = 3300.0 # 55 minutes
kYellowTimeOut = 600.0 # 10 minutes
kGreenTimeOut = 2147483647.0 # never time out

timeOuts = [0.0] * 4
timeOuts[kOff] = kOffTimeOut
timeOuts[kRed] = kRedTimeOut
timeOuts[kYellow] = kYellowTimeOut
timeOuts[kGreen] = kGreenTimeOut


# ------------------------------------------------------------- #

# server defaults

MAX_LENGTH = 4096
PORT = 10007
HOST = '127.0.0.1'

SELECT_TIMEOUT = 1



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

def setLED(serialport,ledName):

    global currentLED
    global ledStartTime
    
    # Clean up any old state
    allOff(serialport)
    if (ledName == kRed):
        sendCommand(serialport, RED_ON)
        currentLED = kRed
    elif (ledName == kYellow):
        currentLED = kYellow
        sendCommand(serialport, YELLOW_ON)
    elif (ledName == kGreen):
        currentLED = kGreen
        sendCommand(serialport, GREEN_ON)
        
    if (ledName == kOff):
        currentLED = kOff
        ledStartTime = 2147483647.0
    else:
        currentLED = ledName
        ledStartTime = time.time();
    print(currentLED,"  ", ledStartTime)
    
# ------------------------------------------------------------- #

        
def checkLEDTimer(serialport):
    global currentLED
    global ledStartTime
    global timeOuts
    
    timeNow = time.time();
  #  print(currentLED, " " , timeNow, " ", ledStartTime, "  ", timeOuts[currentLED])
    if ((timeNow - ledStartTime) > timeOuts[currentLED]):
        nextLED = currentLED + 1;
        if (nextLED > kGreen):
            nextLED = kOff
        setLED(serialport,nextLED)
               
# ------------------------------------------------------------- #

if __name__ == '__main__':
    
    # set up socketserver
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.setblocking(0)
    serversocket.bind((HOST, PORT))
    serversocket.listen(10) # how many connections requests to queue
    readable = [serversocket];
    
    
    # connect to usb serial device
    if len(sys.argv) >= 2:
          deviceName = sys.argv[1]
     
    print(deviceName)
    serialPort = '/dev/'+ deviceName
    mSerial = serial.Serial(serialPort, baudRate)

    # set light to initial state
    setLED(mSerial,currentLED)
    
    
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
                print('\r{}:'.format(a),'connected')
                readable.append(c) # add the client
             else:
                # read from a client, and parse the command
                buf = rs.recv(MAX_LENGTH)
                if not buf:
                    print('\r{}:'.format(rs.getpeername()),'disconnected')
                    readable.remove(rs)
                    rs.close()
                else:
                    if b"active" in buf:
                         if currentLED == kOff:
                              setLED(mSerial,kGreen)
                    elif b"idle" in buf:
                         setLED(mSerial,kOff)
                    elif b"red" in buf:
                         setLED(mSerial,kRed)
                    elif b"yellow" in buf:
                         setLED(mSerial,kYellow)
                    elif b"green" in buf:
                         setLED(mSerial,kGreen)
                    elif b"off" in buf:
                         setLED(mSerial,kOff)
                    elif b"quit" in buf:
                         runningFlag = False  
                    print (buf)
        
        # check if overall timeout (so we don't run forever)
        if ((time.time() - startTime) > kOverallTimeOut):
             runningFlag = False
            

    # clean-up
   #  serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()
    allOff(mSerial)
    mSerial.close()