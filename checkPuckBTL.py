# python3 libraries:
# pip3 install bleak -- for low energy bluetooth
# pip3 install requests -- for posting to server

# LOOK AT
# https://github.com/FiachraBarry99/BlueMaestroAPI/blob/main/BlueMaestroAPI.py
# https://bleak.readthedocs.io/en/latest/api/scanner.html?highlight=register_detection_callback#bleak.BleakScanner

import asyncio
import requests

from bleak import BleakScanner
# from urllib.parse import urlencode
# from urllib.request import Request, urlopen

local_server_url = "http://127.0.0.1:10007"

puck_service_uuids = ['6e400001-b5a3-f393-e0a9-e50e24dcca9e']

current_state = b"OFF"

async def main():
    stop_event = asyncio.Event()
    
    # TODO: add something that calls stop_event.set()

    def callback(device, advertising_data):
        # TODO: do something with incoming data
        global current_state
        print(device)
        puck_setting = advertising_data.manufacturer_data[1424]
        if (puck_setting != b"OFF" and current_state != puck_setting):
          print(advertising_data.manufacturer_data[1424])
          try:
               response = requests.post(local_server_url, data=puck_setting,timeout=1)
               current_state = puck_setting
               print(response)
          except requests.exceptions.Timeout:
               # Maybe set up for a retry, or continue in a retry loop
               current_state = puck_setting
               print("timeout")
          except requests.exceptions.TooManyRedirects:
               # Tell the user their URL was bad and try a different one
               print("too many redirects")
          except requests.exceptions.RequestException as e:
               # catastrophic error. bail.
               raise SystemExit(e)
               
           
        pass

    async with BleakScanner(callback,puck_service_uuids) as scanner: #,[puck_UUID]
        ...
        # Important! Wait for an event to trigger stop, otherwise scanner
        # will stop immediately.
        await stop_event.wait()

    # scanner stops when block exits
    ...

asyncio.run(main())
