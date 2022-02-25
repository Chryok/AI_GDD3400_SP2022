import Constants
import Agent
from Agent import Agent
import Vector
from Vector import Vector
import pygame
from pygame.locals import *
import random

class Enemy(Agent):

    # update for enemy
    def update(self, player, dt):
        # if the player is in attack range then flee
        if (player.center - self.center).length() < Constants.ATTACK_RANGE:
            # set velocity away from player
            self.velocity = ((self.center - player.center).normalize()).scale(self.speed)
            self.engaged = True
            self.engager = player
        # else wander
        else:
            offset = (Vector(self.velocity.y, -self.velocity.x).normalize()).scale(Constants.WANDER_TURN_RADIUS)
            self.velocity = ((self.velocity.normalize() + (offset.scale(random.uniform(-1.0,1.0)))).normalize()).scale(self.speed)
            self.engaged = False

        # use parent method
        super().update(player, dt)

    # gives the enemy a random direction to start moving
    def setRandomVelocity(self):
        self.velocity = Vector(random.uniform(-1.0,1.0),random.uniform(-1.0,1.0)).normalize()
