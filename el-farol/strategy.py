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

'''
   El Farol simulation

   Inductive Reasoning and Bounded Rationality, Brian Arthur,

   https://sites.santafe.edu/~wbarthur/Papers/El_Farol.pdf

   Classes in the module are used to predict attendance at the El Farol bar
'''

from abc import ABC, abstractmethod
import numpy as np

class Strategy(ABC):
	'''
	An abstract class, each of whose implementations predicts attendance

	Attributes:
	    random    Random number generator
		N         Total number of patrons
		m         The minimim number of data points in log required to make a prediction
		name      Name of predictor (used to prevent duplicates)
	'''
	def __init__(self,random,N=100,log = [],m=1,name=''):
		self.random = random
		self.N = N
		self.log = log
		self.m = m
		self.name = name

	def get_predicted_attendance(self):
		'''
		Predict attendance. If there is too little data in the log, choose a random value,
		otherwise delegate to implementation.
		'''
		if len(self.log) < self.m:
			return self.random.random() * self.N
		else:
			return self.get_predicted()

	@abstractmethod
	def get_predicted(self):
		'''Used to predict attendance if there is sufficient data'''
		pass

class MirrorImage(Strategy):
	'''A Strategy that assumes the this week will be the mirror image of last week'''
	def __init__(self,random,N=100,log = []):
		super().__init__(random,N,log,name='MirrorImage',m=1)

	def get_predicted(self):
		return self.N - self.log[-1]

class Cycle(Strategy):
	'''
	A Strategy that assumes that the past recurs cyclically,
	so this week will be the same it was `m` weeks ago.
	'''
	def __init__(self,random,N=100,log = [],m=3):
		super().__init__(random,N,log,m=m,name=f'Cycle {m}')

	def get_predicted(self):
		return self.log[-self.m]

class Average(Strategy):
	'''A Strategy that assumes the this week will be the average of the last few weeks'''
	def __init__(self,random,N=100,log = [],m=4):
		super().__init__(random,N,log,name=f'Average {m}',m=m)

	def get_predicted(self):
		return  np.mean(self.log[-self.m:])

class Trend(Strategy):
	'''
	A Strategy that assumes the this week will continue the trend from the last few weeks

	Attributes
	    n    The number of weeks that we are targetting. If we have fewer points, use
		     what we have, as long as there are at least two points.
	'''
	def __init__(self,random,N=100,log = [],n=4,m=2):
		super().__init__(random,N,log,name=f'Average {n}',m=m)
		self.n = n

	def get_predicted(self):
		'''
		Fit a trendline to the last `n` attendances, then extrapolate to the current period.
		Clamp into range from [0,N]
		'''
		y = np.array(self.log[-self.n:])
		x = np.arange(0,len(y))
		z = np.polyfit(x,y,1)
		return  min(0,max(z[0] * len(y) + z[1],self.N))

class StrategyFactory:
	'''Used to create strategies'''
	def __init__(self,random,N,log,n_strategies=100):
		self.random = random
		self.log = log
		self.N = N
		self.strategies = [self.build(len(Strategy.__subclasses__())) for _ in range(n_strategies)]

	def build(self,n_strategy_types):
		'''Create a strategy at random'''
		match(self.random.randint(0,n_strategy_types-1)):
			case 0:
				return MirrorImage(self.random,self.N,self.log)
			case 1:
				return Cycle(self.random,self.N,self.log,m=self.random.randint(1,12)) #FIXME -- magic numbers
			case 2:
				return Average(self.random,self.N,self.log,m=self.random.randint(2,4))  #FIXME -- magic numbers
			case 3:
				return Trend(self.random,self.N,self.log,n=self.random.randint(4,8))  #FIXME -- magic numbers

	def create(self):
		'''Used by Clients to create a strategy: actually look up from list.'''
		n = len(self.strategies)
		return self.strategies[self.random.randint(0,n-1)]

