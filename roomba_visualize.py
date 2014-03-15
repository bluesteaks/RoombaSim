import math
import time

from Tkinter import *

class DoneVisualization:
	def __init__(self,data,avg,done):
		self.master=Tk()
		self.master.wm_title("RoombaSim")

		if data['robot_type']:
			texta="It took %d RandomWalkRobot(s) %d step(s) on average (%d trials) to clean a %dx%d room with a minimum coverage of %d percent" %\
		(data['num_robots'],avg,data['num_trials'],data['room_width'],data['room_height'],data['min_coverage'])
		else:
			texta="It took %d Robot(s) %d step(s) on average (%d trials) to clean a %dx%d room with a minimum coverage of %d percent" %\
		(data['num_robots'],avg,data['num_trials'],data['room_width'],data['room_height'],data['min_coverage'])

		if done:
			texta="Simulation was stopped."

		Label(text=texta).pack()
		Button(self.master,text='exit',command=self.master.destroy).pack()
		mainloop()

class SettingsVisualization:
	def __init__(self,data):
		self.master=Tk()
		self.master.wm_title("RoombaSim")

		self.data=data

		Label(text='How many robots?').pack(anchor=W)
		self.num_robots = Entry(self.master, width=10)
		self.num_robots.pack(anchor=NW)
		self.num_robots.insert(0,1)

		Label(text='What robot speed?').pack(anchor=W)
		self.robot_speed = Entry(self.master, width=10)
		self.robot_speed.pack(anchor=NW)
		self.robot_speed.insert(0,1)

		Label(text='Width of room?').pack(anchor=W)
		self.room_width = Entry(self.master, width=10)
		self.room_width.pack(anchor=NW)
		self.room_width.insert(0,10)

		Label(text='Height of room?').pack(anchor=W)
		self.room_height = Entry(self.master, width=10)
		self.room_height.pack(anchor=NW)
		self.room_height.insert(0,10)

		Label(text='Percentage of coverage?').pack(anchor=W)
		self.min_coverage = Entry(self.master, width=10)
		self.min_coverage.pack(anchor=NW)
		self.min_coverage.insert(0,75)

		Label(text='How many trials?').pack(anchor=W)
		self.num_trials = Entry(self.master, width=10)
		self.num_trials.pack(anchor=NW)
		self.num_trials.insert(0,20)

		Label(text='Robot type? (0 for regular, 1 for always random direction)').pack(anchor=W)
		self.robot_type = Entry(self.master, width=10)
		self.robot_type.pack(anchor=NW)
		self.robot_type.insert(0,0)

		Label(text='Delay between steps in seconds').pack(anchor=W)
		self.delay = Entry(self.master, width=10)
		self.delay.pack(anchor=NW)
		self.delay.insert(0,0.02)

		self.okButton=Button(self.master,text='Run Simulation',command=self.onok).pack()
		self.master.update()

		mainloop()

	def onok(self):
		self.data['num_robots']=int(self.num_robots.get())
		self.data['robot_speed']=int(self.robot_speed.get())
		self.data['room_width']=int(self.room_width.get())
		self.data['room_height']=int(self.room_height.get())
		self.data['num_trials']=int(self.num_trials.get())
		self.data['robot_type']=int(self.robot_type.get())
		self.data['min_coverage']=int(self.min_coverage.get())
		self.data['delay']=float(self.delay.get())

		self.master.destroy()

class RobotVisualization:
	def __init__(self,num_robots,width,height,delay,iteration):
		self.delay=delay
		self.isdone=False
		self.iteration=iteration
		self.max_dim=max(width,height)
		self.width=width
		self.height=height
		self.num_robots=num_robots

		self.master=Tk()
		self.master.wm_title("RoombaSim")
		self.w=Canvas(self.master,width=500,height=500)
		self.w.pack()
		self.master.update()

		x1,y1=self._map_coords(0,0)
		x2,y2=self._map_coords(width,height)
		self.w.create_rectangle(x1,y1,x2,y2,fill="white")

		self.tiles={}
		for i in range(width):
			for j in range(height):
				x1,y1=self._map_coords(i,j)
				x2,y2=self._map_coords(i+1,j+1)
				self.tiles[(i,j)]=self.w.create_rectangle(x1,y1,x2,y2,fill="gray")

		for i in range(width+1):
			x1,y1=self._map_coords(i,0)
			x2,y2=self._map_coords(i,height)
			self.w.create_line(x1,y1,x2,y2)

		for i in range(height+1):
			x1,y1=self._map_coords(0,i)
			x2,y2=self._map_coords(width,i)
			self.w.create_line(x1,y1,x2,y2)

		self.robots=None
		self.text=self.w.create_text(25,0,anchor=NW,text=self._status_string(0,0))
		self.button=Button(self.master,text='Stop Simulation',command=self.onstop).pack()
		self.time=0
		self.master.update()

	def onstop(self):
		self.isdone=True

	def _status_string(self,time,num_clean_tiles):
		percent_clean=100*float(num_clean_tiles)/(self.width*self.height)
		return "Iteration %d; Time: %04d; %d tiles (%d%%) cleaned" % (self.iteration+1,time,num_clean_tiles,percent_clean)

	def _map_coords(self, x, y):
		return (250+450*((x-self.width/2.0)/self.max_dim), 250+450*((self.height/2.0-y)/self.max_dim))

	def _draw_robot(self, position, direction):
		x1,y1=self._map_coords(position.getX(),position.getY())
		x2,y2=self._map_coords(position.getX()+math.sin(math.radians(direction)),position.getY()+math.cos(math.radians(direction)))
		return self.w.create_line(x1,y1,x2,y2,fill="red")

	def update(self, room, robots):
		# Removes a gray square for any tiles have been cleaned.
		for i in range(self.width):
			for j in range(self.height):
				if room.isTileCleaned(i, j):
					self.w.delete(self.tiles[(i, j)])
		# Delete all existing robots.
		if self.robots:
			for robot in self.robots:
				self.w.delete(robot)
				self.master.update_idletasks()
		# Draw new robots
		self.robots = []
		for robot in robots.values():
			pos = robot.getRobotPosition()
			x, y = pos.getX(), pos.getY()
			x1, y1 = self._map_coords(x - 0.08, y - 0.08)
			x2, y2 = self._map_coords(x + 0.08, y + 0.08)
			self.robots.append(self.w.create_oval(x1, y1, x2, y2,
												  fill = "black"))
			self.robots.append(
				self._draw_robot(robot.getRobotPosition(), robot.getRobotDirection()))
		# Update text
		self.w.delete(self.text)
		self.time += 1
		self.text = self.w.create_text(
			25, 0, anchor=NW,
			text=self._status_string(self.time, room.getNumCleanedTiles()))
		self.master.update()
		time.sleep(self.delay)

	def done(self):
		time.sleep(2)
		self.master.destroy()