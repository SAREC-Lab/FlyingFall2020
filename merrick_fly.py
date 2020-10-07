# Import DroneKit-Python
from dronekit import connect, VehicleMode, time
import math
import time
#Setup option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Print out vehicle state information')
parser.add_argument('--connect',help="vehicle connection target string.")
args=parser.parse_args()

connection_string = args.connect

# Connect to the Vehicle.
print "\nConnecting to vehicle on: %s" % connection_string
vehicle = connect(connection_string, wait_ready=False)
vehicle.wait_ready(timeout=120)

#Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print "GPS: %s" % vehicle.gps_0
print "Battery: %s" % vehicle.battery
print "Last Heartbeat: %s" % vehicle.last_heartbeat
print "Is Armable?: %s" % vehicle.system_status.state
print "Mode: %s" % vehicle.mode.name # settable

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True 
    print("Vehicle armed!")

    #Takeoff
    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
    lat = vehicle.location.global_relative_frame.lat
    lon = vehicle.location.global_relative_frame.lon
    alt = vehicle.location.global_relative_frame.alt
    print('Current location after takeoff is: {0},{1},{2}'.format(lat,lon,alt))

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


####################################
# YOUR CODE GOES HERE
####################################
def get_location(original, dNorth, dEast):
	earth_radius = 6378137.0

	dLat = dNorth/earth_radius
	dLon = dEast/(earth_radius*math.cos(math.pi*original.lat/180))

	newlat = original.lat + (dLat * 180/math.pi)
	newlon = original.lon + (dLon * 180/math.pi)
	return LocationGlobalRelative(newlat, newlon, original.alt)

def get_distance(loc1, loc2):
	dLat = loc2.lat - loc1.lat
	dLon = loc2.lon - loc1.lon
	return math.sqrt((dLat*dLat) + (dLon*dLon)) * 1.113195e5

# Check that you are using proper GOTO commands that are
# executed in a loop with the following logic:
def goto(targetLocation, gotoFunction=vehicle.simple_goto):
	#Determine where to fly the drone
	current = vehicle.location.global_relative_frame
	targetDistance = get_distance(current, targetLocation)
	#Fly the drone
	gotoFunction(targetLocation)
	#Fly until reached tolerance of destination
	while vehicle.mode.name == "GUIDED":
		#Update server
		nowLocation = vehicle.location.global_relative_frame

		#Print information
		print("Location: %s, %s, - Alt: %s" % (nowLocation.lat, nowLocation.lon, nowLocation.alt))
		#Check tolerance

		remaining = get_distance(nowLocation, targetLocation)
		if remaining <= targetDistance*0.05:
			print("Reached target")
			break
		#Sleep
		time.sleep(2)

# You can call your function for each waypoint
# SANITY CHECK that you don't go farther than 20 meters from your starting waypoint.
# I'm somehow against anyone trying to fly to Australia during our flight tests!

#TAKE OFF
arm_and_takeoff(10)

#SET AIRSPEED
vehicle.airspeed = 3

#Original starting location
home = vehicle.location.global_relative_frame

#FLY NORTHWEST < 20 METERS
target1 = get_location(vehicle.location.global_relative_frame, 14.14, -14.14)
goto(target1)

#FLY EAST 20 METERS
target2 = get_location(vehicle.location.global_relative_frame, 0, 20)
goto(target2)

#RETURN TO START
goto(home)


####################################
# Add this at the end
####################################
print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
