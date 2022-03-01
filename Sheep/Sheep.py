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
dog = Player(Vector((Constants.WORLD_WIDTH / 2) - Constants.PLAYER_SIZE / 2, (Constants.WORLD_HEIGHT / 2) - Constants.PLAYER_SIZE / 2), Constants.PLAYER_SIZE, Constants.PLAYER_SPEED, Constants.PLAYER_COLOR, dogImage)

# Create enemies
sheeps = []
for i in range(5):
    sheeps.append(Enemy(Vector(random.randint(100, Constants.WORLD_WIDTH - 100), random.randint(100, Constants.WORLD_HEIGHT - 100)), Constants.ENEMY_SIZE, Constants.ENEMY_SPEED, Constants.ENEMY_COLOR, sheepImage, dog))
    sheeps[i].setRandomTargetDir()

# time variables
prev_time = time.time()
dt = 0

# game loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # time variables used for delta time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    #reset screen
    display.fill(Constants.BACKGROUND_COLOR)

    # update and draw player
    dog.update(sheeps, dt)
    dog.draw(display)

    # update and draw enemies
    for sheep in sheeps:
        sheep.update(dt)
        sheep.draw(display)
        print(sheep)

    # show the new frame and set framerate
    pygame.display.flip();
    clock.tick(Constants.FRAME_RATE)