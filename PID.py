import numpy as np
from perlin_noise import PerlinNoise, Interp
import random
import matplotlib.pyplot as plt
import tomllib

#The PID controller
def PID(target, currVal, prevErr, currInt, Kp, Kd, Ki, dt):
    err = target-currVal
    D = (err - prevErr)/dt
    I = currInt + err * dt
    control = Kp * err + Kd * D + Ki * I
    return control, err, I

#Let's make the leg as a class for ease
class Wheel:
    controlParam = 1
    #init wheel
    def __init__(self, height, speed, dt):
        self.height = height
        self.speed = speed
        self.dt = dt

    #the transfer function (here for simplicity, it's just Y(s)/X(s) = 1)
    def step(self, control):
        self.speed = control * self.controlParam
        self.height += self.speed * self.dt

#The Plant and the Controller, and outputs final heights and pitch
def system(Kp, Kd, Ki):

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    #modify these to change the timeframe and time step size
    dt = (config["simConfig"]["dt"])
    timeFrame = (config["simConfig"]["timeFrame"])

    timeSteps = int(timeFrame/dt)
    
    #modify these to changeg the terrain shape
    
    amplitude = config["terrainConfig"]["amplitude"]
    frequency = config["terrainConfig"]["frequency"]
    octaves = config["terrainConfig"]["octaves"]
    avgTerrain = config["terrainConfig"]["avgTerrain"]

    wheelFr = Wheel(10, 0, dt)
    wheelFl = Wheel(10, 0, dt)
    wheelRr = Wheel(10, 0, dt)
    wheelRl = Wheel(10, 0, dt)

    wheels = [wheelFr, wheelFl, wheelRr, wheelRl]

    time = np.arange(0, timeFrame, dt)
    terrain = np.zeros((4, timeSteps))

    #generate terrain for the legs
    noises = [PerlinNoise(random.randint(0, 10000), amplitude, frequency, octaves, interp=Interp.CUBIC) for _ in range(4)]
    for i in range(4):
        for j in range(timeSteps):
            terrain[i][j] = noises[i].get(time[j])
            terrain[i][j] += avgTerrain
    if config["terrainConfig"]["hasDrops"]:
        terrain[0][int(2/dt):] -= [2 for _ in terrain[0][int(2/dt):]]
        terrain[3][int(3.5/dt):] -= [2 for _ in terrain[3][int(3.5/dt):]]

    #Initialize datas
    heights = np.zeros((4, timeSteps))
    errs = np.zeros((4, timeSteps))
    ints = np.zeros((4, timeSteps))
    targets = np.zeros((4, timeSteps))
    heights[:,0] = [wheel.height for wheel in wheels]
    avgHeight = np.zeros(timeSteps)
    pitches = np.zeros(timeSteps)

    avgHeight[0] = (sum(heights[:,0]) + sum(terrain[:,0]))/4
    pitches[0] = (sum(heights[0:2,0]) - sum(heights[2:4,0]))/2

    #starting the sim
    for step in range(1, timeSteps):
        
        #find the targer height each leg should have
        terrainAvg = 20 - sum(terrain[:,step])/2
        targets[:,step] = [terrainAvg - wheelFl.height, terrainAvg - wheelFr.height, terrainAvg - wheelRl.height, terrainAvg - wheelRr.height]
    
        #get the control thingy
        PIDs = [PID(targets[i, step], heights[i,step-1], errs[i,step-1], ints[i,step-1], Kp, Kd, Ki, dt) for i in range(4)]
        controls = [PIDs[i][0] for i in range(4)]
        ints[:,step] = [PIDs[i][2] for i in range(4)]
        errs[:, step] = [PIDs[i][1] for i in range(4)]

        for i in range(len(wheels)):
            wheels[i].step(controls[i])
        heights[:,step] = [wheel.height for wheel in wheels]
        avgHeight[step] = (sum(heights[:,step]) + sum(terrain[:,step]))/4
        pitches[step] = (sum(heights[0:2,step]) - sum(heights[2:4,step]))/2

    return avgHeight, pitches, heights, terrain

#for running the sim without autotuner
if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    # Kp, Kd, Ki = (10, 0.10711112931380898, 5.219131502961188)
    Kp, Kd, Ki = config["PIDConfig"]["Kp"], config["PIDController"]["Kd"], config["PIDController"]["Ki"]
    avgHeight, pitch, heights, terrain = system(Kp, Kd, Ki)

    dt = config["simConfig"]["dt"]
    timeFrame = config["simConfig"]["timeFrame"]
    timeSteps = int(timeFrame/dt)
    time = np.arange(0, timeFrame, dt)

    fig, ax = plt.subplots(2, 1)
    ax[0].plot(time, avgHeight)
    ax[0].set_title("Average Height over Time")
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Average Height")

    ax[1].plot(time, pitch)
    ax[1].set_title("Pitch over Time")
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("Pitch")

    fig, ax = plt.subplots(2, 2)
    ax[0, 1].set_title("Front Left Leg Height and Terrain Height")
    ax[0, 0].set_title("Front Right Leg Height and Terrain Height")
    ax[1, 1].set_title("Rear Left Leg Height and Terrain Height")
    ax[1, 0].set_title("Rear Right Leg Height and Terrain Height")

    for i in range(2):
        for j in range(2):
            ax[i, j].plot(time, heights[i*2 + j,:], label = "Leg height")
            ax[i, j].plot(time, terrain[i*2 + j,:], label="Terrain height")
            ax[i, j].set_xlabel("Time")
            ax[i, j].set_ylabel("Height")
    plt.show()

