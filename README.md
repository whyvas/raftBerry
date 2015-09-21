# raftBerry
The raftBerry is my attempt to create a fully autonomous, raspberry pi controlled electric floating dock to drive us around a lake using Google Maps GPS waypoints. The dock has a control station with the following:

Hardware:

10ft x 10ft wooden floating dock w/ 6 x 50 gallon barrels.

2 x Minn Kota Endura C2 trolling motors (30lbs of thrust each) removed head.

10 x 12v automotive relays.

8 channel sainsmart relay board.

Raspberry pi 2.

Ublox 6M serial GPS.

i2c digital compass.

2 x Large Deep cycle batteries.

2 x 12v->5v USB power supplies.

Cheapo car DVD/USB/SD card audio system with LCD display.

2 x Cheapo car speakers.

Voltmeter with LCD display.

2 x Battery cut off switches.

SPST switch for selecting battery to display on voltmeter.

SPST switch for selecting GPS or manual control.

Arcade joystick for manual control.

Arcade momentary pushbutton for shutdown.

8 x RGB leds + custom 3D printed holder for motor speed/direction display.

Software:
The code is entirely written in python. Various code snippets have been stolen from the internet. I will work to provide credit to the original authors in the near future. I've installed it on the debian wheezy version: x on a raspberry pi 2 but I suspect it would work with other devices. 

The packages required from a fresh install are: 
*****Add packages
PIP packages:
Serial port configurations:

The software launches the required gpsd daemon and uses the GPIO so it requires sudo or root to run.



