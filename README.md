# MwillCU

Server and client scripts to control an [AdaFruit Tri-Color USB Controlled Tower Light](https://www.adafruit.com/product/5125) for busy / available entry signal lights, to indicate if office occupant is "on the air" or otherwise unavailable.


[TODO: link to video demonstration]

## Hardware

- [AdaFruit Tri-Color USB Controlled Tower Light with Buzzer (Product ID: 5125)](https://www.adafruit.com/product/5125)

- [USB 3.0 Active Extension Cable 32 Feet with 5V 2A Power Adapter](https://www.amazon.com/dp/B07XHR14LJ?ref=ppx_pop_dt_b_asin_title&th=1)

[TODO: diagram of office]

## Server Installation

-  Be sure to install pyserial: ```pip3 install pyserial```

-  Launch the server: ```python MwillCU.python```

## Control

client processes should 

1. connect on port 10007, eg. ```nc 127.0.0.1 10007 hello```

2. send commands:

- ```red``` : turns light RED for kRedTimeOut, then server will automatically switch light  to YELLOW
- ```yellow``` turns light YELLOW for kYellowTimeOut, then server will automatically switch light to GREEN
- ```green``` turns light GREEN for kGreenTimeOut, then server will automatically switch light to OFF
- ```off``` turns light OFF (and never times out)
- ```quit``` tells server to turn off light and quit itself


## Elgato Stream Deck Integration

## Video Camera / Keyboard Activity Detection


# Technical Details
 
## USB Connection

https://unix.stackexchange.com/questions/117037/how-to-send-data-to-a-serial-port-and-see-any-answer

## Detect User and Camera activity:

https://stackoverflow.com/questions/31734686/detect-user-activity-in-cocoa-app-taps-clicks
https://stackoverflow.com/questions/53559121/how-to-detect-user-inactivity-in-os-x-writing-in-swift-cocoa?noredirect=1&lq=1

	To detect video camera is on:

	https://stackoverflow.com/questions/60535678/macos-detect-when-camera-is-turned-on-off


		on bigsur and below:
			log stream | grep "Post event kCameraStreamStart"

		on monterey
			log stream --predicate 'subsystem contains "com.apple.UVCExtension" and composedMessage contains "Post PowerLog"'




## Communicating via socket

https://stackoverflow.com/questions/23148278/send-commands-from-command-line-to-a-running-python-script-in-unix

https://unix.stackexchange.com/questions/336876/simple-shell-script-to-send-socket-message

https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number

https://stackoverflow.com/questions/5875177/how-to-close-a-socket-left-open-by-a-killed-program

https://stackoverflow.com/questions/45927337/recieve-data-only-if-available-in-python-sockets
        

https://serverfault.com/questions/512722/how-to-automatically-close-netcat-connection-after-data-is-sent


https://unix.stackexchange.com/questions/150385/nc-not-waiting-for-server-disconnect-on-os-x/150400#150400



## About the name

https://youtu.be/0UZ7wSXDe94?t=49
