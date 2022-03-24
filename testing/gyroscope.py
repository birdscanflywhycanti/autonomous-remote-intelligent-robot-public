"""
Rotate given angle, tracked using gyroscope.
"""

import ThunderBorg
import time
import math
import sys

import board
import adafruit_mpu6050

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()
# TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
TB.Init()
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print(
            "No ThunderBorg at address %02X, but we did find boards:" % (TB.i2cAddress)
        )
        for board in boards:
            print("    %02X (%d)" % (board, board))
        print(
            "If you need to change the I²C address change the setup line so it is correct, e.g."
        )
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()
TB.SetCommsFailsafe(False)  # Disable the communications failsafe

# Movement settings (worked out from our MonsterBorg on carpet tiles)
timeForward1m = 0.85  # Number of seconds needed to move about 1 meter
timeSpin360 = 1.10  # Number of seconds needed to make a full left / right spin
testMode = False  # True to run the motion tests, False to run the normal sequence

# Power settings
voltageIn = 12.0  # Total battery voltage to the ThunderBorg
voltageOut = (
    12.0 * 0.95
)  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# initialise gyroscope board
i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c)

# Function to spin an angle in degrees
def PerformSpin(degrees):
    if angle < 0.0:
        # Left turn
        driveLeft = -1.0
        driveRight = +1.0
        angle *= -1
    else:
        # Right turn
        driveLeft = +1.0
        driveRight = -1.0

    # Set the motors running
    TB.SetMotor1(driveRight * maxPower)
    TB.SetMotor2(driveLeft * maxPower)
    
    # poll the gyroscope for rotation
    sampling = 0.05 # poll every 0.05 seconds, fine tune to minimise overshooting target rotation
    total_rotation = 0

    while True:
        x, y, z = mpu.gyro
        print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (x, y, z))
        x, y, z = math.degrees(x), math.degrees(y), math.degrees(z)
        print("Gyro X:%.2f, Y: %.2f, Z: %.2f deg/s" % (x, y, z))

        total_rotation += (x * sampling) # increment degree rotation by current rotation velocity, devided by sampling time

        if total_rotation >= degrees:
            break   # exit once achieved target rotation

        time.sleep(sampling)

    # Turn the motors off
    TB.MotorsOff()