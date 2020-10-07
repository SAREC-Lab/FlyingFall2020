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
import math

R = 6373.0

def get_distance_meters(location1, location2):
    lat1 = math.radians(location1.lat)
    lon1 = math.radians(location1.lon)
    lat2 = math.radians(location2.lat)
    lon2 = math.radians(location2.lon)

    #dlon = math.radians(lon2) - math.radians(lon1)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c * 1000

    return distance

def my_goto_function(target):
    vehicle.simple_goto(target)
    while vehicle.mode == "GUIDED":
        if get_distance_meters(vehicle.location.global_relative_frame, target) < 1:
            break
        
initial_location = LocationGlobalRelative(vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon,vehicle.location.global_relative_frame.alt)

# go 10 - 20 meters NW
print("HEADED NW")
new_latitude  = vehicle.location.global_relative_frame.lat  + ( 10/ R) * (180 / math.pi) / 1000
new_longitude = vehicle.location.global_relative_frame.lon + ( -10 / R) * (180 / math.pi) / math.cos(vehicle.location.global_relative_frame.lat * math.pi/180) / 1000
my_goto_function(LocationGlobalRelative(new_latitude,new_longitude,10))
# go 20 meters E
print("HEADED E")
new_longitude = vehicle.location.global_relative_frame.lon + ( 20 / R) * (180 / math.pi) / math.cos(vehicle.location.global_relative_frame.lat * math.pi/180) / 1000
my_goto_function(LocationGlobalRelative(new_latitude,new_longitude,10))
# RTL
print("RTL")
my_goto_function(initial_location)

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

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
