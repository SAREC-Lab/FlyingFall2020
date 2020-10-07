# Import DroneKit-Python
from dronekit import connect, VehicleMode, time, Vehicle, LocationGlobalRelative
import math
import time
import matplotlib.pyplot as plt
from geopy import distance

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

arm_and_takeoff(10)




class Location_Tracker:
    def __init__(self):

        self.x_cor = []
        self.y_cor = []

    def plot_journey(self):
        plt.plot(self.x_cor, self.y_cor, 'bo')
        plt.show()

    def add_xcor(self, x):
        self.x_cor.append(x)

    def add_ycor(self, y):
        self.y_cor.append(y)
        print(self.x_cor)
        print(self.y_cor)


def goToPoint(vehicle, point, loc):
    pos = vehicle.location.global_relative_frame
    vehicle.simple_goto(point)
    dist = distance.distance((pos.lat, pos.lon), (point.lat, point.lon)).meters
    alt_dist = abs(point.alt - pos.alt)
    while dist > 1 and vehicle.mode.name == "GUIDED" and alt_dist > .5:
        print("Distance %f" % dist)
        print(pos)
        time.sleep(.3)
        pos = vehicle.location.global_relative_frame
        alt_dist = abs(point.alt - pos.alt)
        dist = distance.distance((pos.lat, pos.lon), (point.lat, point.lon)).meters
        loc.add_xcor(pos.lon)
        loc.add_ycor(pos.lat)

def goInDirection(vehicle, direction, d, loc):
    pos = vehicle.location.global_relative_frame
    if direction == "NW":
        x = pos.lat + .01
        z = pos.lon - .01
        target_point = LocationGlobalRelative(x, z, 10)
        vehicle.simple_goto(target_point)
        cur_pos = vehicle.location.global_relative_frame
        dist = distance.distance((pos.lat, pos.lon), (cur_pos.lat, cur_pos.lon)).meters
        while dist < d and vehicle.mode.name == "GUIDED":
            print(cur_pos)
            time.sleep(.3)
            cur_pos = vehicle.location.global_relative_frame
            dist = distance.distance((pos.lat, pos.lon), (cur_pos.lat, cur_pos.lon)).meters
            loc.add_xcor(cur_pos.lon)
            loc.add_ycor(cur_pos.lat)
    if direction == "E":
        x = pos.lon + .01
        target_point = LocationGlobalRelative(pos.lat, x, 15)
        vehicle.simple_goto(target_point)
        cur_pos = vehicle.location.global_relative_frame
        dist = distance.distance((pos.lat, pos.lon), (cur_pos.lat, cur_pos.lon)).meters
        while dist < d and vehicle.mode.name == "GUIDED":
            time.sleep(.3)
            print(cur_pos)
            cur_pos = vehicle.location.global_relative_frame
            dist = distance.distance((pos.lat, pos.lon), (cur_pos.lat, cur_pos.lon)).meters
            loc.add_xcor(cur_pos.lon)
            loc.add_ycor(cur_pos.lat)

def changeAlt(vehicle, altitude_target):
    cur_location = vehicle.location.global_relative_frame
    target_point = LocationGlobalRelative(cur_location.lat, cur_location.lon, altitude_target)
    vehicle.simple_goto(target_point)
    while vehicle.mode.name == "GUIDED":
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= altitude_target * 0.95:
            print("Reached target altitude")
            break
        time.sleep(.5)

loc = Location_Tracker()

# Take off to 10 meters
arm_and_takeoff(10)

starting_pos = vehicle.location.global_relative_frame

# Hover for 5 seconds
print("Hover for 5 seconds")
time.sleep(5)

# Fly North West for 18-20 meters
print("Fly North West for 18-20 meters")
goInDirection(vehicle, "NW", 18, loc)

# Increase altitude to 15 meters
print("Increase altitude to 15 meters")
changeAlt(vehicle, 15)

# Fly East for 18-20 meters
print("Fly East for 18-20 meters")
goInDirection(vehicle, "E", 18, loc)

# Fly back to lat and lon with final altitude of 10 meters
print("Fly back to lat and lon with final altitude of 10 meters")
goToPoint(vehicle, LocationGlobalRelative(starting_pos.lat, starting_pos.lon, 10), loc)

loc.plot_journey()


print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
