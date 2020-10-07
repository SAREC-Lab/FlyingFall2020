#!/ usr / bin / env python
# -*- coding: utf-8 -*-



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


####################################
# YOUR CODE GOES HERE
####################################

import math
import os
import time
from math import sin, cos, atan2, radians, sqrt

from dronekit import Vehicle, connect, VehicleMode, LocationGlobalRelative
from dronekit_sitl import SITL

from flight_plotter import Location, CoordinateLogger, GraphPlotter
from ned_utilities import ned_controller

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


################################################################################################
# ARM and TAKEOFF
################################################################################################

# function:   	arm and takeoff
# parameters: 	target altitude (e.g., 10, 20)
# returns:	n/a

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    print("home: " + str(vehicle.location.global_relative_frame.lat))

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    while True:
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * .95:
            print("Reached target altitude")
            break
        time.sleep(1)


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

    # print("Distance (meters):", distance)
    return distance

############################################################################################
# Controlling Drones by sending meters
############################################################################################
def fly2_meters( current_lat, current_lon, m_lat, m_lon):
    R = 6373.0
    pi = math.pi
    cos = math.cos

    m = (1 / ((2 * pi / 360)*R)) / 1000  #1 meter in degree
    
    new_lat = current_lat + (m_lat*m)
    new_lon = current_lon + (m_lon*m)/cos(current_lat*(pi/180))

    return (new_lat, new_lon)
    
    


###########################################################################################
#Main functionality: Example of one NED command
###########################################################################################

vehicle, sitl = connect_virtual_vehicle(1,([41.714436,-86.241713,0])) 

## Take off to 10 meter
arm_and_takeoff(10)

## Hover for 5 sec
print("hovoring for 5 sec")
time.sleep(5)

## getting starting position
startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)


## fly2 with 14.14m west and 14.14 north
print("flying north 14.14 meters and west 14.14 meters")
time.sleep(2)
new_target = fly2_meters(vehicle.location.global_relative_frame.lat,
                         vehicle.location.global_relative_frame.lon,
                         -14.14,
                         14.14 )

targetLocation = LocationGlobalRelative(new_target[0],new_target[1],10)
vehicle.simple_goto(targetLocation)

##     ****************checking if the drone arrives or not
currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode.name == "GUIDED" and get_distance_meters(currentLocation,targetLocation) > 0.5:
    
    #keep track of the coodinates
    lats.append(vehicle.location.global_relative_frame.lat)
    lons.append(vehicle.location.global_relative_frame.lon)
    # line.set_xdata(lats)
    # line.set_ydata(lons)

    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    distance_to_target = get_distance_meters(currentLocation, targetLocation)
    print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))


## Increase alt to 15 meters
print("Increasing alt to 15 meters")
time.sleep(2)
targetLocation = LocationGlobalRelative(vehicle.location.global_relative_frame.lat,
                          vehicle.location.global_relative_frame.lon, 
                          15)
vehicle.simple_goto(targetLocation)

while(vehicle.mode.name == "GUIDED" and (15 - vehicle.location.global_relative_frame.alt) > 0.5):
    print("Current altitude: {0}".format(vehicle.location.global_relative_frame.alt))

## fly East for 20 meters
print("flying East for 20 meters")
time.sleep(2)
new_target = fly2_meters(vehicle.location.global_relative_frame.lat,
                         vehicle.location.global_relative_frame.lon,
                         20,
                         0 )

targetLocation = LocationGlobalRelative(new_target[0],new_target[1],15)
vehicle.simple_goto(targetLocation)

##     ****************checking if the drone arrives or not
currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode.name == "GUIDED" and get_distance_meters(currentLocation,targetLocation) > 0.5:
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    distance_to_target = get_distance_meters(currentLocation, targetLocation)
    print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))


## return back to original
print("returning back to original")
time.sleep(2)
targetLocation = LocationGlobalRelative(41.714436,-86.241713,10)
vehicle.simple_goto(targetLocation)

##     ****************checking if the drone arrives or not
currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode.name == "GUIDED" and get_distance_meters(currentLocation,targetLocation) > 0.5:
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    distance_to_target = get_distance_meters(currentLocation, targetLocation)
    print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))






# Check that you are using proper GOTO commands that are
# executed in a loop with the following logic:
#def my_goto_function(target):
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
print("Landing")
time.sleep(2)
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
