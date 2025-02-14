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

   Classes in the module represent the El Farol bar
'''

import mesa
from patron import Patron
from strategy import StrategyFactory

class ElFarol(mesa.Model):
	'''
	The El Farol bar, which has a finite capacity
	'''
	def __init__(self,
				 population = 100,
				 seed = None,
				 capacity = 60,
				 review_interval = 5,
				 tolerance = 25,
				 basket_min = 5,
				 basket_max = 12):
		super().__init__(seed=seed)
		Patron.create_agents(model=self, n=population,tolerance = tolerance)
		self.log = []
		self.capacity = capacity
		self.step_number = 0
		self.review_interval = review_interval
		self.datacollector = mesa.DataCollector(
				model_reporters = {'Attendance' : self.get_attendance},
				agent_reporters = {'Happiness' : 'happiness',
								   'Discrepency' : 'discrepency'}
			)

		strategyfactory = StrategyFactory(self.random,population,self.log)

		for patron in self.agents:
			m = self.random.randint(basket_min,basket_max)
			for _ in range(m):
				patron.strategies.append(strategyfactory.create())
			patron.capacity = capacity

		self.running = True

	def step(self):
		self.step_number += 1
		self.agents.shuffle_do('decide_whether_to_attend')
		self.log.append(self.get_attendance())
		self.agents.do('calculate_happiness')
		self.agents.do('record_outcome')
		self.agents.do('review_strategy')
		self.datacollector.collect(self)

	def get_attendance(self):
		'''Calculate the number of Patrons who have decided to attend'''
		return sum(1 for patron in self.agents if patron.attend)

	def is_comfortable(self):
		'''
		The bar is comfortable provided the attendance doesn't exceed capacity
		'''
		return self.log[-1] <= self.capacity
