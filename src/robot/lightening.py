# thunderborg motor class
import thunderborg.ThunderBorg3 as ThunderBorg # conversion for python 3
import sys

class Thunder:
    def __init__(self):
        # Setup the ThunderBorg
        self.thunder = ThunderBorg.ThunderBorg()
        self.i2cAddress = self.thunder.i2cAddress

        # self.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address
        self.thunder.Init()

        if not TB.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                print("No ThunderBorg found, check you are attached :)")
            else:
                print(
                    "No ThunderBorg at address %02X, but we did find boards:" % (self.i2cAddress)
                )
                for board in boards:
                    print("%02X (%d)" % (board, board))
                print(
                    "If you need to change the I2C address change the setup line so it is correct, e.g."
                )
                print("TB.i2cAddress = 0x%02X" % (boards[0]))
            sys.exit()
        
        self.thunder.SetCommsFailsafe(False)  # Disable the communications failsafe

        # Power settings
        voltageIn = 9.6   # Total battery voltage to the ThunderBorg

        # NOTE: limiter has lower bound to power motors, ~0.4 experimental lower bound
        limiter = 0.6     # utilise only <limiter>% of power, to slow down actions

        voltageOut = (
            12.0 * limiter
        )  # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

        # Setup the power limits
        if voltageOut > voltageIn:
            maxPower = 1.0
        else:
            maxPower = voltageOut / float(voltageIn)
    
    def Init(self):
        self.thunder.Init()

    def SetCommsFailsafe(self, bool):
        self.thunder.SetCommsFailsafe(bool)

    def SetMotor1(self, differential):
        self.thunder.SetMotor1(differential)

    def SetMotor2(self, differential):
        self.thunder.SetMotor2(differential)

    def MotorsOff(self):
        self.thunder.MotorsOff()