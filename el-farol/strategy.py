#!/usr/bin/env python

#   Copyright (C) 2025 Simon Crase

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
import numpy as np

class Strategy(ABC):
	'''An abstract class, each of whose implementations predicts attendance'''
	def __init__(self,random,population=100,log = [],m=1,name=''):
		self.random = random
		self.population = population
		self.log = log
		self.m = m
		self.name = name

	def get_predicted_attendance(self):
		'''
		Predict attendance. If there is too little data in the log, choose a random value,
		otherwise delegate to implementation.
		'''
		if len(self.log) < self.m:
			return self.random.random() * self.population
		else:
			return self.get_predicted()

	@abstractmethod
	def get_predicted(self):
		'''Used to predict attendance if there is sufficient data'''
		pass

class MirrorImage(Strategy):
	'''A Strategy that assumes the this week will be the mirror image of last week'''
	def __init__(self,random,population=100,log = []):
		super().__init__(random,population,log,name='MirrorImage')

	def get_predicted(self):
		return self.population - self.log[-1]

class Cycle(Strategy):
	'''
	A Strategy that assumes that the past recurs cyclically,
	so this week will be the same it was `m` weeks ago.
	'''
	def __init__(self,random,population=100,log = [],m=3):
		super().__init__(random,population,log,m=m,name=f'Cycle {m}')

	def get_predicted(self):
		return self.log[-self.m]

class Average(Strategy):
	'''A Strategy that assumes the this week will be the average of the last few weeks'''
	def __init__(self,random,population=100,log = [],m=4):
		super().__init__(random,population,log,name=f'Average {m}')

	def get_predicted(self):
		return  np.mean(self.log[-self.m:])

class Trend(Strategy):
	'''A Strategy that assumes the this week will be the trend from the last few weeks'''
	def __init__(self,random,population=100,log = [],m=4):
		super().__init__(random,population,log,name=f'Average {m}',m=m)

	def get_predicted(self):
		'''
		Fit a trendline to the last `m` attendances, then extrapolate to the current period.
		Clamp into range from [0,population]
		'''
		y = np.array(self.log[-self.m:])
		x = np.arange(0,len(y))
		z = np.polyfit(x,y,1)
		return  min(0,max(z[0] * len(y) + z[1],self.population))

class StrategyFactory:
	'''Used to create strategies'''
	def __init__(self,random,population,log):
		self.random = random
		self.log = log
		self.population = population

	def create(self):
		'''Create a strategy at random'''
		match(self.random.randint(0,4-1)):
			case 0:
				return MirrorImage(self.random,self.population,self.log)
			case 1:
				return Cycle(self.random,self.population,self.log,m=self.random.randint(1,4))
			case 2:
				return Average(self.random,self.population,self.log,m=self.random.randint(2,4))
			case 3:
				return Trend(self.random,self.population,self.log,m=self.random.randint(4,8))

