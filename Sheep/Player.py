import Constants
import Agent
from Agent import Agent
import Vector
from Vector import Vector
import pygame
from pygame.locals import *

class Player(Agent):

    def __init__(self, position, size, speed, color, image):
        super().__init__(position, size, speed, color, image)
        self.turnSpeed = Constants.PLAYER_TURN_SPEED
        

    # update for player
    def update(self, enemies, dt):

        # target to first enemy in list for now if we dont have a target already
        if self.target == None and enemies:
            self.target = enemies[0]
            # if the target selected is the same as our last target move on to next target
            if self.target == self.lastTarget and len(enemies) > 1:
                self.target = enemies[1]
            # go through the list and select the closest enemy as long as it was not the previously targeted enemy
            for e in enemies:
                if (e.center - self.center).length() < (self.target.center - self.center).length() and e != self.lastTarget:
                    self.target = e

        # chase target
        if self.target != None:
            # store the calculated, normalized direction to the Sheep being tracked
            self.targetDir = (self.target.center - self.center).normalize()

            # calculate applied force based on weights
            self.allForces.append(self.targetDir.scale(Constants.DIR_TO_ENEMY_WEIGHT))
            
            # use parent method
            super().update(dt)

        else:
            self.velocity = Vector(0,0)