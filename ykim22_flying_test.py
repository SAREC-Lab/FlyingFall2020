# Import DroneKit-Python
from dronekit import connect, VehicleMode, time
from geopy import Point
from geopy.distance import geodesic

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
####################################

# Check that you are using proper GOTO commands that are
# executed in a loop with the following logic:
# def my_goto_function(target):
#    print the target coordinates so we know what is happening
#    simple goto command
#    while loop must include while vehicle.mode="GUIDED"
#        check distance to target
#        if close to target
#            break 

# Input:    starting coordinates, distance (km), bearing (N=0, E=90, S=180, W=270)
# Output:   target coordinates (as geopy.point.Point)
def find_point(start, d, bearing):
    return geodesic(kilometers=d).destination(Point(start[0], start[1]), bearing)

def find_distance(a, b):
    return geodesic(a, b).km

home_coords = (41.714436, -86.241713, 0)
vehicle.airspeed = 2


# Fly NW for 20m
point_nw20 = find_point((home_coords[0], home_coords[1]), 0.02, 315)
point_nw20 = LocationGlobalRelative(point_nw20.latitude, point_nw20.longitude, 10)

print("Vehicle heading towards: " + str(point_nw20.lat) + " " + str(point_nw20.lon))
vehicle.simple_goto(point_nw20, groundspeed=5)

current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode == "GUIDED" and (find_distance((home_coords[0], home_coords[1]), current_location) < 0.019):
    current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    d = find_distance((home_coords[0], home_coords[1]), current_location)
    print("Distance: " + str(d) + " Ground Speed: " + str(vehicle.groundspeed))


# Increase altitude to 15m
altitude = 15
point_higher = LocationGlobalRelative(current_location[0], current_location[1], altitude)

print("Vehicle rising to: " + str(altitude))
vehicle.simple_goto(point_higher)

current_altitude = vehicle.location.global_relative_frame.alt
while vehicle.mode == "GUIDED" \
    and (current_altitude >= (altitude * 0.95)) \
    and (find_distance((home_coords[0], home_coords[1]), current_location) < 0.019):
    current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    current_altitude = vehicle.location.global_relative_frame.alt
    d = find_distance((home_coords[0], home_coords[1]), current_location)
    print("Distance: " + str(d) + " Ground Speed: " + str(vehicle.groundspeed) + " Altitude: " + str(current_altitude))


# Fly E for 20m
point_e20 = find_point(current_location, 0.02, 90)
point_e20 = LocationGlobalRelative(point_e20.latitude, point_e20.longitude, current_altitude)

print("Vehicle heading towards: " + str(point_e20.lat) + " " + str(point_e20.lon))
vehicle.simple_goto(point_e20, groundspeed=5)

current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode == "GUIDED" \
    and (find_distance((point_nw20.lat, point_nw20.lon), current_location) < 0.019) \
    and (find_distance((home_coords[0], home_coords[1]), current_location) < 0.019):
    current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    d = find_distance((home_coords[0], home_coords[1]), current_location)
    print("Distance: " + str(d) + " Ground Speed: " + str(vehicle.groundspeed))


# Fly back home to final altitude of 10m
print("Returning to Launch")
point_home = LocationGlobalRelative(home_coords[0], home_coords[1], 10)

print("Vehicle heading back home towards: " + str(point_home.lat) + " " + str(point_home.lon))
vehicle.simple_goto(point_home, groundspeed=5)

current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
while vehicle.mode == "GUIDED" and (find_distance((home_coords[0], home_coords[1]), current_location) > 0.008):
    current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    current_altitude = vehicle.location.global_relative_frame.alt
    d = find_distance((home_coords[0], home_coords[1]), current_location)
    print("Distance: " + str(d) + " Ground Speed: " + str(vehicle.groundspeed) + " Altitude: " + str(current_altitude))

time.sleep(3)
current_location = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
current_altitude = vehicle.location.global_relative_frame.alt
print("Position: " + str(current_location[0]) + " " + str(current_location[1]) + " Altitude: " + str(current_altitude))
print("Ready to land")

# You can call your function for each waypoint
# SANITY CHECK that you don't go farther than 20 meters from your starting waypoint.
# I'm somehow against anyone trying to fly to Australia during our flight tests!

####################################
# Add this at the end
####################################
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
