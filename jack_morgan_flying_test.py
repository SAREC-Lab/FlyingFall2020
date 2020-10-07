# Import DroneKit-Python
from __future__ import print_function
import time
from geopy.distance import geodesic
from dronekit import connect, VehicleMode, LocationGlobalRelative
import math
#Setup option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Print out vehicle state information')
parser.add_argument('--connect',help="vehicle connection target string.")
args=parser.parse_args()

connection_string = args.connect

# Connect to the Vehicle.
print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=False)
vehicle.wait_ready(timeout=120)

#Get some vehicle attributes (state)
print("Get some vehicle attribute values:")
print("GPS: %s" % vehicle.gps_0)
print("Battery: %s" % vehicle.battery)
print("Last Heartbeat: %s" % vehicle.last_heartbeat)
print("Is Armable?: %s" % vehicle.system_status.state)
print("Mode: %s" % vehicle.mode.name) # settable


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
    print('Current location after takeoff is: {0},{1},{2}'.format(lat, lon, alt))

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute immediately).
    while (vehicle.mode == "GUIDED"):
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def goto(home, vehicle, location):
    target_dist = 0.35
    while vehicle.mode == "GUIDED":
        current = vehicle.location.global_relative_frame
        lats.append(current.lat)
        lons.append(current.lon)
        vehicle.simple_goto(location)
        print(" Lat: ", current.lat, " Lon: ", current.lon, " Height: ", current.alt)
        # Break and return from function just below target altitude.
        coords = (current.lat, current.lon)
        distance = geodesic(coords, (location.lat, location.lon)).meters
        distance_to_home = geodesic(coords, (home.lat, home.lon)).meters
        print("distance: ", distance)
        h_diff = location.alt - current.alt
        dist = math.sqrt(distance**2 + h_diff**2)
        print("dist: ", dist)
        if dist < target_dist or distance_to_home > 21:
            print("Reached target location")
            break
        time.sleep(1)


def point_difference(curr, degrees, meters, height):
    alt = height
    degrees = degrees * math.pi/180
    lat = curr.lat + meters * math.cos(degrees) / 111111
    lon = curr.lon + (meters * math.sin(degrees) / math.cos(curr.lat) / 111111)
    return LocationGlobalRelative(lat, lon, alt)


def fly_to_height(vehicle, height):
    while vehicle.mode == "GUIDED":
        current = vehicle.location.global_relative_frame
        target = LocationGlobalRelative(current.lat, current.lon, height)
        vehicle.simple_goto(target)
        print("Current altitude: ", current.alt)
        if current.alt >= height * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


j = 0
arm_and_takeoff(10)
home = vehicle.location.global_relative_frame
home.alt = 10.0
while vehicle.mode == "GUIDED" and j < 5:
    time.sleep(1)
    j += 1

vehicle.airspeed = 10
print("Set airspeed to 10")

'''
fly to northwest
'''
northwest = point_difference(home, 315, 20, 10)
print(northwest)
goto(home, vehicle, northwest)

'''
fly up to 15
'''
fly_to_height(vehicle, 15)
northwest.alt = 15.0

'''
fly east
'''
east = point_difference(northwest, 90, 20, 15)
print(east)
goto(northwest, vehicle, east)

'''
return home
'''
goto(east, vehicle, home)
print("Returning home")
vehicle.mode = VehicleMode("LAND")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
