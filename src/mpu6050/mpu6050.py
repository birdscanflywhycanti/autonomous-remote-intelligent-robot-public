# create a singleton sensor class to house gyroscope instance and provide data as thread
import logging
import math
import time
from threading import Thread

import adafruit_mpu6050
import board


class MPU6050(Thread):
    def __init__(self):
        Thread.__init__(self)

        # initialise gyroscope board
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.mpu = adafruit_mpu6050.MPU6050(i2c)

        self.gyro = None
        self.acceleration = None

        self.poll = 0.05  # poll every <self.poll> seconds

        self.abs_z = 0     # preprocessing to save duplicate instructions
        self.z = 0
        self.orientation = 0
        self.orientation_flag = False

    def run(self):
        """ Update loop to poll MPU sensor for gyro and accelerometer data.
        
        """
        
        while True:
            self.gyro = self.mpu.gyro
            self.acceleration = self.mpu.acceleration
            
            if self.orientation_flag:
                self.gyroscopic()

            time.sleep(self.poll)

    def gyroscopic(self):
        """ Update internal orientation, for calculating future rotations.
        
        """

        logging.debug(f"orientation: {self.orientation}")
        
        x, y, z = self.mpu.gyro
        self.abs_z = abs(math.degrees(z))
        self.z = math.degrees(z)
        
        self.orientation += -self.z * self.poll

        if self.orientation >= 360:
            self.orientation -= 360
        elif self.orientation < 0:
            self.orientation += 355

if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(filename="logging_mpu6050", filemode="a", format='%(asctime)s - %(message)s', level=logging.DEBUG)

    # initialise mpu6050 board
    mpu = MPU6050()
    mpu.setName("MPU6050")
    mpu.start()

    while True:
        logging.debug(f"orientation: {mpu.orientation}, z: {mpu.z}")
        #logging.debug(f"accelerometer: {mpu.acceleration}\ngyro: {mpu.gyro}")
