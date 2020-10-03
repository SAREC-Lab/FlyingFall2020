from __future__ import print_function
import time
from dronekit_sitl import SITL
from dronekit import Vehicle, VehicleMode, connect, LocationGlobalRelative, LocationGlobal

import math
import json
from websocket import create_connection
from drone_model import Drone_Model
ws = create_connection("ws://localhost:8000")

drone_model_object =  Drone_Model(1,0,0)

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect
sitl = None

def get_location_metres(original_location, dNorth, dEast):

            earth_radius = 6378137.0 #Radius of "spherical" earth
            #Coordinate offsets in radians
            dLat = dNorth/earth_radius
            dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

            #New position in decimal degrees
            newlat = original_location.lat + (dLat * 180/math.pi)
            newlon = original_location.lon + (dLon * 180/math.pi)
            if type(original_location) is LocationGlobal:
                targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
            elif type(original_location) is LocationGlobalRelative:
                targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
            else:
                raise Exception("Invalid Location object passed")
            return targetlocation

# Start SITL if no connection string specified
# This technique for starting SITL allows us to specify defffaults
if not connection_string:
    sitl_defaults = '~/git/ardupilot/tools/autotest/default_params/copter.parm'
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=41.714469, -86.241786,0,180']
    sitl.launch(sitl_args, await_ready=True, restart=True)
    connection_string = 'tcp:127.0.0.1:5760'
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)
print ('Current position of vehicle is: %s' % vehicle.location.global_frame)


def custom_sleep(drone_model, sleep_time):
    current_time = 0
    while(current_time<sleep_time):
        lat = vehicle.location.global_relative_frame.lat
        lon = vehicle.location.global_relative_frame.lon
        drone_model.update_status(lat,lon)
        ws.send(drone_model.toJSON())
        print('Current location is: {0},{1}'.format(lat,lon))
        time.sleep(1)
        current_time+=1

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
    lat = vehicle.location.global_relative_frame.lat
    lon = vehicle.location.global_relative_frame.lon
    print('Current location before takeoff is: {0},{1}'.format(lat,lon))
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
    lat = vehicle.location.global_relative_frame.lat
    lon = vehicle.location.global_relative_frame.lon
    print('Current location after takeoff is: {0},{1}'.format(lat,lon))

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        drone_model_object.update_status(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        ws.send(drone_model_object.toJSON())
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)




arm_and_takeoff(10)


time.sleep(5)
original_pos=vehicle.location.global_relative_frame
print("Set default/target airspeed to 3")
vehicle.airspeed = 3

print("Going towards first point for 30 seconds ...")
point1 = get_location_metres(vehicle.location.global_relative_frame, 14.1421, -14.1421)
vehicle.simple_goto(point1)
time.sleep(20)
print(point1,vehicle.location.global_relative_frame)
# sleep so we can see the change in map
#time.sleep(30)
pos=vehicle.location.global_relative_frame
print("Going towards second point for 30 seconds (groundspeed set to 10 m/s) ...")
point2 = LocationGlobalRelative(pos.lat, pos.lon, 15)
vehicle.simple_goto(point2)
print(point2,vehicle.location.global_relative_frame)
# sleep so we can see the change in map
time.sleep(5)

point3 = get_location_metres(vehicle.location.global_relative_frame, 0, 20)
vehicle.simple_goto(point3)
print(point3,vehicle.location.global_relative_frame)
time.sleep(20)

vehicle.simple_goto(original_pos)
time.sleep(20)
print(original_pos,vehicle.location.global_relative_frame)

vehicle.mode=VehicleMode("LAND")
# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()
