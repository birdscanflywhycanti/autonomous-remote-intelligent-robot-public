#!/usr/bin/env python
# coding: Latin-1

# Simple example of a motor sequence script

# Import library functions we need
import ThunderBorg3
import time
import math
import sys

# Setup the ThunderBorg
TB = ThunderBorg3.ThunderBorg()
#TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
TB.Init()
if not TB.foundChip:
    boards = ThunderBorg3.ScanForThunderBorg()
    if len(boards) == 0:
        print 'No ThunderBorg found, check you are attached :)'
    else:
        print 'No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'TB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
TB.SetCommsFailsafe(False)             # Disable the communications failsafe

# Movement settings (worked out from our MonsterBorg on carpet tiles)
timeForward1m = 0.85                    # Number of seconds needed to move about 1 meter
timeSpin360   = 1.10                    # Number of seconds needed to make a full left / right spin
testMode = False                        # True to run the motion tests, False to run the normal sequence

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    max_power = 1.0
else:
    max_power = voltageOut / float(voltageIn)

# Function to perform a general movement
def PerformMove(driveLeft, driveRight, numSeconds):
    # Set the motors running
    TB.SetMotor1(driveRight * max_power)
    TB.SetMotor2(driveLeft * max_power)
    # Wait for the time
    time.sleep(numSeconds)
    # Turn the motors off
    TB.MotorsOff()

# Function to spin an angle in degrees
def PerformSpin(angle):
    if angle < 0.0:
        # Left turn
        driveLeft  = -1.0
        driveRight = +1.0
        angle *= -1
    else:
        # Right turn
        driveLeft  = +1.0
        driveRight = -1.0
    # Calculate the required time delay
    numSeconds = (angle / 360.0) * timeSpin360
    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)

# Function to drive a distance in meters
def PerformDrive(meters):
    if meters < 0.0:
        # Reverse drive
        driveLeft  = -1.0
        driveRight = -1.0
        meters *= -1
    else:
        # Forward drive
        driveLeft  = +1.0
        driveRight = +1.0
    # Calculate the required time delay
    numSeconds = meters * timeForward1m
    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)

# Run test mode if required
if testMode:
    # Show settings
    print 'Current settings are:'
    print '    timeForward1m = %f' % (timeForward1m)
    print '    timeSpin360 = %f' % (timeSpin360)
    # Check distance
    raw_input('Check distance, Press ENTER to start')
    print 'Drive forward 50cm'
    PerformDrive(+0.5)
    raw_input('Press ENTER to continue')
    print 'Drive reverse 50cm'
    PerformDrive(-0.5)
    # Check spinning
    raw_input('Check spinning, Press ENTER to continue')
    print 'Spinning left'
    PerformSpin(-360)
    raw_input('Press ENTER to continue')
    print 'Spinning Right'
    PerformSpin(+360)
    print 'Update the settings as needed, then test again or disable test mode'
    sys.exit(0)

### Our sequence of motion goes here ###

# Draw a 40cm square
for i in range(4):
    PerformDrive(+0.4)
    PerformSpin(+90)

# Move to the middle of the square
PerformSpin(+45)
distanceToOtherCorner = math.sqrt(0.4**2 + 0.4**2) # Pythagorean theorem
PerformDrive(distanceToOtherCorner / 2.0)
PerformSpin(-45)

# Spin each way inside the square
PerformSpin(+360)
PerformSpin(-360)

# Return to the starting point
PerformDrive(-0.2)
PerformSpin(+90)
PerformDrive(-0.2)
PerformSpin(-90)