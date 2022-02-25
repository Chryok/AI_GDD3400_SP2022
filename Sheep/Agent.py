import Constants
import Vector
from Vector import Vector
import pygame
from pygame.locals import *

class Agent:

    #constuctor
    def __init__(self, position, size, speed, color):
        self.position = Vector(position.x, position.y)
        self.speed = speed
        self.size = size
        self.velocity = Vector(0, 0)
        self.center = self.calcCenter()
        self.color = color
        self.engaged = False
        self.engager = None
        self.agentRect = pygame.Rect(position.x, position.y, size, size)

    # draws the agent using the rect updated in update, draws lines to show when engaged with another agent and to show the velocity
    def draw(self, display):
        # draw agent image
        pygame.draw.rect(display, self.color, self.agentRect)
        # draw velocity vector
        pygame.draw.line(display, Constants.COLOR_BLUE, (self.center.x, self.center.y),(self.center.x + self.velocity.normalize().x * self.size, self.center.y + self.velocity.normalize().y * self.size), width = 3)
        # if engaged, draw line to show with who
        if self.engaged and self.engager != None:
            pygame.draw.line(display, Constants.COLOR_RED, (self.center.x, self.center.y),(self.engager.center.x , self.engager.center.y), width = 3)

    # updates the position based on velocity vector, clamps position in screen, updates rect
    def update(self, enemies, dt):
        self.position += self.velocity.scale(dt)
        self.clampPositionInScreen()

        # update center
        self.center = self.calcCenter()

        #update Rect
        self.agentRect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)

    # calculates the center of the agent on screen
    def calcCenter(self):
         return Vector(self.position.x + self.size/2, self.position.y + self.size/2)

    # returns true if the agent is colliding with the target agent
    def collision(self, other):
        return pygame.Rect.colliderect(self.agentRect, other.agentRect)

    # clamps the values of the x and y position vector to keep the agent on screen
    def clampPositionInScreen(self):
        self.position.x = max(0, min(self.position.x, Constants.WORLD_WIDTH - self.size))
        self.position.y = max(0, min(self.position.y, Constants.WORLD_HEIGHT - self.size))

    # prints data to the console
    def __str__(self):
        return 'size: ' + str(self.size) + ' position: ' + str(self.position) + ' velocity: ' + str(self.velocity) + ' center: ' + str(self.center)