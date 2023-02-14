import serial
import time
import socket
import select
import sys
import glob


kOverallTimeOut = 86400 # 86400000.0  # quit server after a while so we don't run forever


deviceName = 'cu.usbmodem120457001'
baudRate = 38400

# use default serial port, almost certainly not correct
serialPort = '/dev/'+ deviceName

lastCheck = time.time()

lastState = "no_motion"
 
def checkSerial(serial):

     global lastCheck
     global lastState

     if (serial.in_waiting > 0):

        # Read data out of the buffer until a carraige return / new line is found
        serialString = serial.readline()
        asciiString = serialString.decode('Ascii')
        serial.flushInput()
        
        if (asciiString != lastState):

               # Print the contents of the serial data
               print(asciiString)
               lastState = asciiString
      
        
   #   else:
#           
#           if ((time.time() - lastCheck) > 1):
#                lastCheck = time.time()
#                print("No Data")
        
# ------------------------------------------------------------- #


 
if __name__ == '__main__':

     mSerial = serial.Serial(serialPort, baudRate)

     # prepare for loop
     startTime = time.time()
     runningFlag = True


     
     while runningFlag:
    
        checkSerial(mSerial)
    
           # check if overall timeout (so we don't run forever)
        if ((time.time() - startTime) > kOverallTimeOut):
             runningFlag = False
            

     # clean-up
     #  serversocket.shutdown(socket.SHUT_RDWR)
     #  serversocket.close()
     mSerial.close()