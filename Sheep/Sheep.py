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

# Create Player
player = Player(Vector((Constants.WORLD_WIDTH / 2) - Constants.PLAYER_SIZE / 2, (Constants.WORLD_HEIGHT / 2) - Constants.PLAYER_SIZE / 2), Constants.PLAYER_SIZE, Constants.PLAYER_SPEED, Constants.PLAYER_COLOR)

# Create enemies
enemies = []
for i in range(10):
    enemies.append(Enemy(Vector(random.randint(100, Constants.WORLD_WIDTH - 100), random.randint(100, Constants.WORLD_HEIGHT - 100)), Constants.ENEMY_SIZE, Constants.ENEMY_SPEED, Constants.ENEMY_COLOR))
    enemies[i].setRandomVelocity()

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
    player.update(enemies, dt)
    player.draw(display)

    # update and draw enemies
    for e in enemies:
        e.update(player, dt)
        e.draw(display)
        print(e)

    # show the new frame and set framerate
    pygame.display.flip();
    clock.tick(Constants.FRAME_RATE)