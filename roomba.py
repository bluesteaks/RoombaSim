import math
import random
import time

import roomba_visualize

class Position(object):
	def __init__(self,x,y):
		self.x=x
		self.y=y

	def getX(self):
		return self.x

	def getY(self):
		return self.y

	def getNewPosition(self,angle,speed):
		old_x,old_y=self.getX(),self.getY()

		delta_x=speed*math.sin(math.radians(angle))
		delta_y=speed*math.cos(math.radians(angle))

		new_x=old_x+delta_x
		new_y=old_y+delta_y

		return Position(new_x,new_y)

class RectangularRoom(object):
	def __init__(self,width,height):
		self.width=width
		self.height=height
		self.tiles={}

		for i in range(width):
			for j in range(height):
				self.tiles[i,j]=0

	def cleanTileAtPosition(self,pos):
		self.tiles[math.floor(pos.getX()),math.floor(pos.getY())]=1

	def isTileCleaned(self,m,n):
		return self.tiles[m,n]

	def getNumTiles(self):
		return len(self.tiles)

	def getNumCleanedTiles(self):
		return sum(1 for tile in self.tiles if self.tiles[tile]==1)

	def isPositionInRoom(self,pos):
		return pos.getX()<self.width and pos.getY()<self.height and pos.getX()>=0 and pos.getY()>=0

	def getRandomPosition(self):
		return Position(random.uniform(0,self.width),random.uniform(0,self.height))

class BaseRobot(object):
	def __init__(self,room,speed):
		self.room=room
		self.speed=speed
		self.pos=room.getRandomPosition()
		self.direction=random.randint(0,360)

	def getRobotPosition(self):
		return self.pos

	def getRobotDirection(self):
		return self.direction

	def setRobotPosition(self,position):
		self.pos=position

	def setRobotDirection(self,direction):
		self.direction=direction

class Robot(BaseRobot):
	def updatePositionAndClean(self):
		new_pos=self.getRobotPosition().getNewPosition(self.getRobotDirection(),self.speed)

		if self.room.isPositionInRoom(new_pos):
			self.setRobotPosition(new_pos)
			self.room.cleanTileAtPosition(self.getRobotPosition())
		else:
			self.direction=random.randint(0,360)

class RandomRobot(BaseRobot):
	def updatePositionAndClean(self):
		random.seed()
		self.setRobotDirection(random.randint(0,360))
		new_pos=self.getRobotPosition().getNewPosition(self.getRobotDirection(),self.speed)

		if self.room.isPositionInRoom(new_pos):
			self.setRobotPosition(new_pos)
			self.room.cleanTileAtPosition(self.getRobotPosition())
		else:
			self.direction=random.randint(0,360)

def runSimulation(num_robots,speed,width,height,min_coverage,num_trials,robot_type,delay):
	duration={}
	done=False

	for iteration in range(num_trials):
		if done:
			break

		anim = roomba_visualize.RobotVisualization(num_robots, width, height,delay,iteration)

		room=RectangularRoom(width,height)
		robots={}
		step=0

		for i in range(num_robots):
			if robot_type:
				robots[i]=RandomRobot(room,speed)
			else:	
				robots[i]=Robot(room,speed)		

		anim.update(room,robots)
		while float(room.getNumCleanedTiles())/float(room.getNumTiles())*100 < min_coverage:
			for robot in robots.values():
				robot.updatePositionAndClean()
			anim.update(room,robots)
			step+=1

			if anim.isdone:
				done=True
				break

		duration[iteration]=step
		anim.done()

	if done:
		return -1
	else:
		return sum(value for value in duration.values())/float(num_trials)+1

data={}
settings=roomba_visualize.SettingsVisualization(data)
avg=runSimulation(data['num_robots'],data['robot_speed'],data['room_width'],data['room_height'],data['min_coverage'],data['num_trials'],data['robot_type'],data['delay'])
if avg==-1:
	done=roomba_visualize.DoneVisualization(data,avg,True)
else:
	done=roomba_visualize.DoneVisualization(data,avg,False)