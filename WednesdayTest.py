#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
simple_goto.py: GUIDED mode "simple goto" example (Copter Only)
Demonstrates how to arm and takeoff in Copter and how to navigate to points using Vehicle.simple_goto.
Full documentation is provided at http://python.dronekit.io/examples/simple_goto.html
"""

from __future__ import print_function
import time
from dronekit_sitl import SITL
from dronekit import Vehicle, VehicleMode, connect, LocationGlobalRelative

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
# This technique for starting SITL allows us to specify defffaults 
if not connection_string:
    sitl_defaults = '~/git/ardupilot/tools/autotest/default_params/copter.parm'
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=35.361350, 149.165210,0,180']
    sitl.launch(sitl_args, await_ready=True, restart=True)
    connection_string = 'tcp:127.0.0.1:5760'

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)
print ('Current position of vehicle is: %s' % vehicle.location.global_frame)

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(3)
        print("Arming motors")
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)
    
    print("Vehicle armed!")
    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(10)

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
    while (vehicle.mode.name == "GUIDED"):
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




print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()