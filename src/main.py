from algorithms.algorithm import Algorithm
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
    input_matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    start_node = (0,0)
    end_node = (3,0)

    algorithm = Algorithm(matrix= input_matrix, start_node= start_node, end_node= end_node)
    path = algorithm.use_a_star()

    instructions = pathing(path, 0.4)
    print(instructions)
    
    follow(instructions)

if __name__ == "__main__":
    main()