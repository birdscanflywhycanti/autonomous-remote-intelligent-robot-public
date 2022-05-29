# Autonomous Remote Intelligent Robot
## Link to Video:

## Project Description 

### Participants
Zachary - [@Cutwell](https://github.com/Cutwell)

Ivan - [@luckychan12](https://github.com/luckychan12)

## Packages Used:

## Feature Showoff

## How to use:

## How does the program code work?

## How do the functions fit together

## What makes your program special and how does it compare to similar things?

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
