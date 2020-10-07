# Import DroneKit-Python
from __future__ import print_function
import time
from dronekit_sitl import SITL
from dronekit import Vehicle, VehicleMode, connect, LocationGlobalRelative


#Setup option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Print out vehicle state information')
parser.add_argument('--connect',help="vehicle connection target string.")
args=parser.parse_args()

connection_string = args.connect

if not connection_string:
    sitl_defaults = '~/git/ardupilot/tools/autotest/default_params/copter.parm'
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=35.361350, 149.165210,0,180']
    sitl.launch(sitl_args, await_ready=True, restart=True)
    connection_string = 'tcp:127.0.0.1:5760'

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
    # Don't try to arm until autopilot is ready
    #while not vehicle.is_armable:
    #    print(" Waiting for vehicle to initialise...")
    #    time.sleep(3)
    #    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    #while not vehicle.armed:
    #    print(" Waiting for arming...")
    time.sleep(5)

    print("Vehicle armed!")
    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def my_goto_function(target):
    print ('Target position is: %s' % target)
    print ('Current position of vehicle is: %s' % vehicle.location.global_frame)
    print('Traveling')
    vehicle.simple_goto(target, groundspeed=10)
    time.sleep(30)
    print ('Current position of vehicle is: %s' % vehicle.location.global_frame)

arm_and_takeoff(10)
initialLoc = LocationGlobalRelative(vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_frame.alt)

point1 = LocationGlobalRelative(vehicle.location.global_frame.lat - 0.00008, vehicle.location.global_frame.lon + 0.00008, vehicle.location.global_frame.alt)
my_goto_function(point1)

point2 = LocationGlobalRelative(vehicle.location.global_frame.lat + 0.0001, vehicle.location.global_frame.lon, vehicle.location.global_frame.alt)
my_goto_function(point2)

my_goto_function(initialLoc)

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
