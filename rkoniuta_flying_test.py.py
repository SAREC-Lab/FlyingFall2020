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
    while vehicle.mode == "GUIDED":
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

arm_and_takeoff(10)

####################################
# YOUR CODE GOES HERE
def print_location(v, mute = False):
    lat = v.location.global_relative_frame.lat
    lon = v.location.global_relative_frame.lon
    alt = v.location.global_relative_frame.alt
    if not mute:
        print("Current Coordinates: \n-Lat: {}, \n-Lon: {}, \n-Alt: {}".format(lat, lon, alt))
    return lat, lon, alt

def my_goto_function(vehicle, offset_lat, offset_lon, offset_alt):
    lat, lon, alt = print_location(vehicle, mute=True)
    start = (lat, lon)

    goal_lat, goal_lon, goal_alt = lat + offset_lat, lon + offset_lon, alt + offset_alt
    goal_point = LocationGlobalRelative(goal_lat, goal_lon, goal_alt)
    goal = (goal_lat, goal_lon)

    vehicle.simple_goto(goal_point)

    while vehicle.mode == "GUIDED":
        lat_temp, lon_temp, alt_temp = print_location(vehicle, mute=True)
        curr = (lat_temp, lon_temp)
        dist = distance.distance(goal, curr)
        if dist < .5 or dist > 25:
            break
        time.sleep(.5)

    time.sleep(10)

    lat, lon, alt = print_location(vehicle)
    print("TRAVEL COMPLETED: Horizontal Distanced traveled {:.2f}m".format(distance.distance(start, (lat, lon)).m))


def my_return_function(vehicle, home_lat, home_lon, home_alt):
    home = (home_lat, home_lon)
    home_point = LocationGlobalRelative(home_lat, home_lon, home_alt)
    vehicle.simple_goto(home_point)

    while vehicle.mode == "GUIDED":
        lat, lon, alt = print_location(vehicle, mute=True)
        curr = (lat, lon)
        dist = distance.distance(home, curr)
        if dist < .5 or dist > 25:
            break
        time.sleep(.5)

print("Waiting for 5 seconds")
for i in range(1, 6):
    print("waiting for 5 seconds ... {}".format(i))
    time.sleep(1)

print("Set default/target airspeed to 3")
vehicle.airspeed = 3

# ASSUMPTION: lat moves north and south, with positive changes being north
#             lon moves west and east, with positive changes being east
lat, lon, alt = print_location(vehicle, mute=True)
init_point = (lat, lon)

print("\nFLYING NW FOR 20 METERS")
my_goto_function(vehicle, .00012, -.00017, 0)

print("\nINCREASING ALT TO 15")
my_goto_function(vehicle, 0, 0, 5)

print("\nMOVING EAST FOR 20 meters")
my_goto_function(vehicle, 0, .00024, 0)

print("\nRETURNING TO ORIGINAL POSITION")
my_return_function(vehicle, lat, lon, alt)

time.sleep(10)

print("\nLANDING")
my_goto_function(vehicle, 0, 0, -10)

lat_final, lon_final, alt_final = print_location(vehicle, mute=True)
print("\n***Completed mission, final distance from origin: {:.2f}m".format(distance.distance(init_point, (lat_final, lon_final)).m))

print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

#################################################

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