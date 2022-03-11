import Constants
import Node
import pygame
import Vector

from pygame import *
from Vector import *
from Node import *
from enum import Enum

class SearchType(Enum):
	BREADTH = 0
	DJIKSTRA = 1
	A_STAR = 2
	BEST_FIRST = 3

class Graph():
	def __init__(self):
		""" Initialize the Graph """
		self.nodes = []			# Set of nodes
		self.obstacles = []		# Set of obstacles - used for collision detection

		# Initialize the size of the graph based on the world size
		self.gridWidth = int(Constants.WORLD_WIDTH / Constants.GRID_SIZE)
		self.gridHeight = int(Constants.WORLD_HEIGHT / Constants.GRID_SIZE)

		# Create grid of nodes
		for i in range(self.gridHeight):
			row = []
			for j in range(self.gridWidth):
				node = Node(i, j, Vector(Constants.GRID_SIZE * j, Constants.GRID_SIZE * i), Vector(Constants.GRID_SIZE, Constants.GRID_SIZE))
				row.append(node)
			self.nodes.append(row)

		## Connect to Neighbors
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				# Add the top row of neighbors
				if i - 1 >= 0:
					# Add the upper left
					if j - 1 >= 0:		
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j - 1]]
					# Add the upper center
					self.nodes[i][j].neighbors += [self.nodes[i - 1][j]]
					# Add the upper right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j + 1]]

				# Add the center row of neighbors
				# Add the left center
				if j - 1 >= 0:
					self.nodes[i][j].neighbors += [self.nodes[i][j - 1]]
				# Add the right center
				if j + 1 < self.gridWidth:
					self.nodes[i][j].neighbors += [self.nodes[i][j + 1]]
				
				# Add the bottom row of neighbors
				if i + 1 < self.gridHeight:
					# Add the lower left
					if j - 1 >= 0:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j - 1]]
					# Add the lower center
					self.nodes[i][j].neighbors += [self.nodes[i + 1][j]]
					# Add the lower right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j + 1]]

	def getNodeFromPoint(self, point):
		""" Get the node in the graph that corresponds to a point in the world """
		point.x = max(0, min(point.x, Constants.WORLD_WIDTH - 1))
		point.y = max(0, min(point.y, Constants.WORLD_HEIGHT - 1))

		# Return the node that corresponds to this point
		return self.nodes[int(point.y/Constants.GRID_SIZE)][int(point.x/Constants.GRID_SIZE)]

	def placeObstacle(self, point, color):
		""" Place an obstacle on the graph """
		node = self.getNodeFromPoint(point)

		# If the node is not already an obstacle, make it one
		if node.isWalkable:
			# Indicate that this node cannot be traversed
			node.isWalkable = False		

			# Set a specific color for this obstacle
			node.color = color
			for neighbor in node.neighbors:
				neighbor.neighbors.remove(node)
			node.neighbors = []
			self.obstacles += [node]

	def reset(self):
		""" Reset all the nodes for another search """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].reset()

	def buildPath(self, endNode):
		""" Go backwards through the graph reconstructing the path """
		path = []
		node = endNode
		while node.backNode is not 0: # because the dog did a weird spin at the start of the path sometimes, I am changing the path to start one node away from the dog instead of at the dog to avoid this spin
			node.isPath = True
			path = [node] + path
			node = node.backNode

		# If there are nodes in the path, reset the colors of start/end
		if len(path) > 0:
			path[0].isPath = False
			path[0].isStart = True
			path[-1].isPath = False
			path[-1].isEnd = True
		return path

	def findPath_Breadth(self, start, end):
		""" Breadth Search """
		#print("Breadth")
		self.reset()

		# define start and end nodes
		startNode = self.getNodeFromPoint(start)
		endNode = self.getNodeFromPoint(end)

		# set up start node
		startNode.isVisited = True

		# define queue and add start node to queue
		queue = []
		queue.append(startNode)

		# while the queue is not empty
		while queue:
			# pop the first node off the queue
			c = queue.pop(0)
			c.isExplored = True
			
			# for each neighbor, calculate cost if it was not calculated already and set back pointer
			for n in c.neighbors:
				if n.isVisited == False:
					n.backNode = c
					# if this node is our end node then return path
					if n == endNode:
						return self.buildPath(n)
					queue.append(n)
					n.isVisited = True

		# Return empty path indicating no path was found
		return []

	def findPath_Djikstra(self, start, end):
		""" Djikstra's Search """
		#print("DJIKSTRA")
		self.reset()

		# define start and end nodes
		startNode = self.getNodeFromPoint(start)
		endNode = self.getNodeFromPoint(end)

		# set up start node
		startNode.isVisited = True
		startNode.costFromStart = 0

		# define queue and add start node to queue
		queue = []
		queue.append(startNode)

		# while the queue is not empty
		while queue:
			# sort the queue so that its in order of node cost
			queue.sort(key=lambda x: x.costFromStart)

			# pop the first node off the queue
			c = queue.pop(0)
			c.isExplored = True
			# if this node is our end node then return path
			if c == endNode:
				return self.buildPath(c)
			# for each neighbor, calculate cost if it was not calculated already and set back pointer
			for n in c.neighbors:
				if n.isVisited == False:
					n.backNode = c
					n.costFromStart = c.costFromStart + (c.center - n.center).length()
					queue.append(n)
					n.isVisited = True
					# if this node has already been visited, check for new cost and update if needed
				else:
					potentialCost = c.costFromStart + (c.center - n.center).length()
					if potentialCost < n.costFromStart:
						n.backNode = c
						n.costFromStart = potentialCost

		# Return empty path indicating no path was found
		return []

	def findPath_AStar(self, start, end):
		""" A Star Search """
		#print("A_STAR")
		self.reset()

		# get ref to start node and set it to visited/set it up
		startNode = self.getNodeFromPoint(start)
		startNode.isVisited = True
		startNode.costFromStart = 0

		# get ref to end node
		endNode = self.getNodeFromPoint(end)

		# set up start node total cost as the estimated cost to the target
		startNode.cost = (startNode.center - endNode.center).length()

		# create queue and add start node to it
		queue = []
		queue.append(startNode)

		# while the queue is not empty check neighbors and update their costs
		while queue:
			# sort the queue so that its in order of node cost
			queue.sort(key=lambda x: x.cost)

			c = queue.pop(0)
			c.isExplored = True
			# if we just poped the end node off the queue, build and return path
			if c == endNode:
				return self.buildPath(c)
			# for every neighboring node
			for n in c.neighbors:
				# if its a new node, update back pointer and cost, and add to queue, set to visited
				if n.isVisited == False:
					n.backNode = c
					n.costFromStart = c.costFromStart + (c.center - n.center).length()
					n.cost = n.costFromStart + (n.center - endNode.center).length()
					queue.append(n)
					n.isVisited = True
					# if its not a new node, check and update cost and back pointer if needed
				else:
					potentialCost = c.costFromStart + (c.center - n.center).length()
					if potentialCost < n.costFromStart:
						n.backNode = c
						n.costFromStart = potentialCost
						n.cost = potentialCost + (n.center - endNode.center).length()
		
		# Return empty path indicating no path was found
		return []

	def findPath_BestFirst(self, start, end):
		""" Best First Search """
		#print("BEST_FIRST")
		self.reset()

		# define start and end nodes
		startNode = self.getNodeFromPoint(start)
		endNode = self.getNodeFromPoint(end)

		# set up start node
		startNode.isVisited = True
		startNode.cost = (startNode.center - endNode.center).length()

		# define queue and add start node to queue
		queue = []
		queue.append(startNode)

		# while the queue is not empty
		while queue:
			# sort the queue so that its in order of node cost
			queue.sort(key=lambda x: x.cost)

			# pop the first node off the queue
			c = queue.pop(0)
			c.isExplored = True
			# if this node is our end node then return path
			if c == endNode:
				return self.buildPath(c)
			# for each neighbor, calculate cost if it was not calculated already and set back pointer
			for n in c.neighbors:
				if n.isVisited == False:
					n.backNode = c
					n.cost = (n.center - endNode.center).length()
					queue.append(n)
					n.isVisited = True

		# Return empty path indicating no path was found
		return []

	def findPath_AStar_Custom(self, start, end, sheep):
		""" A Star Custom Search """
		#print("A_STAR_CUSTOM")
		self.reset()

		# get ref to start node and set it to visited/set it up
		startNode = self.getNodeFromPoint(start)
		startNode.isVisited = True
		startNode.costFromStart = 0

		# get ref to end node
		endNode = self.getNodeFromPoint(end)

		# set up start node total cost as the estimated cost to the target
		startNode.cost = (startNode.center - endNode.center).length()

		# create queue and add start node to it
		queue = []
		queue.append(startNode)

		# while the queue is not empty check neighbors and update their costs
		while queue:
			# sort the queue so that its in order of node cost
			queue.sort(key=lambda x: x.cost)

			c = queue.pop(0)
			c.isExplored = True
			# if we just poped the end node off the queue, build and return path
			if c == endNode:
				return self.buildPath(c)
			# for every neighboring node
			for n in c.neighbors:
				# if its a new node, update back pointer and cost, and add to queue, set to visited
				if n.isVisited == False:
					n.backNode = c
					n.costFromStart = c.costFromStart + (c.center - n.center).length()
					n.cost = n.costFromStart + (n.center - endNode.center).length()
					queue.append(n)
					n.isVisited = True
					# if its not a new node, check and update cost and back pointer if needed
				else:
					potentialCost = c.costFromStart + (c.center - n.center).length()
					if potentialCost < n.costFromStart:
						n.backNode = c
						n.costFromStart = potentialCost
						n.cost = potentialCost + (n.center - endNode.center).length()

				# add number to cost if within sheep flee range, to try and avoid entering that range
				if (n.center - sheep.center).length() <= Constants.SHEEP_MIN_FLEE_DIST:
					n.cost += (Constants.SHEEP_MIN_FLEE_DIST * 3.14159265) - (n.center - sheep.center).length()
		
		# Return empty path indicating no path was found
		return []

	def draw(self, screen):
		""" Draw the graph """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].draw(screen)