from algorithms.a_star import a_star
from algorithms.d_star_lite import d_star_lite

from robot.accelerometer import PerformDrive
from robot.gyroscope import PerformSpin
from robot.drive import pathing, follow
from robot.mpu6050 import mpu6050
from robot.lightening import Thunder

# initialise mpu6050 board
mpu = mpu6050()
mpu.setName('mpu6050')
mpu.start()

TB = Thunder()

def main():
    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    path = a_star(matrix)

    instructions = pathing(path, 0.4)

    print(instructions)

    follow(instructions)

if __name__ == "__main__":
    main()