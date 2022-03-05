import Constants
import Vector
from Vector import Vector
import pygame
from pygame.locals import *
import math

class Agent:

    #constuctor
    def __init__(self, position, size, speed, color, image):
        self.size = Vector(size, size)
        self.image = image
        self.imageAngle = 45
        self.surf = pygame.transform.rotate(self.image, self.imageAngle)
        self.boundingRect = self.surf.get_bounding_rect()
        self.color = color
        self.position = Vector(position.x, position.y)
        self.velocity = Vector(0, 0)
        self.speed = speed
        self.target = None
        self.targetDir = Vector(0, 0)
        self.allForcesTargetDirection = Vector(0, 0)
        self.differenceVector = self.allForcesTargetDirection - self.velocity
        self.turnSpeed = 0.4
        self.lastTarget = None
        self.updateRect()
        self.updateCenter()
        self.upperLeft = Vector(self.center.x - self.surf.get_width()/2, self.center.y - self.surf.get_height()/2)
        self.updateDistToBoundaries()

        # list of forces applied due to being close to a boundary
        self.boundaryForces = []
        self.boundariesNearMe = []

        # list of ALL forces to be summed up to the agent
        self.allForces = []

    # draws the agent using the rect updated in update, draws lines to show when engaged with another agent and to show the velocity
    def draw(self, display):

        # draw agent image
        self.updateImageAngle()
        self.surf = pygame.transform.rotate(self.image, self.imageAngle)
        self.upperLeft = Vector(self.center.x - self.surf.get_width()/2, self.center.y - self.surf.get_height()/2)
        display.blit(self.surf, [self.upperLeft.x, self.upperLeft.y])
        #pygame.draw.rect(display, self.color, self.agentRect)

        # draw bounding rect
        if Constants.DEBUG_BOUNDING_RECTS:
            pygame.draw.rect(display, self.color, self.boundingRect, Constants.DEBUG_LINE_WIDTH)

        # draw debug lines
        self.drawDebugLines(display)

        # clear boundariesNearMe to prep for next frame
        self.boundariesNearMe.clear()

    # updates the position based on velocity vector, clamps position in screen, updates rect
    def update(self, dt):

        # update boundary forces
        self.updateBoundaryForces()

        # reset applied force then add all forces together into applied force
        self.allForcesTargetDirection = Vector(0, 0)
        for f in self.allForces:
            self.allForcesTargetDirection += f
        self.allForcesTargetDirection = self.allForcesTargetDirection.normalize()

        # update difference vector
        self.differenceVector = self.allForcesTargetDirection - self.velocity

        # set velocity based on turn speed
        if self.differenceVector.length() < self.turnSpeed:
            self.updateVelocity(self.allForcesTargetDirection)
        else:
            self.updateVelocity(self.velocity + self.differenceVector.normalize().scale(self.turnSpeed))

        # update position using velocity vector based on applied force
        self.position += self.velocity.scale(dt * self.speed)
        self.clampPositionInScreen()

        # clear all forces for next update
        self.allForces.clear()

        # update center
        self.updateCenter()

        #update Rect
        self.updateRect()

        # get bounding rect of surface
        self.boundingRect = self.surf.get_bounding_rect()
        self.boundingRect = self.boundingRect.move(self.upperLeft.x, self.upperLeft.y)

        # if we tag the target set last target = target and target = none.
        if self.isInCollision(self.target):
            self.lastTarget = self.target
            self.target = None

    # calculates the center of the agent on screen
    def updateCenter(self):
        self.center = Vector(self.position.x + self.size.x/2, self.position.y + self.size.y/2)
        return self.center

    # returns true if the agent is colliding with the target agent
    def isInCollision(self, other):
        return pygame.Rect.colliderect(self.boundingRect, other.boundingRect)

    # clamps the values of the x and y position vector to keep the agent on screen
    def clampPositionInScreen(self):
        self.position.x = max(0, min(self.position.x, Constants.WORLD_WIDTH - self.size.x))
        self.position.y = max(0, min(self.position.y, Constants.WORLD_HEIGHT - self.size.y))

    # prints data to the console
    def __str__(self):
        return 'size: ' + str(self.size.x) + ', ' + str(self.size.y) + ' position: ' + str(self.position) + ' velocity: ' + str(self.velocity) + ' center: ' + str(self.center)

    # updates the rect
    def updateRect(self):
        self.agentRect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    # normalizes the provided velocity
    def updateVelocity(self, vel):
        self.velocity = vel.normalize()
        return self.velocity

    # updates distances to boundaries
    def updateDistToBoundaries(self):
        # left boundary
        self.distToLeftBoundary = self.center.x
        
        # right boundary
        self.distToRightBoundary = Constants.WORLD_WIDTH - self.center.x
        
        # top boundary
        self.distToTopBoundary = self.center.y
        
        # bottom boundary
        self.distToBotBoundary = Constants.WORLD_HEIGHT - self.center.y

    # calculates and appends boundary force to boundaryForces
    def addBoundaryForce(self, boundaryNormalVector, boundaryDist):
        if boundaryDist < Constants.BOUNDARY_RADIUS:
            self.boundaryForces.append((boundaryNormalVector.scale((Constants.BOUNDARY_RADIUS - boundaryDist))).scale(Constants.BOUNDARY_WEIGHT * int(Constants.ENABLE_BOUNDARIES)))
            self.boundariesNearMe.append(boundaryNormalVector)

    # updates all boundary forces
    def updateBoundaryForces(self):
        self.updateDistToBoundaries()
        self.boundaryForces.clear()
        # left boundary
        self.addBoundaryForce(Constants.LEFT_BOUND_NORM, self.distToLeftBoundary)

        # right boundary
        self.addBoundaryForce(Constants.RIGHT_BOUND_NORM, self.distToRightBoundary)

        # top boundary
        self.addBoundaryForce(Constants.TOP_BOUND_NORM, self.distToTopBoundary)

        # bottom boundary
        self.addBoundaryForce(Constants.BOT_BOUND_NORM, self.distToBotBoundary)

        # add boundary forces to the AllForces list
        for f in self.boundaryForces:
            self.allForces.append(f)

    # draws the boundary vector
    def drawBoundaryVector(self, display, boundaryNormal, lengthToDrawLine):
        pygame.draw.line(display, Constants.COLOR_BLUE, (self.center.x, self.center.y),(self.center.x - boundaryNormal.x * lengthToDrawLine, self.center.y - boundaryNormal.y * lengthToDrawLine), width = 2)

    # updates the image angle
    def updateImageAngle(self):
        self.imageAngle = math.degrees(math.atan2(self.velocity.x, self.velocity.y)) - 180

    # draw debug lines
    def drawDebugLines(self, display):
        if Constants.DEBUG_VELOCITY:
            # target velocity vector
            pygame.draw.line(display, Constants.COLOR_GREEN, (self.center.x, self.center.y),(self.center.x + self.allForcesTargetDirection.x * self.size.x * 4, self.center.y + self.allForcesTargetDirection.y * self.size.y * 2), width = 3)

        # This is the velocity vector itself, not the target velocity, this will always be a straight line coming straight out from the agent
        #pygame.draw.line(display, Constants.COLOR_BLUE, (self.center.x, self.center.y),
        #                 (self.center.x + self.velocity.x * self.size.x * 2,
        #                  self.center.y + self.velocity.y * self.size.y * 2), Constants.DEBUG_LINE_WIDTH)
        
        if Constants.DEBUG_BOUNDARIES:
            # boundary force vectors
            for f in self.boundariesNearMe:
                self.drawBoundaryVector(display, f, Constants.BOUNDARY_RADIUS)