from Game.Point import Point,PointType
import random
import time
from enum import Enum
import numpy as np

class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    @classmethod
    def reverse(self, direction):
        match direction:
            case Direction.UP:
                return Direction.DOWN
            case Direction.RIGHT:
                return Direction.LEFT
            case Direction.DOWN:
                return Direction.UP
            case Direction.LEFT:
                return Direction.RIGHT
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError
    
    @classmethod
    def rotateCW(self, direction):
        match direction:
            case Direction.UP:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.LEFT
            case Direction.LEFT:
                return Direction.UP
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError

    @classmethod
    def rotateCCW(self, direction):
        match direction:
            case Direction.UP:
                return Direction.LEFT
            case Direction.LEFT:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.UP
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError

    @classmethod
    def getOffset(self, direction):
        match direction:
            case Direction.UP:
                return [1, 0]
            case Direction.RIGHT:
                return [0, 1]
            case Direction.DOWN:
                return [-1, 0]
            case Direction.LEFT:
                return [0, -1]
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError


class Grid:
    def __init__(self, cols, rows, agent):
        self.colNum = cols
        self.rowNum = rows
        self.numPoints = self.colNum * self.rowNum
        self.points = [[Point(PointType.EMPTY, x, y) for x in range(0, cols)] for y in range(0, rows)] #Initialize all points as empty
        self.snake = None
        self.food = None
        self.agent = agent
        self.gameRunning = False
    

    def Setup(self):
        for x in range(0, self.colNum):
            for y in range(0, self.rowNum):
                if(x == 0 or x == self.colNum-1)or(y == 0 or y == self.rowNum-1):
                    self.points[y][x].SetType(PointType.WALL) #Set border points as walls
                else:
                    self.points[y][x].SetType(PointType.EMPTY) #Set other points as empty
        headX = self.colNum//2
        headY = self.rowNum//2
        self.PlaceSnake(4, [headX, headY], Direction.UP)
        self.placeRandomFood()

    def startLoopNoGUI(self):
        self.gameRunning = True
        while(self.gameRunning):
            self.gameLoop()
    
    def getPointType(self, point):
        return point.GetType().value
    
    def flattenGrid(self):
        flat = np.array(self.points)
        flat = flat.flatten()
        out = np.vectorize(self.getPointType)(flat)
        return out

    def reset(self):
        if(self.snake != None):
            while(self.snake.body):
                point = self.snake.body.pop()
                point.SetType(PointType.EMPTY)
        if(self.food != None):
            self.food.SetType(PointType.EMPTY)
        self.snake = None
        self.food = None
        
        headX = self.colNum//2
        headY = self.rowNum//2
        self.PlaceSnake(4, [headX, headY], Direction.UP)
        self.placeRandomFood()

    def GameOver(self):
        self.gameRunning = False
        #Probably do other stuff later too

    def gameLoop(self):
        self.agent.MakeMove(self)

    def PlaceSnake(self, size, position, heading):
        from Game.Snake import Snake
        self.snake = Snake(self, size, heading)
        self.snake.BuildBody(position, heading)

    def getPoint(self, x, y):
        return self.points[y][x]

    def getAdjPoint(self, point, direction):
        x, y = point.GetPosition()
        offset = Direction.getOffset(direction)
        return self.points[y+offset[0]][x+offset[1]]
    
    def getEmptyPoints(self):
        freePoints = []
        for x in range(0, self.colNum):
            for y in range(0, self.rowNum):
                point = self.points[y][x]
                if(point.GetType() == PointType.EMPTY):
                    freePoints.append(point)
        return freePoints
    
    def getState(self):
        snake = self.snake
        food = self.food
        heading = snake.heading
        headPos = snake.head.GetPosition()
        
        foodPos = food.GetPosition()

        lookLeft = snake.Look(Direction.rotateCCW(heading))
        lookForward = snake.Look(heading)
        lookRight = snake.Look(Direction.rotateCW(heading))

        state = np.asarray([headPos[0],
                            headPos[1],
                            heading.value,

                            lookLeft[0],
                            lookLeft[1],
                            lookForward[0],
                            lookForward[1],
                            lookRight[0],
                            lookRight[1],

                            snake.bodySize,
                            foodPos[0],
                            foodPos[1],
                            self.GetDistance(snake.head, food)
                            ], dtype=np.float32)

        return state

    #manhattan distance between 2 points
    def GetDistance(self, point1, point2):
        x1 = point1.x
        y1 = point1.y

        x2 = point2.x
        y2 = point2.y

        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def placeRandomFood(self):
        freePoints = self.getEmptyPoints()
        if(freePoints):
            point = random.choice(freePoints)
            point.SetType(PointType.FOOD)
            self.food = point
        else:
            #A perfect game has somehow been played
            #TODO: What to do here?
            pass

    def placeFoodAt(self, position):
        point = self.points[position[0]][position[1]]
        point.SetType(PointType.FOOD)
        self.food = point

    
