import pygame
from pygame.locals import *
import Constants
import Vector
from Vector import Vector
import Player
from Player import Player
import Enemy
from Enemy import Enemy
import time
import random

# initialize game
pygame.init()

# Create Display
display = pygame.display.set_mode((Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT))

# bool used to end game
done = False

# Create clock for framerate
clock = pygame.time.Clock()

# load images for the agents
sheepImage = pygame.image.load('sheep.png')
dogImage = pygame.image.load('dog.png')

# Create Player
dog = Player(Vector(random.randint(50, Constants.WORLD_WIDTH - 50), random.randint(50, Constants.WORLD_HEIGHT - 50)), Constants.PLAYER_SIZE, Constants.PLAYER_SPEED, Constants.PLAYER_COLOR, dogImage)

# Create enemies
sheeps = []
for i in range(50):
    sheeps.append(Enemy(Vector(random.randint(50, Constants.WORLD_WIDTH - 50), random.randint(50, Constants.WORLD_HEIGHT - 50)), Constants.ENEMY_SIZE, Constants.ENEMY_SPEED, Constants.ENEMY_COLOR, sheepImage, dog))
    sheeps[i].setRandomTargetDir()

# time variables
prev_time = time.time()
dt = 0

def calculateNeighbors(herd):
    for s in herd:
        s.neighbors.clear()
        for n in herd:
            if s != n and (s.center - n.center).length() < Constants.NEIGHBOR_MIN_DIST:
                s.neighbors.append(n)

def handleDebugging(event):
    # Handle the Debugging for Forces
    if event.type == pygame.KEYUP:

        # Toggle Dog Influence
        if event.key == pygame.K_1:
            Constants.ENABLE_DOG = not Constants.ENABLE_DOG
            print("Toggle Dog Influence", Constants.ENABLE_DOG)

        # Toggle Alignment Influence
        if event.key == pygame.K_2: 
            Constants.ENABLE_ALIGNMENT = not Constants.ENABLE_ALIGNMENT
            print("Toggle Alignment Influence", Constants.ENABLE_ALIGNMENT)

        # Toggle Separation Influence
        if event.key == pygame.K_3: 
            Constants.ENABLE_SEPARATION = not Constants.ENABLE_SEPARATION
            print("Toggle Separation Influence", Constants.ENABLE_SEPARATION)

        # Toggle Cohesion Influence
        if event.key == pygame.K_4: 
            Constants.ENABLE_COHESION = not Constants.ENABLE_COHESION
            print("Toggle Cohesion Influence", Constants.ENABLE_COHESION)

        # Toggle Boundary Influence
        if event.key == pygame.K_5: 
            Constants.ENABLE_BOUNDARIES = not Constants.ENABLE_BOUNDARIES
            print("Toggle Boundary Influence", Constants.ENABLE_BOUNDARIES)

        # Toggle Dog Influence Lines
        if event.key == pygame.K_6: 
            Constants.DEBUG_DOG_INFLUENCE = not Constants.DEBUG_DOG_INFLUENCE
            print("Toggle Dog Influence Lines", Constants.DEBUG_DOG_INFLUENCE)
    
        # Toggle Velocity Lines
        if event.key == pygame.K_7: 
            Constants.DEBUG_VELOCITY = not Constants.DEBUG_VELOCITY
            print("Toggle Velocity Lines", Constants.DEBUG_VELOCITY)

        # Toggle Neighbor Lines
        if event.key == pygame.K_8: 
            Constants.DEBUG_NEIGHBORS = not Constants.DEBUG_NEIGHBORS
            print("Toggle Neighbor Lines", Constants.DEBUG_NEIGHBORS)

        # Toggle Boundary Force Lines
        if event.key == pygame.K_9: 
            Constants.DEBUG_BOUNDARIES = not Constants.DEBUG_BOUNDARIES
            print("Toggle Boundary Force Lines", Constants.DEBUG_BOUNDARIES)

        # Toggle Bounding Box Lines
        if event.key == pygame.K_0: 
            Constants.DEBUG_BOUNDING_RECTS = not Constants.DEBUG_BOUNDING_RECTS
            print("Toggle Bounding Box Lines", Constants.DEBUG_BOUNDING_RECTS)

# game loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        else:
            handleDebugging(event)

    # time variables used for delta time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    #reset screen
    display.fill(Constants.BACKGROUND_COLOR)

    calculateNeighbors(sheeps)

    # update and draw player
    dog.update(sheeps, dt)
    dog.draw(display)

    # update and draw enemies
    for sheep in sheeps:
        sheep.update(dt)
        sheep.draw(display)

    # show the new frame and set framerate
    pygame.display.flip();
    clock.tick(Constants.FRAME_RATE)