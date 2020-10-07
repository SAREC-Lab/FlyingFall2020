# Import DroneKit-Python
from dronekit import connect, VehicleMode, time

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
    while (vehicle.mode == "GUIDED"):
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

arm_and_takeoff(10)

####################################
# YOUR CODE GOES HERE
####################################

################################################################################################
# function:    Get distance in meters
# parameters:  Two global relative locations
# returns:     Distance in meters
################################################################################################
def get_distance_meters(locationA, locationB):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(locationA.lat)
    lon1 = radians(locationA.lon)
    lat2 = radians(locationB.lat)
    lon2 = radians(locationB.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 1000

    print "Distance (meters):", distance
    return distance

def goto_target(target_location):
	while vehicle.mode.name == "GUIDED":
		vehicle.simple_goto(target_location)
		remaining_distance = get_distance_meters(vehicle.location.global_frame, target_location)
		
		#x = vehicle.location.global_frame.lat
		#y = vehicle.location.global_frame.lon
		#x_pos.append(x)
		#y_pos.append(y)

		if remaining_distance < 1:
			print("Reached target-> lat: {} lon: {} alt: {}".format(vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_frame.alt))
			break;
		time.sleep(0.5)

def adjust_altitude(height):
	while vehicle.mode.name == "GUIDED":
		
		altitudeIncrease = LocationGlobalRelative(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon, height)
		vehicle.simple_goto(altitudeIncrease)

		remaining_distance = abs(height - vehicle.location.global_frame.alt)
		print(remaining_distance)
	
		if remaining_distance < 0.10:
			location = vehicle.location.global_frame
			print("Reached target altitude {}. Lat: {}, Lon: {}".format(location.alt, location.lat, location.lon))
			break;
		time.sleep(0.5)

def goto_target_compass(current_location, north, south, east, west, final_distance):
    lat_change = 0
	lon_change = 0

	if north:
		south = False
		lat_change = 10

	if south:
		north = False
		lat_change = -10

	if east:
		west = False
		lon_change = 10


	if west:
		east = False
		lon_change = -10

	target_location = LocationGlobalRelative(current_location.lat + lat_change, current_location.lon + lon_change, current_location.alt)
	
	while vehicle.mode.name == "GUIDED":
		vehicle.simple_goto(target_location)
		remaining_distance = get_distance_meters(current_location, vehicle.location.global_frame)
		
		#x = vehicle.location.global_frame.lat
		#y = vehicle.location.global_frame.lon
		#x_pos.append(x)
		#y_pos.append(y)
		
		if remaining_distance >= final_distance:
			print("Reached target-> lat: {} lon: {} alt: {}".format(current_location.lat, current_location.lon, current_location.alt))
			break;
		time.sleep(0.5)

############################################################################################
# Main functionality: Example of one NED command
############################################################################################

vehicle, sitl = connect_virtual_vehicle(1,([41.714436,-86.241713,0]))

arm_and_takeoff(10)
vehicle.airspeed = 15
vehicle.groundspeed = 15
time.sleep(5)

startingLocation = LocationGlobalRelative(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon, vehicle.location.global_relative_frame.alt)

goto_target_compass(vehicle.location.global_relative_frame, True, False, False, True, 20)

altitudeIncrease = LocationGlobalRelative(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon, 15)

adjust_altitude(15)

goto_target_compass(vehicle.location.global_relative_frame, False, False, True, False, 20)

goto_target(startingLocation)
adjust_altitude(10)

#plt.plot(x_pos, y_pos, 'ro')
#plt.show()

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