from math import radians, sin, cos, sqrt, asin
from gps import * 
import os 
import smbus
import time 
import threading 
import math
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
bus = smbus.SMBus(1)
address = 0x1e

#Setup GPIO input pins
#GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Setup GPIO output pins
GPIO.setup(10, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(7, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(8, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT, pull_up_down=GPIO.PUD_UP)

#Emergency shutdown
def motorsOff(channel): #turn off all relays when exiting
	GPIO.output(10, 1)
	GPIO.output(9, 1)
	GPIO.output(11, 1)
	GPIO.output(7, 1)
	GPIO.output(8, 1)
	GPIO.output(25, 1)
	GPIO.output(24, 1)
	GPIO.output(23, 1)
	print "Motors off"

def modeSelect(channel): #set autonomous or manual mode
	print "Mode selected"

def emergencyStop(channel): #set motors to off, cleanup GPIO and poweroff pi
	print "Emergency stop button pressed"
	leftspeed=0
	rightspeed=0
	motorsOff(0)
	GPIO.cleanup()
	os.system('shutdown now -h')
	exit()
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
#increase right by 1, if right = 7 and left doesn't = 0, decrease left by 1
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
def setSpeed():
	global rightspeed, leftspeed
	if rightspeed==3:
		GPIO.output(10,0)
                GPIO.output(9,0)
                GPIO.output(11,0)
                GPIO.output(7,0)
		print "Set Right:",rightspeed
	elif rightspeed==2:
		GPIO.output(10,1)
                GPIO.output(9,0)
                GPIO.output(11,0)
                GPIO.output(7,0)
                print "Set Right:",rightspeed
	elif rightspeed==1:
                GPIO.output(10,1)
                GPIO.output(9,1)
                GPIO.output(11,0)
                GPIO.output(7,0)
                print "Set Right:",rightspeed
	elif rightspeed==0:
                GPIO.output(10,1)
                GPIO.output(9,1)
                GPIO.output(11,1)
                GPIO.output(7,1)
                print "Set Right:",rightspeed
	elif rightspeed==-1:
                GPIO.output(10,1)
                GPIO.output(9,1)
                GPIO.output(11,0)
                GPIO.output(7,1)
                print "Set Right:",rightspeed
	elif rightspeed==-2:
                GPIO.output(10,1)
                GPIO.output(9,0)
                GPIO.output(11,0)
                GPIO.output(7,1)
                print "Set Right:",rightspeed
	elif rightspeed==-3:
                GPIO.output(10,0)
                GPIO.output(9,0)
                GPIO.output(11,0)
                GPIO.output(7,1)
                print "Set Right:",rightspeed
	if leftspeed==3:
		GPIO.output(8,0)
                GPIO.output(25,0)
                GPIO.output(24,0)
                GPIO.output(23,0)
                print "Set Left:",leftspeed
        elif leftspeed==2:
                GPIO.output(8,1)
                GPIO.output(25,0)
                GPIO.output(24,0)
                GPIO.output(23,0)
                print "Set Left:",leftspeed
        elif leftspeed==1:
                GPIO.output(8,1)
		GPIO.output(25,1)
		GPIO.output(24,0)
		GPIO.output(23,0)
                print "Set Left:",leftspeed
        elif leftspeed==0:
                GPIO.output(8,1)
		GPIO.output(25,1)
		GPIO.output(24,1)
		GPIO.output(23,1)
                print "Set Left:",leftspeed
	elif leftspeed==-1:
		GPIO.output(8,1)
                GPIO.output(25,1)
                GPIO.output(24,0)
                GPIO.output(23,1)
                print "Set Left:",leftspeed
        elif leftspeed==-2:
                GPIO.output(8,1)
                GPIO.output(25,0)
                GPIO.output(24,0)
                GPIO.output(23,1)
                print "Set Left:",leftspeed
        elif leftspeed==-3:
		GPIO.output(8,0)
                GPIO.output(25,0)
                GPIO.output(24,0)
                GPIO.output(23,1)
                print "Set Left:",leftspeed

#Function that returns the angle remaining to get to desired bearing.
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

#Haversine function to return heading and distance between two coordinates
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

if __name__ == '__main__':
	#Launch GPSD
	print("Launching gpsd...")
	os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
	time.sleep(2)
	gpsc = GpsController()
	print "Loading waypoints from file"
	#Add kml file loading into linked list here
	try:
		gpsc.start()
		while True:
			#Replace true below with manual/auto switch check
			while True:
				dlat =  46.219173
				dlon = -76.125144
				currentBearing = getBearing()
				clat = gpsc.fix.latitude
				clon =  gpsc.fix.longitude
				print "============================================================"
				print "Autonomous mode"
				print "============================================================"
				print "Current Lat: " +str(clat)
				print "Current Lon: " +str(clon)
				print "Next Lat: " +str(dlat)
				print "Next Lon: " +str(dlon)
				print "Distance remaining: " + str(int(haversine(clat,clon,dlat,dlon)))+ "m"
				print "Current Bearing: " + str(currentBearing)
				print "Desired Bearing: " + str(bearing(clat, clon,dlat, dlon))
				print "Turn Offset: " + str(turnOffset(currentBearing,bearing(clat,clon,dlat,dlon)))
				print "UTC Time: ", gpsc.utc[11:-5]
				print "GPS Error: "+ str(gpsc.fix.epx) + "m"
				if gpsc.fix.mode == 0:
					print "No mode"
				elif gpsc.fix.mode == 1:
					print "No Fix"
				elif gpsc.fix.mode == 2:
					print "2D Lock"
				elif gpsc.fix.mode == 3:
					print "3D Lock"
				#print "sats ", gpsc.satellites
				time.sleep(1)
				os.system('clear') 
			#change to check automan switch	
			while False:
				motorsOff(0)
				while(GPIO.input(AUTOMAN) ==0):
					if(GPIO.input(22) ==0):
						emergencyStop(0)
					if(GPIO.input(17) ==0):
						joyUp(0)
					if(GPIO.input(3) ==0):
						joyDown(0)
					if(GPIO.input(2) ==0):
						joyLeft(0)
					if(GPIO.input(4) ==0):
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
