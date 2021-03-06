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

time.sleep(5)

import math
r_earth = 6378.137

def get_northwest_coords(latitude, longitude, dx, dy):
    dx = dx / 1000
    dy = dy / 1000
    new_latitude = latitude + (dy / r_earth) * (180 / math.pi)
    new_longitude = longitude + (dx / r_earth) * (180 / math.pi) / math.cos(latitude * math.pi/180)
    return new_latitude, new_longitude

def get_east_coords(latitude, longitude, dx):
    dx = dx / 1000
    new_longitude = longitude + (dx / r_earth) * (180 / math.pi) / math.cos(latitude * math.pi/180)
    return new_longitude


def goto_function(vehicle, new_lat, new_lon):
    # get current coords
    lat = vehicle.location.global_relative_frame.lat
    lon = vehicle.location.global_relative_frame.lon
    alt = vehicle.location.global_relative_frame.alt

    point1 = LocationGlobalRelative(new_lat, new_lon, 10)
    print("TARGET COORDINATES")
    print(new_lat)
    print(new_lon)

    vehicle.simple_goto(point1)
    while (vehicle.mode == "GUIDED"):
        lat_distance = abs(new_lat - vehicle.location.global_relative_frame.lat)
        lon_distance = abs(new_lon - vehicle.location.global_relative_frame.lon)
        if (lat_distance < 0.000005) and (lon_distance < 0.000005):
            break

def change_altitude(vehicle, new_alt):
    lat = vehicle.location.global_relative_frame.lat
    lon = vehicle.location.global_relative_frame.lon

    print("TARGET ALTITUDE")
    print(new_alt)

    point = LocationGlobalRelative(lat, lon, new_alt)
    vehicle.simple_goto(point)
    while (vehicle.mode == "GUIDED"):
        curr_alt = vehicle.location.global_relative_frame.alt
        if curr_alt >= new_alt*0.95:
            print("reached target altitude")
            break

print("Starting to go NW")
lat1 = vehicle.location.global_relative_frame.lat
lon1 = vehicle.location.global_relative_frame.lon
new_lat, new_lon = get_northwest_coords(lat1, lon1, 14.0, 14.0)
goto_function(vehicle, new_lat, new_lon)

print("increasing altitude")
change_altitude(vehicle, 15)

print("Starting to go east")
lat = vehicle.location.global_relative_frame.lat
lon = vehicle.location.global_relative_frame.lon
new_lon = get_east_coords(lat, lon, 20.0)
goto_function(vehicle, lat, new_lon)

print("Going back to original coordinates")
goto_function(vehicle, lat1, lon1)
change_altitude(vehicle, 10)




# Check that you are using proper GOTO commands that are
# executed in a loop with the following logic:
#def fly_northwest(target):
#    print the target coordinates so we know what is happening
#    simple goto command
#    while loop must include while vehicle.mode="GUIDED"
#        check distance to target
#        if close to target
#            break 
#
# You can call your function for each waypoint
# SANITY CHECK that you don't go farther than 20 meters from your starting waypoint.
# I'm somehow against anyone trying to fly to Australia during our flight tests!

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
