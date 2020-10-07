# Import DroneKit-Python
from dronekit import connect, VehicleMode, time, LocationGlobalRelative
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

####################################
# My functions
####################################

def flyHome(vehicle, point):
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

def goTowardsDIrection(vehicle, direction, d):
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

####################################
# End of my functions and classes
####################################

arm_and_takeoff(10)

####################################
# YOUR CODE GOES HERE
####################################

starting_pos = vehicle.location.global_relative_frame

print("Hover for 5 seconds")
time.sleep(5)

print("Fly North West for 20 meters")
goTowardsDIrection(vehicle, "NW", 20)

print("Increase altitude to 15 meters")
changeAlt(vehicle, 15)

print("Fly East for 20 meters")
goTowardsDIrection(vehicle, "E", 20)

print("Fly back to lat and lon with final altitude of 10 meters")
flyHome(vehicle, LocationGlobalRelative(starting_pos.lat, starting_pos.lon, 10))

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
print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

time.sleep(5)

print("Completed")
