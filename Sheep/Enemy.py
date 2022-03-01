import Constants
import Agent
from Agent import Agent
import Vector
from Vector import Vector
import pygame
from pygame.locals import *
import random

class Enemy(Agent):

    # constructor
    def __init__(self, position, size, speed, color, image, player):
        super().__init__(position, size, speed, color, image)
        self.isFleeing = False
        self.playerRef = player
        self.updateTarget(player)
        self.offset = Vector(0,0)
        self.turnSpeed = Constants.ENEMY_TURN_SPEED

        # int counter so that we dont change dir every frame when wandering
        self.secondsSinceLastWanderChange = 0.0
        self.secondsToWaitTillNextWanderChange = random.uniform(0.1,3.0)

    # update for enemy
    def update(self, dt):

        # reset target to player if we dont have a target
        if self.target == None:
            self.target = self.playerRef

        # count up seconds sense last wander change
        self.secondsSinceLastWanderChange += 1 * dt

        # if the player is in attack range then flee
        if self.isTargetClose():

            # update targets direction vector
            self.targetDir = (self.center - self.target.center).normalize()

            # calculate applied force based on weights
            self.allForces.append(self.targetDir.scale(Constants.DIR_FROM_PLAYER_WEIGHT))

        # else wander
        else:

            if self.secondsSinceLastWanderChange >= self.secondsToWaitTillNextWanderChange:
                self.secondsSinceLastWanderChange = 0.0
                self.secondsToWaitTillNextWanderChange = random.uniform(0.1,3.0)
                # calculate offset from current direction
                self.offset = Vector(self.targetDir.y, -self.targetDir.x).scale(Constants.WANDER_TURN_RADIUS).scale(random.uniform(-1.0,1.0))

            # update targets direction vector to apply wander
            self.targetDir = (self.targetDir + self.offset).normalize()

            # calculate applied force based on weights
            self.allForces.append(self.targetDir.scale(Constants.WANDER_WEIGHT))

        # use parent method
        super().update(dt)

    # draw
    def draw(self, display):
        # if engaged, draw line to show with who
        if self.isFleeing and self.target != None:
            pygame.draw.line(display, Constants.COLOR_RED, (self.center.x, self.center.y),(self.target.center.x , self.target.center.y), width = 3)
        super().draw(display)

    # gives the enemy a random direction to start moving
    def setRandomTargetDir(self):
        self.targetDir = Vector(random.uniform(-1.0,1.0), random.uniform(-1.0,1.0)).normalize()

    # switches the enemy from wander to flee and vice versa
    def switchMode(self):
        if isFleeing:
            self.isFleeing = False
        else:
            self.isFleeing = True

    # if the player is within the minimum attack distance, set isFleeing to true and return true. otherwise, set isFleeing to false and return false
    def isTargetClose(self):
        if(self.target):
            if (self.target.center - self.center).length() < Constants.MIN_ATTACK_DIST:
                self.isFleeing = True
                return True
        self.isFleeing = False
        return False

    # sets the target
    def updateTarget(self, target):
        self.target = target
