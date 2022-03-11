from Constants import *
from pygame import *
from random import *
from math import *
from Vector import *
from Agent import *
from Sheep import *
from Dog import *
from Graph import *
from Node import *
from GameState import *

class StateMachine:
	""" Machine that manages the set of states and their transitions """

	def __init__(self, startState):
		""" Initialize the state machine and its start state"""
		self.__currentState = startState
		self.__currentState.enter()

	def getCurrentState(self):
		""" Get the current state """
		return self.__currentState

	def update(self, gameState):
		""" Run the update on the current state and determine if we should transition """
		nextState = self.__currentState.update(gameState)

		# If the nextState that is returned by current state's update is not the same
		# state, then transition to that new state
		if nextState != None and type(nextState) != type(self.__currentState):
			self.transitionTo(nextState)

	def transitionTo(self, nextState):
		""" Transition to the next state """
		self.__currentState.exit()
		self.__currentState = nextState
		self.__currentState.enter()

	def draw(self, screen):
		""" Draw any debugging information associated with the states """
		self.__currentState.draw(screen)

class State:
	def enter(self):
		""" Enter this state, perform any setup required """
		print("Entering " + self.__class__.__name__)
		
	def exit(self):
		""" Exit this state, perform any shutdown or cleanup required """
		print("Exiting " + self.__class__.__name__)

	def update(self, gameState):
		""" Update this state, before leaving update, return the next state """
		print("Updating " + self.__class__.__name__)

	def draw(self, screen):
		""" Draw any debugging info required by this state """
		pass

			   
class FindSheepState(State):
	""" This is an example state that simply picks the first sheep to target """

	def update(self, gameState):
		""" Update this state using the current gameState """
		super().update(gameState)

		# ref to dog, targetSheep, and penBounds
		dog = gameState.getDog()
		penBounds = gameState.getPenBounds()

		# penCenter ref
		penCenter = Vector(penBounds[0].left + penBounds[0].width * 0.5, penBounds[0].top)

		# decide which sheep to target

		# for each sheep, calculate the intelligence of choosing that sheep as our current target
		dog.setTargetSheep(gameState.getHerd()[0])
		for s in gameState.getHerd():
			if (s.center - penCenter).length() < (dog.getTargetSheep().center - penCenter).length():
				dog.setTargetSheep(s)
		
		if (dog.getTargetSheep().center - dog.center).length() <= Constants.DOG_MIN_HERDING_DISTANCE:
			return HerdSheepToPenState()
		else:
			return GetCloserToSheepState()


class HerdSheepToPenState(State):
	def update(self, gameState):
		super().update(gameState)

		# ref to dog, targetSheep, and penBounds
		dog = gameState.getDog()
		targetSheep = dog.getTargetSheep()
		penBounds = gameState.getPenBounds()

		# penCenter ref
		penCenter = Vector(penBounds[0].left + penBounds[0].width * 0.5, penBounds[0].top)

		penToSheepVector = (targetSheep.center - penCenter).normalize()
		sheepToDogVector = (dog.center - targetSheep.center).normalize()
		sheepToDogDistance = (dog.center - targetSheep.center).length()
		sheepToPenDistance = (penCenter - targetSheep.center).length()

		angleDif = math.degrees(math.acos((penToSheepVector.x * sheepToDogVector.x) + (penToSheepVector.y * sheepToDogVector.y)))

		if angleDif > Constants.DOG_PUSH_SHEEP_ANGLE and sheepToPenDistance > 64:
			
			behindSheepDistanceScale = Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI

			targetPos = targetSheep.center + penToSheepVector.scale(behindSheepDistanceScale)
			targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

			while targetNode.isWalkable != True:
				behindSheepDistanceScale *= 0.9
				targetPos = targetSheep.center + penToSheepVector.scale(behindSheepDistanceScale)
				targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

			# temp directly call the custom AStar method to stay out of the sheeps flee range
			dog.calculatePathAvoidingSheep(targetPos, targetSheep)
		else:
			behindSheepDistanceScale = Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_HERD_DIST_MULTI

			targetPos = targetSheep.center + penToSheepVector.scale(behindSheepDistanceScale)
			targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

			while targetNode.isWalkable != True:
				behindSheepDistanceScale *= 0.9
				targetPos = targetSheep.center + penToSheepVector.scale(behindSheepDistanceScale)
				targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

			dog.calculatePathToNewTarget(targetPos)

		return FollowPathState()

class GetCloserToSheepState(State):
	def update(self, gameState):
		super().update(gameState)

		# ref to dog, targetSheep, and penBounds
		dog = gameState.getDog()
		targetSheep = dog.getTargetSheep()
		penBounds = gameState.getPenBounds()

		# penCenter ref
		penCenter = Vector(penBounds[0].left + penBounds[0].width * 0.5, penBounds[0].top)

		penToSheepVector = (targetSheep.center - penCenter).normalize()
		sheepToDogVector = (dog.center - targetSheep.center).normalize()

		potentialTargetPositions = []

		# pen to sheep side vectors
		potentialTargetPositions.append(targetSheep.center + Vector(penToSheepVector.y, -penToSheepVector.x).scale(Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI))
		potentialTargetPositions.append(targetSheep.center + Vector(-penToSheepVector.y, penToSheepVector.x).scale(Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI))

		# sheep to dog side vectors
		potentialTargetPositions.append(targetSheep.center + Vector(sheepToDogVector.y, -sheepToDogVector.x).scale(Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI))
		potentialTargetPositions.append(targetSheep.center + Vector(-sheepToDogVector.y, sheepToDogVector.x).scale(Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI))
		
		behindSheepTargetPos = targetSheep.center + penToSheepVector.scale(Constants.SHEEP_MIN_FLEE_DIST * Constants.DOG_DONT_SPOOK_SHEEP_MULTI)
		
		targetPos = potentialTargetPositions.pop(0)

		for p in potentialTargetPositions:
			if (p - behindSheepTargetPos).length() * 0.5 + (p - dog.center).length() < (targetPos - behindSheepTargetPos).length() * 0.5 + (targetPos - dog.center).length():
				targetPos = p

		targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

		while targetNode.isWalkable != True:
			targetPos = targetPos + (targetSheep.center - targetPos).normalize()
			targetNode = gameState.getGraph().getNodeFromPoint(targetPos)

		dog.calculatePathToNewTarget(targetPos)

		return FollowPathState()

class FollowPathState(State):
	""" This is the state the dog enters to follow the path """

	def update(self, gameState):
		super().update(gameState)
		dog = gameState.getDog()
		if dog.getPathLength() > 0 and not dog.getTargetSheep().boundingRect.colliderect(gameState.getPenBounds()[1]):
			return FollowPathState()
		elif dog.getTargetSheep().boundingRect.colliderect(gameState.getPenBounds()[1]):
			dog.path = []
			return Idle()
		else:
			return HerdSheepToPenState()

		return Idle()

class Idle(State):
	""" This is an idle state where the dog does nothing """

	def update(self, gameState):
		super().update(gameState)

		# Do nothing
		if len(gameState.getHerd()) > 0:
			return FindSheepState()
		else:
			return Idle()