import tomllib
import numpy as np
import matplotlib.pyplot as plt
import random
import PID
import math

#Function to check the fitness of the individual
def fitnessCheck(K):
    avgHeight, pitch, heights, _ = PID.system(K[0], K[1], K[2])
    target = 10
    err = np.average([abs(height - target) for height in avgHeight if not math.isnan(height)])
    return -abs(err)

#To initialize the population
def initPopulation(size, lowerBound, upperBound):
    population = []
    for _ in range(size):
        cont = (random.uniform(lowerBound, upperBound),
                random.uniform(lowerBound, upperBound),
                random.uniform(lowerBound, upperBound))
        population.append(cont)
    return population

#Conduct tournaments and select the fittest out of the batch
def selection(population, fitnesses, tournament_size=3):
    selected = []
    for _ in range(len(population)):
        tournament = [ind for ind in random.sample(list(zip(population, fitnesses)), tournament_size) if not math.isnan(ind[1])]
        try:
            winner = max(tournament, key=lambda x: x[1])[0]
            selected.append(winner)
        except ValueError:
            pass
    return selected

#The bees and the birds function
def crossover(parent1, parent2):
    alpha = random.random()
    child1 = tuple(alpha * p1 + (1 - alpha) * p2 for p1, p2 in zip(parent1, parent2))
    child2 = tuple(alpha * p2 + (1 - alpha) * p1 for p1, p2 in zip(parent1, parent2))
    return child1, child2

#Where radiation comes into work
def mutation(individual, mutationRate, lowerBound, upperBound):
    individual = list(individual)
    for i in range(len(individual)):
        if random.random() < mutationRate:
            mutationAmount = random.uniform(-1, 1)
            individual[i] += mutationAmount
            individual[i] = max(min(individual[i], upperBound), lowerBound)
    return tuple(individual)

#Main algorithm
def geneticAlgorithm(populationSize, lowerBound, upperBound, generations, mutationRate):
    population = initPopulation(populationSize, lowerBound, upperBound)
    
    bestPerformers = []
    allPopulations = []

    for generation in range(generations):
        print(generation)
        fitnesses = [fitnessCheck(ind) for ind in population]
        
        # Store the best performer of the current generation
        bestIndividual = max(population, key=fitnessCheck)
        bestFitness = fitnessCheck(bestIndividual)
        bestPerformers.append((bestIndividual, bestFitness))
        allPopulations.append(population[:])
        
        #Selecting the best
        population = selection(population, fitnesses, 5)

        nextPopulation = []

        #sex.
        for i in range(0, len(population), 2):
            parent1 = population[i]
            parent2 = population[i + 1]

            child1, child2 = crossover(parent1, parent2)

            nextPopulation.append(mutation(child1, mutationRate, lowerBound, upperBound))
            nextPopulation.append(mutation(child2, mutationRate, lowerBound, upperBound))
        nextPopulation[0] = bestIndividual
        population = nextPopulation
    

    finalPopulation = allPopulations[-1]
    finalFitnesses = [fitnessCheck(ind) for ind in finalPopulation]
    
    #Plot the performances
    generations_list = range(1, len(bestPerformers) + 1)
    Kp = [ind[0][0] for ind in bestPerformers]
    Kd = [ind[0][1] for ind in bestPerformers]
    Ki = [ind[0][2] for ind in bestPerformers]
    fig, ax = plt.subplots()
    ax.plot(generations_list, Kp, label='Kp', color='blue')
    ax.plot(generations_list, Kd, label='Kd', color='green')
    ax.plot(generations_list, Ki, label='Ki', color='red')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Parameter Values')
    ax.set_title('Parameter Values Over Generations')
    ax.legend()

    avgHeight, pitch, heights, terrain = PID.system(bestIndividual[0], bestIndividual[1], bestIndividual[2])
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    # Kp, Kd, Ki = (10, 0.10711112931380898, 5.219131502961188)

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

    print(max(population, key=fitnessCheck))
    plt.show()

if __name__ == "__main__":
    
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    geneticConfig = config["geneticConfig"]

    populationSize = geneticConfig["populationSize"]
    lowerBound = geneticConfig["lowerBound"]
    upperBound = geneticConfig["upperBound"]
    generations = geneticConfig["generations"]
    mutationRate = geneticConfig["mutationRate"]
    geneticAlgorithm(populationSize, lowerBound, upperBound, generations, mutationRate)

