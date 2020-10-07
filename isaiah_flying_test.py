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
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

arm_and_takeoff(10)


################################################################################################
# function:    Get distance in meters
# parameters:  Two global relative locations
# returns:     Distance in meters
################################################################################################
def get_distance_meters(locationA, locationB):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(locationA.lat)
    lon1 = radians(locationA.lon)
    lat2 = radians(locationB.lat)
    lon2 = radians(locationB.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 1000

    # print("Distance (meters):", distance)
    return distance

def land_drone():
    vehicle.mode = VehicleMode("LAND")
    print ("LANDING....")
    time.sleep(30) 


############################################################################################
# Main functionality: Example of one NED command
############################################################################################

startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
launchLocation = startingLocation

def hover_5():
    #################################################### Hover for 5 seconds ################################################
    print('Hovering for 5 seconds:')
    print('5')
    time.sleep(1)
    stdout.write("\033[F") #back to previous line 
    stdout.write("\033[K") #clear line 
    print('4')
    time.sleep(1)
    stdout.write("\033[F") #back to previous line 
    stdout.write("\033[K") #clear line 
    print('3')
    time.sleep(1)
    stdout.write("\033[F") #back to previous line 
    stdout.write("\033[K") #clear line 
    print('2')
    time.sleep(1)
    stdout.write("\033[F") #back to previous line 
    stdout.write("\033[K") #clear line 
    print('1')
    time.sleep(1)
    stdout.write("\033[F") #back to previous line 
    stdout.write("\033[K") #clear line 
    print('')

def north_west_20():
    ############################################### Target Location 20 meters North West ####################################
    print('Move 20 meters North West')
    startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    target_lat = vehicle.location.global_relative_frame.lat + (0.00015)
    target_lon = vehicle.location.global_relative_frame.lon - (0.00015)
    target_alt = vehicle.location.global_relative_frame.alt 
    targetLocation = LocationGlobalRelative(target_lat,target_lon, target_alt)

    # Go to destination
    vehicle.simple_goto(targetLocation)

    # Just wait for it to get there!
    print("ARE WE THERE YET?")
    print('')
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    while vehicle.mode == 'GUIDED':
        stdout.write("\033[F") #back to previous line 
        stdout.write("\033[K") #clear line 
        currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        distance_to_target = get_distance_meters(currentLocation, targetLocation)
        print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))
        time.sleep(1)
        if distance_to_target <= .5:
            print('Destination Reached')
            break

    # How close did it get?
    endLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    print("Starting position: " + str(startingLocation.lat) + ", " + str(startingLocation.lon))
    print("Target position: " + str(targetLocation.lat) + ", " + str(targetLocation.lon))
    print("End position: " + str(endLocation.lat) + ", " + str(endLocation.lon))
    print('')

    ######################################################################################################################

def raise_20():
    ##################################### Raise to an altitude of 20 meters ##############################################
    print('Raise to an Altitude of 20 meters')
    startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    target_lat = vehicle.location.global_relative_frame.lat + (0.0)
    target_lon = vehicle.location.global_relative_frame.lon - (0.0)
    target_alt = 20
    targetLocation = LocationGlobalRelative(target_lat,target_lon,target_alt)

    # Go to destination
    vehicle.simple_goto(targetLocation)

    # Just wait for it to get there!
    print("ARE WE THERE YET?")
    print()
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    distance_to_target = abs(vehicle.location.global_relative_frame.alt - target_alt)
    while vehicle.mode == 'GUIDED':
        stdout.write("\033[F") #back to previous line 
        stdout.write("\033[K") #clear line 
        currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        distance_to_target = abs(vehicle.location.global_relative_frame.alt - target_alt)
        print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))
        time.sleep(1)
        if distance_to_target <= .5:
            print('Destination Reached')
            break

    # How close did it get?
    endLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    print("Starting position: " + str(startingLocation.lat) + ", " + str(startingLocation.lon))
    print("Target position: " + str(targetLocation.lat) + ", " + str(targetLocation.lon))
    print("End position: " + str(endLocation.lat) + ", " + str(endLocation.lon))
    print('')

    ######################################################################################################################

def east_20():
    ########################################### Target Location 20 meters East ###########################################
    print('Move 20 meters East')
    startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    target_lat = vehicle.location.global_relative_frame.lat + (0.0)
    target_lon = vehicle.location.global_relative_frame.lon + (0.00024)
    target_alt = vehicle.location.global_relative_frame.alt 
    targetLocation = LocationGlobalRelative(target_lat,target_lon,target_alt)

    # Go to destination
    vehicle.simple_goto(targetLocation)

    # Just wait for it to get there!
    print("ARE WE THERE YET?")
    print()
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    while vehicle.mode == 'GUIDED':
        stdout.write("\033[F") #back to previous line 
        stdout.write("\033[K") #clear line 
        currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        distance_to_target = get_distance_meters(currentLocation, targetLocation)
        print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))
        time.sleep(1)
        if distance_to_target <= .5:
            print('Destination Reached')
            break

    # How close did it get?
    endLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    print("Starting position: " + str(startingLocation.lat) + ", " + str(startingLocation.lon))
    print("Target position: " + str(targetLocation.lat) + ", " + str(targetLocation.lon))
    print("End position: " + str(endLocation.lat) + ", " + str(endLocation.lon))
    print('')

    ######################################################################################################################

def rtl_10():
    ################################# Return to launch with altitude of 10 meters ########################################
    print('Return to launch with altitude of 10 meters')
    startingLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    target_lat = launchLocation.lat
    target_lon = launchLocation.lon
    target_alt = 10
    targetLocation = LocationGlobalRelative(target_lat,target_lon,target_alt)

    # Go to destination
    vehicle.simple_goto(targetLocation)

    # Just wait for it to get there!
    print("ARE WE THERE YET?")
    print()
    currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    while vehicle.mode == 'GUIDED':
        stdout.write("\033[F") #back to previous line 
        stdout.write("\033[K") #clear line 
        currentLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        distance_to_target = get_distance_meters(currentLocation, targetLocation)
        print ('Distance:  {0}  Ground speed: {1} '.format(distance_to_target,vehicle.groundspeed))
        time.sleep(1)
        if distance_to_target <= .5:
            print('Destination Reached')
            break

    # How close did it get?
    endLocation = Location(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    print("Starting position: " + str(startingLocation.lat) + ", " + str(startingLocation.lon))
    print("Target position: " + str(targetLocation.lat) + ", " + str(targetLocation.lon))
    print("End position: " + str(endLocation.lat) + ", " + str(endLocation.lon))
    print('')

def land():
    ########################################### LAND ########################################################################
    print('Land')
    land_drone()
    print('')
    #########################################################################################################################

hover_5()
north_west_20()
raise_20()
east_20()
rlt_10()

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