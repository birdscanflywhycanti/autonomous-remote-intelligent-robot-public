# Autonomous Remote Intelligent Robot
![D* Lite example](/.github/images/example.gif)
![Robot navigating around a person](/.github/images/Avoid.gif)

## Participants
Zachary - [@Cutwell](https://github.com/Cutwell)
Ivan - [@luckychan12](https://github.com/luckychan12)

## Link to Video:

## Project Description 
We identified an emerging niche in autonomous robotics. Security and routine inspections of inaccessible facilities (due to distance or time of day) are often performed at the expense of human agents. We followed the state of the art developments from companies such as Boston Dynamics to develop our robot capable of autonomous behaviour and suitable for performing simple surveillance tasks.


### Robot navingating around somebody stepping infront of it:
![Robot navigating around a person](/.github/images/Avoid.gif)

## How the main program loop works:
First, the program initialises the D* Lite Algorithm by parsing the initial environment.
An input matrix is passed into the program, which details where any known obstacles are and how large the accessible environment is. 
This matrix is then converted into a graph of interconnected nodes. 
The program then initialises the weights of each node in the graph to represent any obstacles in the initial input matrix.
After this, the program enters the main execution loop. 
First, it calculates the next node to be visited. 
The robot then checks to see if the next node is accessible using the ultrasonic sensors. 
If the node is not accessible, the robot marks and updates this within its internal graph before recalculating the following shortest path. 
If the next node to be visited is available, the robot drives to the following location and updates the algorithm of its current position in the graph. 


## Project structure
We used a class-based structure to organise our codebase and expose individual functions.

![Project tree structure](/.github/images/project_structure.png)

We used a raspberry pi 4 for our central controller, and collected internal and external data using a MPU6050 and HCSR04 sensor.

![Project tree structure](/.github/images/hardware_structure.png)

## What makes your program special and how does it compare to similar things?
While other artefacts in the field make use of expensive robotic components, the Thunderborg robot is relatively inexpensive and saves cost with the sensor components used. Our project focuses on maximising performance and overcoming these hardware-based constraints.

## How to setup / run the program
- To use this product, it is assumed that you have a Thunderborg robot, equipped with a Raspberry Pi, HCSR04 Ultrasonic Sensor, a MPU6050 Gyroscope/Accelerometer, and Python 3.X installed.

1. First, you must copy the `/src` directory into the robot. 
2. Then you need to install the packages listed in `requirements.txt`.
3. You can then run `src/demo.py` to start the program.

The program parameters can be set in the `instructions.json` file. Here you can set the initial world dimensions and the locations of the start and goal positions. 

### Example instructions.json
```json
{
    "matrix": [ // define a long corridor environment
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ],
    "unit_size": 1.5,   // unit size of 1.5 (approx 50cm)
    "start": "x2y12",   // starting coordinates (assumes oriented North)
    "instructions": [   // visit this nodes and perform a door open/close check
        {
            "goal": "x0y6", // visit this node
            "final_rotation": -90   // rotate -90 relative to North
        },
        {
            "goal": "x4y0", // visit this node
            "final_rotation": 90    // rotate 90 degrees relative to North
        }
    ]
}
```
### The program executing the example instructions.json file
![D* Lite example](/.github/images/corridor.gif)
## Packages Used:
See our `requirements.txt` for a list of third-party packages used.
