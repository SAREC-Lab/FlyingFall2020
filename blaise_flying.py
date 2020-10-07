# Import DroneKit-Python
# Blaise von Ohlen
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

def getLocationMeters(original_location, dNorth, dEast):
    earth_radius = 6378137.0 
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt) 
    return targetlocation

def getDistance(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def goto(destination, vehicle):
    print("Target Coords: " + str(destination))
    vehicle.simple_goto(destination)
    totalDistance = getDistance(vehicle.location.global_relative_frame, destination)
    while vehicle.mode.name == "GUIDED":
        distanceFromTarget = getDistance(vehicle.location.global_relative_frame, destination)
        if distanceFromTarget < (totalDistance * .03):
            print("Reached destination!")
            break
        time.sleep(5)

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

original_loc = vehicle.location.global_relative_frame

# Fly 20 meters to the northwest
dMove1 = 10 * math.sqrt(2)
waypoint1 = getLocationMeters(vehicle.location.global_relative_frame, dMove1, -dMove2)
goto(waypoint1, vehicle)

# Fly 20 meters to the East
waypoint2 = getLocationMeters(vehicle.locatoin.global_relative_frame, 0, 20)
goto(waypoint2, vehicle)

# Return Back
goto(original_loc, vehicle)

print("Returning to Launch")
vehicle.mode = VehicleMode("LAND")  # Note we replace RTL with LAND

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")