// to be run on puck
// button click cycles from OFF -> red -> green -> OFF
// received in python using bleak:
// advertising_data.manufacturer_data[1424] = b"OFF", or b"red", or b"green"

var state = "OFF";
NRF.setAdvertising({},{manufacturer: 0x0590, manufacturerData:[state]});

// cycle from OFF -> red -> green -> OFF
function changeState() {
  if (state == "OFF") {
    state = "red";
    digitalWrite(LED1,1);
    digitalWrite(LED2,0);
  }
  else if (state == "red") {
    state = "green";
    digitalWrite(LED1,0);
    digitalWrite(LED2,1);
  }
  else if (state == "green") {
    state = "OFF";
    digitalWrite(LED1,0);
    digitalWrite(LED2,0);
  }
}

// watch rising edge of button
// TODO: don't know why function gets called repeatedly 
// (or is it that advertising data is broadcast repeatedly?)
setWatch(
     function() {
           changeState();
           NRF.setAdvertising({},{manufacturer: 0x0590, manufacturerData:[state]});
     },
     BTN, {edge:"rising", debounce:50, repeat:1});
