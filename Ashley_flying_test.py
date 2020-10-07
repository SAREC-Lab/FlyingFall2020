# Import DroneKit-Python
from dronekit import connect, VehicleMode, time
import math

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

####################################
# YOUR CODE GOES HERE
####################################

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

def newLoc_meters(loc, ndist, edist):
    R = 6378137.0 #Radius of earth
    addLat = ndist/R
    addLon = edist/(R*math.cos(math.pi*loc.lat/180))
    newLat = loc.lat + (addLat * 180/math.pi)
    newLon = loc.lon + (addLon * 180/math.pi)
    return LocationGlobalRelative(newLat, newLon, loc.alt)

def goto(ndist, edist):
    targetLoc = newLoc_meters(vehicle.location.global_relative_frame, ndist, edist)
    vehicle.simple_goto(targetLoc)
    return targetLoc

def get_distance_meters(loc1, loc2):
    diffLat = loc2.lat - loc1.lat
    diffLon = loc2.lon - loc2.lon
    return math.sqrt((diffLat*diffLat) + (diffLon*diffLon)) * 1.1131915e5

print("Set default/target airspeed to 3")
vehicle.airspeed=3

initLoc = vehicle.location.global_relative_frame

print("Hover for 5 sec")
time.sleep(5)
currLat = vehicle.location.global_relative_frame.lat
currLon = vehicle.location.global_relative_frame.lon
print("  Current Lat: " + str(currLat) + ", Lon: " + str(currLon))

print("Fly NW for 20 meters")
targetLoc = goto(20/math.sqrt(2), -20/math.sqrt(2)) #gives diagonal NW of 20m
while vehicle.mode.name == 'GUIDED':
    if get_distance_meters(targetLoc, vehicle.location.global_relative_frame) < 1:
        break
    time.sleep(1)
currLat = vehicle.location.global_relative_frame.lat
currLon = vehicle.location.global_relative_frame.lon
print("   Current Lat: " + str(currLat) + ", Lon: " + str(currLon))

print("Increase altitude to 15 meters")
point = LocationGlobalRelative(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon, 15)
vehicle.simple_goto(point)
while vehicle.mode.name == 'GUIDED':
    if get_distance_meters(point, vehicle.location.global_relative_frame) < 1:
        break
    time.sleep(1)
currLat = vehicle.location.global_relative_frame.lat
currLon = vehicle.location.global_relative_frame.lon
print("   Current Lat: " + str(currLat) + ", Lon: " + str(currLon))

print("Fly East for 20 meters")
targetLoc = goto(0, 20) # straight E 20 m
while vehicle.mode.name == 'GUIDED':
    if get_distance_meters(targetLoc, vehicle.locaiton.global_relative_frame) < 1:
        break
    time.sleep(1)
currLat = vehicle.location.global_relative_frame.lat
currLon = vehicle.location.global_relative_frame.lon
print("    Current Lat: " + str(currLat) + ", Lon" + str(currLon))

print("Fly back to original position")
point = LocationGlobalRelative(initLoc.lat, initLoc.lon, 15)
vehicle.simple_goto(point)
while vehicle.mode.name == 'GUIDEDE':
    if get_distance_meters(point, vehicle.location.global_relative_frame) < 1:
        break
    time.sleep(1)
currLat = vehicle.location.global_relative_frame.lat
currLon = vehicle.location.global_relative_frame.lon
print("    Current Lat: " + str(currLat) + ", Lon" + str(currLon))


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
