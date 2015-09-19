#raftBerry 
#A python implementation of an autonomous, GPS controlled, electric floating dock. 
#Use this code at your own risk, if you intend to build this device, please be careful, I am not responsible for
#anything that happens if you use this code. The code doesn't do any kind of collision avoidance with land or 
#other crafts. Use at your own risk. This code is pieced together from many sources. Please feel free to submit
#corrections and improvements.
#see https://github.com/whyvas/raftBerry for updates, wiring diagrams and pictures.

from math import radians, sin, cos, sqrt, asin
from gps import * 
from pykml import parser
import os 
import smbus
import time 
import threading 
import math
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
bus = smbus.SMBus(1)
address = 0x1e
leftspeed = 0
rightspeed = 0

#GPIO pin definitions
AUTOMAN = 27
PORTDIR = 23
PORTLOW = 24
PORTMED = 25
PORTHIGH = 8
STARDIR = 7
STARLOW = 11
STARMED = 9
STARHIGH = 10
JOYUP = 17
JOYDOWN = 6
JOYLEFT = 5
JOYRIGHT = 4
SHUTDOWN = 22

#Setup GPIO input pins
GPIO.setup(JOYLEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYRIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOYUP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(AUTOMAN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Setup GPIO output pins
GPIO.setup(STARHIGH, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STARMED, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STARLOW, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STARDIR, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PORTHIGH, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PORTMED, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PORTLOW, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PORTDIR, GPIO.OUT, pull_up_down=GPIO.PUD_UP)

#Function to turn off all motors
def motorsOff(channel):
	GPIO.output(STARHIGH, 1)
	GPIO.output(STARMED, 1)
	GPIO.output(STARLOW, 1)
	GPIO.output(STARDIR, 1)
	GPIO.output(PORTHIGH, 1)
	GPIO.output(PORTMED, 1)
	GPIO.output(PORTLOW, 1)
	GPIO.output(PORTDIR, 1)
	print "Motors off"

#Turn off motors, cleanup GPIO and shutdown the pi
def emergencyStop(channel):
	global leftspeed,rightspeed
	print "Emergency stop button pressed"
	leftspeed=0
	rightspeed=0
	motorsOff(0)
	GPIO.cleanup()
	os.system('shutdown now -h')
	exit()

#Read joystick inputs	
def joyUp(channel):
	global leftspeed,rightspeed
	print "Joystick up"
	if leftspeed < 3:
		leftspeed+=1
	if rightspeed < 3:
			rightspeed+=1
	print'Left:',leftspeed, 'Right:',rightspeed
	setSpeed()
def joyDown(channel):
	global leftspeed, rightspeed
	print "Joystick down"
	if leftspeed > -3:
		leftspeed-=1
	if rightspeed > -3:
		rightspeed-=1
	print "Left:",leftspeed," Right:",rightspeed
	setSpeed()
def joyLeft(channel):
	print "Joystick left"
	incRight()
	print "Left:",leftspeed," Right:",rightspeed
	setSpeed()
def joyRight(channel):
	print "Joystick right"
	incLeft()
	print "Left:",leftspeed," Right:",rightspeed
	setSpeed()

#increase left by 1, if left = 7 and right doesn't = 0, decrease right by 1
def decLeft():
	global leftspeed
	if leftspeed > -3:
		leftspeed-=1
def incLeft():
	global leftspeed, rightspeed
	if leftspeed < 3:
		leftspeed+=1
	elif rightspeed > -3:
		rightspeed-=1
def incRight():
        global rightspeed, leftspeed
        if rightspeed < 3:
                rightspeed+=1
	elif leftspeed > -3:
		leftspeed-=1
def decRight():
        global rightspeed
        if rightspeed > -3:
                rightspeed-=1
                
#Set relays for direction and speed.
def setSpeed():
	global rightspeed, leftspeed
	if rightspeed==3:
		GPIO.output(STARHIGH,0)
                GPIO.output(STARMED,0)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,0)
		print "Set Right:",rightspeed
	elif rightspeed==2:
		GPIO.output(STARHIGH,1)
                GPIO.output(STARMED,0)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,0)
                print "Set Right:",rightspeed
	elif rightspeed==1:
                GPIO.output(STARHIGH,1)
                GPIO.output(STARMED,1)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,0)
                print "Set Right:",rightspeed
	elif rightspeed==0:
                GPIO.output(STARHIGH,1)
                GPIO.output(STARMED,1)
                GPIO.output(STARLOW,1)
                GPIO.output(STARDIR,1)
                print "Set Right:",rightspeed
	elif rightspeed==-1:
                GPIO.output(STARHIGH,1)
                GPIO.output(STARMED,1)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,1)
                print "Set Right:",rightspeed
	elif rightspeed==-2:
                GPIO.output(STARHIGH,1)
                GPIO.output(STARMED,0)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,1)
                print "Set Right:",rightspeed
	elif rightspeed==-3:
                GPIO.output(STARHIGH,0)
                GPIO.output(STARMED,0)
                GPIO.output(STARLOW,0)
                GPIO.output(STARDIR,1)
                print "Set Right:",rightspeed
	if leftspeed==3:
		GPIO.output(PORTHIGH,0)
                GPIO.output(PORTMED,0)
                GPIO.output(PORTLOW,0)
                GPIO.output(PORTDIR,0)
                print "Set Left:",leftspeed
        elif leftspeed==2:
                GPIO.output(PORTHIGH,1)
                GPIO.output(PORTMED,0)
                GPIO.output(PORTLOW,0)
                GPIO.output(PORTDIR,0)
                print "Set Left:",leftspeed
        elif leftspeed==1:
                GPIO.output(PORTHIGH,1)
		GPIO.output(PORTMED,1)
		GPIO.output(PORTLOW,0)
		GPIO.output(PORTDIR,0)
                print "Set Left:",leftspeed
        elif leftspeed==0:
                GPIO.output(PORTHIGH,1)
		GPIO.output(PORTMED,1)
		GPIO.output(PORTLOW,1)
		GPIO.output(PORTDIR,1)
                print "Set Left:",leftspeed
	elif leftspeed==-1:
		GPIO.output(PORTHIGH,1)
                GPIO.output(PORTMED,1)
                GPIO.output(PORTLOW,0)
                GPIO.output(PORTDIR,1)
                print "Set Left:",leftspeed
        elif leftspeed==-2:
                GPIO.output(PORTHIGH,1)
                GPIO.output(PORTMED,0)
                GPIO.output(PORTLOW,0)
                GPIO.output(PORTDIR,1)
                print "Set Left:",leftspeed
        elif leftspeed==-3:
		GPIO.output(PORTHIGH,0)
                GPIO.output(PORTMED,0)
                GPIO.output(PORTLOW,0)
                GPIO.output(PORTDIR,1)
                print "Set Left:",leftspeed

#Function that returns the angle remaining to get to desired bearing. Negative for left, positive for right.
def turnOffset(chead,dhead):
	if (chead > dhead):
		if ((chead-dhead) >= 180):
			return(360-chead+dhead)
		else:
			return((chead-dhead)*-1)
        if (chead < dhead):
                if ((dhead-chead) >= 180):
                        return((360-dhead+chead)*-1)
                else:
                        return(dhead-chead)

#Functions to read the bearing from the digital compass.
def read_byte(adr):
	return bus.read_byte_data(address, adr)
def read_word(adr):
	high = bus.read_byte_data(address, adr)
	low = bus.read_byte_data(address, adr+1)
	val = (high << 8) + low
	return val
def read_word_2c(adr):
	val = read_word(adr)
	if (val >= 0x8000):
		return -((65535 - val) + 1)
	else:
		return val
def write_byte(adr, value):
	bus.write_byte_data(address, adr, value)
def getBearing():
	write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
	write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
	write_byte(2, 0b00000000) # Continuous sampling
	scale = 0.92
	x_out = read_word_2c(3) * scale
	y_out = read_word_2c(7) * scale
	z_out = read_word_2c(5) * scale
	bearing  = math.atan2(y_out, x_out)
	if (bearing < 0):
		bearing += 2 * math.pi
	return(math.degrees(bearing))
        
#GPS Functions to get location, time, speed, etc
class GpsController(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
		self.running = False
	def run(self):
		self.running = True
		while self.running:
            # grab EACH set of gpsd info to clear the buffer
			self.gpsd.next()
	def stopController(self):
		self.running = False
	@property
	def fix(self):
		return self.gpsd.fix
	@property
	def utc(self):
		return self.gpsd.utc
	@property
	def satellites(self):
		return self.gpsd.satellites

#Haversine function to return distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
	R = 6372.8 # Earth radius in kilometers
	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)
	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))
	return R * c * 1000
	
#Function to calculate the bearing between two waypoints.
def bearing(lat1, lon1, lat2, lon2):
	rlat1 = math.radians(lat1)
	rlat2 = math.radians(lat2)
	rlon1 = math.radians(lon1)
	rlon2 = math.radians(lon2)
	dlon = math.radians(lon2-lon1)
	b = math.atan2(math.sin(dlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(dlon)) # bearing calc
	bd = math.degrees(b)
	br,bn = divmod(bd+360,360) # the bearing remainder and final bearing
	return bn
	
#Function to return the closest waypoint to current position
def findClosest():
        closestd = 10000000
        closesti = 0
        clon = gpsc.fix.latitude
        clat = gpsc.fix.longitude
        for x in range(0,len(root.Document.Folder.Placemark)):
                lat = float(str(root.Document.Folder.Placemark[x].Point.coordinates).split(",")[0])
                lon = float(str(root.Document.Folder.Placemark[x].Point.coordinates).split(",")[1])
                dist = haversine(lat,lon,clat,clon)
                #print str(lat)+ " " +str(lon)+" "+str(dist)
                if (closestd > dist):
                        closesti = x
                        closestd = dist
        #print "Closest index is: " + str(closesti)
        #print "Closest distance is: " + str(closestd)
        return closesti
#Set the speed and direction based on turn offset
def autoSpeed(turn):
	global leftspeed,rightspeed
	if (turn > 150):
		leftspeed=3
		rightspeed=-3
	if (turn > 120 and turn <= 150):
		leftspeed=3
		rightspeed=-2
	if (turn > 90 and turn <= 120):
		leftspeed=3
		rightspeed=-1
	if (turn > 60 and turn <= 90):
		leftspeed=3
		rightspeed=0
	if (turn > 30 and turn <= 60):
		leftspeed=3
		rightspeed=1
	if (turn > 10 and turn <= 30):
		leftspeed=3
		rightspeed=2
	if (turn > -10 and turn <= 10):
		leftspeed=3
		rightspeed=3
	if (turn > -30 and turn <= -10):
		leftspeed=2
		rightspeed=3
	if (turn > -60 and turn <= -30):
		leftspeed=1
		rightspeed=3
	if (turn > -90 and turn <= -60):
		leftspeed=0
		rightspeed=3
	if (turn > -120 and turn <= -90):
		leftspeed=-1
		rightspeed=3
	if (turn > -150 and turn <= -120):
		leftspeed=-2
		rightspeed=3
	if (turn < -150 ):
		leftspeed=-3
		rightspeed=3


#Read and parse KML file for GPS tour.
print "Loading waypoints from file"
root = parser.fromstring(open('LacLong.kml', 'r').read())
#Launch GPSD
print("Launching gpsd...")
os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
time.sleep(2)
	
#Main program loop
if __name__ == '__main__':
	gpsc = GpsController()
	waypoint = 0
	#Add kml file loading into linked list here
	try:
		gpsc.start()
		while True:
			#Replace true below with manual/auto switch check
			while True:
				print "Entering autonomous mode, waiting for GPS lock to find closest waypoint in list"
				while(gpsc.fix.mode!=3):
					time.sleep(1)
				waypoint = findClosest()
				os.system('clear')
				while True:
					dlat = float(str(root.Document.Folder.Placemark[waypoint].Point.coordinates).split(",")[1])
					dlon = float(str(root.Document.Folder.Placemark[waypoint].Point.coordinates).split(",")[0])
					currentBearing = getBearing()
					clat = gpsc.fix.latitude
					clon = gpsc.fix.longitude
					print "============================================================"
					print "raftBerry Autonomous mode"
					print "============================================================"
					print "Current Lat: " +str(clat)
					print "Current Lon: " +str(clon)
					print "Waypoint Lat: " +str(dlat)
					print "Waypoint Lon: " +str(dlon)
					print "Waypoint Index: " + str(waypoint)
					print "Waypoint Distance: " + str(int(haversine(clat,clon,dlat,dlon)))+ "m"
					print "Current Bearing: " + str(currentBearing)
					print "Waypoint Bearing: " + str(bearing(clat, clon,dlat, dlon))
					print "Turn Offset: " + str(turnOffset(currentBearing,bearing(clat,clon,dlat,dlon)))
					print "UTC Time: ", gpsc.utc[11:-5]
					print "GPS Error: "+ str(gpsc.fix.epx) + "m"
					if gpsc.fix.mode == 0:
						print "GPS Status: No mode"
					elif gpsc.fix.mode == 1:
						print "GPS Status: No Fix"
					elif gpsc.fix.mode == 2:
						print "GPS Status: 2D Lock"
					elif gpsc.fix.mode == 3:
						print "GPS Status: 3D Lock"
					print "Closest waypoint: " +str(findClosest())
					print "Port motor speed: "+ str(leftspeed)
					print "Starboard motor speed: "+str(rightspeed)
					autoSpeed(turnOffset(currentBearing,bearing(clat,clon,dlat,dlon)))
					if (int(haversine(clat,clon,dlat,dlon)) < 10):
						if (waypoint < len(root.Document.Folder.Placemark)):
							waypoint+=1
						else:
							print "At the end of the loop"
							motorsOff()
						
					print "============================================================"
					time.sleep(1)
					os.system('clear') 
			#change to check automan switch	
			while False:
				motorsOff(0)
				while(GPIO.input(AUTOMAN) ==0):
					if(GPIO.input(SHUTDOWN) ==0):
						emergencyStop(0)
					if(GPIO.input(JOYUP) ==0):
						joyUp(0)
					if(GPIO.input(JOYDOWN) ==0):
						joyDown(0)
					if(GPIO.input(JOYLEFT) ==0):
						joyLeft(0)
					if(GPIO.input(JOYRIGHT) ==0):
						joyRight(0)
					time.sleep(.5)
	

#Ctrl C
	except KeyboardInterrupt:
		print "\nKeyboard interrupt caught, cleaning GPIO and exiting."
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise
	finally:
		print "Cleaning up GPIO"
		GPIO.cleanup()
		print "Stopping gps controller"
		gpsc.stopController()
		gpsc.join()
		print "Done"
