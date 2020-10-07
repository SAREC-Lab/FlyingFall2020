"""
Title:      DelleDonne_flying_test.py
Author:     Joe Delle Donne
Date:       10/06/2020
"""

# Import DroneKit-Python
from dronekit import connect, Vehicle, VehicleMode, time, LocationGlobalRelative
from math import *

# Setup option parsing to get connection string
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

# Function that returns the difference in meters between two coordinate locations
def get_distance_meters(locationA, locationB):
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
    return distance

# Function that takes in a starting location, difference in x, and difference in y, and outputs new coordinates
def get_new_coordinates(start, dx, dy):
    r_earth = 6373000.0
    new_latitude  = start.lat  + (dy / r_earth) * (180 / pi)
    new_longitude = start.lon + (dx / r_earth) * (180 / pi) / cos(start.lat * pi/180)
    return LocationGlobalRelative(new_latitude, new_longitude, 10)

# Goto function that has the drone fly to a target location
def goto(drone, target):

    # Get drone location and display
    drone_location = drone.location.global_relative_frame
    print("\nDrone location:  {}, {}".format(drone_location.lat, drone_location.lon))
    print("Flying to target: {}, {}".format(target.lat, target.lon))

    # Go to the target location
    drone.simple_goto(target)

    # Drone location progress loop
    while drone.mode == "GUIDED":

        # Print distance to target
        distance = get_distance_meters(drone.location.global_relative_frame, target)
        print("Distance to target: {} m".format(distance))

        # Stop if the drone is within 5 meters of the target
        if distance < 5:
            break
        time.sleep(0.5)

# Fly 10-20 meters North West
start = vehicle.location.global_relative_frame
loc1 = get_new_coordinates(LocationGlobalRelative(start.lat, start.lon, 10), -10.0, 10.0)
goto(vehicle, loc1)

# Fly 10 meters East
loc2 = get_new_coordinates(LocationGlobalRelative(loc1.lat, loc1.lon, 10), 10.0, 0.0)
goto(vehicle, loc2)

# Return to starting coordinates
goto(vehicle, start)

####################################
# Add this at the end
####################################
print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND
time.sleep(10)

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
