import math


class Vector:

    #constuctor
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #print returns string in format "(x, y)"
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

    #override for +
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    #override for -
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    #returns a copy of the magnitude of the vector
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    #returns a number that is the dot product of two vectors
    def dot(self, other):
        newX = self.x * other.x
        newY = self.y * other.y
        return newX + newY

    #returns a copy of the vector scaled by a value
    def scale(self, scaleFactor):
        return Vector(self.x * scaleFactor, self.y * scaleFactor)

    #returns a copy of the vector normalized
    def normalize(self):
        #check to make sure we dont divide by 0
        if self.x == 0 and self.y == 0:
          return Vector(0,0)
        else:
          length = self.length()
          return Vector(self.x / length, self.y / length)


