# # ! remove before sending
# from dronekit_sitl import SITL

# Import DroneKit-Python
from dronekit import connect, VehicleMode, time, LocationGlobalRelative
import math

#Setup option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Print out vehicle state information')
parser.add_argument('--connect',help="vehicle connection target string.")
args=parser.parse_args()

connection_string = args.connect
# ! remove before sending
# sitl = None

# # Start SITL if no connection string specified
# # This technique for starting SITL allows us to specify defffaults 
# if not connection_string:
#     sitl_defaults = '~/git/ardupilot/tools/autotest/default_params/copter.parm'
#     sitl = SITL()
#     sitl.download('copter', '3.3', verbose=True)
#     sitl_args = ['-I0', '--model', 'quad', '--home=41.714841,-86.241941,0,180']
#     sitl.launch(sitl_args, await_ready=True, restart=True)
#     connection_string = 'tcp:127.0.0.1:5760'

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
    print('Current location after takeoff is: {0},{1},{2}'.format(lat,lon,alt))

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("distance target altitude")
            break
        time.sleep(1)

arm_and_takeoff(10)

####################################
# YOUR CODE GOES HERE
####################################

# ! switch out before sending to prof. huang
startingCoords = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
# startingCoords = [41.714841,-86.241941]

def calculateEndCoords(direction, distance):
    # direction should be in radians, distance should be in m
    d = distance / 1000 # distance in km
    R = 6373.0

    drone_lat = math.radians(vehicle.location.global_relative_frame.lat)
    drone_lon = math.radians(vehicle.location.global_relative_frame.lon)

    targetLat = math.asin( math.sin(drone_lat)*math.cos(d/R) + math.cos(drone_lat)*math.sin(d/R)*math.cos(direction))
    targetLon = drone_lon + math.atan2(math.sin(direction)*math.sin(d/R)*math.cos(drone_lat), math.cos(d/R)-math.sin(drone_lat)*math.sin(targetLat))

    targetLat = math.degrees(targetLat)
    targetLon = math.degrees(targetLon)

    return [targetLat, targetLon]

def distance(waypoint):
    # radius of earth in km
    R = 6373.0

    drone_lat = math.radians(vehicle.location.global_relative_frame.lat)
    drone_lon = math.radians(vehicle.location.global_relative_frame.lon)

    lat = math.radians(waypoint[0])
    lon = math.radians(waypoint[1])

    dlat = lat - drone_lat
    dlon = lon - drone_lon

    a = math.sin(dlat / 2)**2 + math.cos(drone_lat) * math.cos(lat) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # distance between points in meters
    distance = (R * c) * 1000
    #print("Distance to waypoint: %.2f m" % distance)
    return distance

# fly 15 m northwest
def flyNW():
    startingCoords = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
    targetCoords = calculateEndCoords(math.radians(315), 15)
    print("Flying to target coordinates: %.6f, %.6f" % (targetCoords[0], targetCoords[1]))
    vehicle.simple_goto(LocationGlobalRelative(targetCoords[0], targetCoords[1]))
    distanceFlown = 0.0
    targetDistance = distance(targetCoords)
    while (targetDistance >= 1) and (vehicle.mode.name == "GUIDED"):
        targetDistance = distance(targetCoords)
        vehicle.simple_goto(LocationGlobalRelative(targetCoords[0], targetCoords[1]))
        distanceFlown = distance(startingCoords)
        if distanceFlown > 20.0:
            print("Error: distance flown >= 20 m")
            break

# fly 10 m east
def flyE():
    startingCoords = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
    targetCoords = calculateEndCoords(math.radians(90), 10)
    print("Flying to target coordinates: %.6f, %.6f" % (targetCoords[0], targetCoords[1]))
    vehicle.simple_goto(LocationGlobalRelative(targetCoords[0], targetCoords[1]))
    distanceFlown = 0.0
    targetDistance = distance(targetCoords)
    while (targetDistance >= 1) and (vehicle.mode.name == "GUIDED"):
        targetDistance = distance(targetCoords)
        vehicle.simple_goto(LocationGlobalRelative(targetCoords[0], targetCoords[1]))
        distanceFlown = distance(startingCoords)
        if distanceFlown > 20.0:
            print("Error: distance flown >= 20 m")
            break

flyNW()
flyE()

# return to starting coordinates and land
prevCoords = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
print("Returning to starting coordinates: %.6f, %.6f" % (startingCoords[0], startingCoords[1]))
vehicle.simple_goto(LocationGlobalRelative(startingCoords[0], startingCoords[1]))
distance = distance(startingCoords)
distanceFlown = 0.0
while (distance >= 1) and (vehicle.mode == "GUIDED"):
    distance = distance(startingCoords)
    vehicle.simple_goto(LocationGlobalRelative(startingCoords[0], startingCoords[1]))
    distanceFlown = distance(startingCoords)
    if distanceFlown > 20.0:
        print("Error: distance flown >= 20 m")
        break

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
