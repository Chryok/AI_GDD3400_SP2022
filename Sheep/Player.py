import Constants
import Agent
from Agent import Agent
import Vector
from Vector import Vector
import pygame
from pygame.locals import *

class Player(Agent):

    # constructor
    def __init__(self, position, size, speed, color):
        super().__init__(position, size, speed, color)
        self.target = None
        self.lastTarget = None

    # update for player
    def update(self, enemies, dt):
        # target to first enemy in list for now if we dont have a target already
        if self.target == None and enemies[0] != None:
            self.target = enemies[0]
            # if the target selected is the same as our last target move on to next target
            if self.target == self.lastTarget and enemies[1] != None:
                self.target = enemies[1]
            # go through the list and select the closest enemy as long as it was not the previously targeted enemy
            for e in enemies:
                if (e.center - self.center).length() < (self.target.center - self.center).length() and e != self.lastTarget:
                    self.target = e

        # chase target
        if self.target != None:
            # set velocity towards target and then go that way
            self.velocity = ((self.target.center - self.center).normalize()).scale(self.speed)

            # set engaged and engager, this is for drawing the red lines for debugging
            self.engaged = True
            self.engager = self.target
            
            # use parent method
            super().update(enemies, dt)

            # if we tag the target set last target = target and target = none.
            if self.collision(self.target):
                self.lastTarget = self.target
                self.target = None