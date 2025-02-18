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

import unittest
import mesa
import numpy as np
from patron import Patron
from strategy import StrategyFactory

class Bar(mesa.Model):
	'''
	The El Farol bar, which has a finite capacity

	Attributes:
		log             Used to record attendance for each period
		capacity        Venue remains confortable if there are fewer attendees than capacity
		step_number     Keep track of time, so we can review strategies periodically
		review_interval Determine whether to review strategies
		datacollector   Used to record data from run
		running         Used by batch runner
	'''
	def __init__(self,
				 N = 100,
				 seed = None,
				 capacity = 60,
				 review_interval = 5,
				 tolerance = 25,
				 k = 12):
		super().__init__(seed=seed)
		Patron.create_agents(model=self, n=N,tolerance = tolerance)
		self.log = []
		self.capacity = capacity
		self.step_number = 0
		self.review_interval = review_interval
		self.datacollector = mesa.DataCollector(
				model_reporters = {'Attendance' : self.get_attendance,
								   'Gini'       : self.get_gini},
				agent_reporters = {'Happiness' : 'happiness',
								   'Discrepency' : 'discrepency'}
			)

		strategyfactory = StrategyFactory(self.random,N,self.log)

		for patron in self.agents:
			for _ in range(k):
				patron.strategies.append(strategyfactory.create())
			patron.capacity = capacity

		self.running = True

	def step(self):
		'''
		Carry out one step of simulation.
		'''
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

	def get_gini(self):
		'''
		Compute Gini index based on happiness
		'''
		return get_gini_coefficient(np.array([agent.happiness for agent in self.agents]))


	def is_comfortable(self):
		'''
		The bar is comfortable provided the attendance doesn't exceed capacity
		'''
		return self.log[-1] <= self.capacity

def get_gini_coefficient(incomes):
	'''
	Calculate Gini coefficient from
	https://en.wikipedia.org/wiki/Gini_coefficientes

	NB. The test for this case breaks
	'''
	n, = incomes.shape
	total_income = incomes.sum()
	return np.abs(np.subtract.outer(incomes,incomes)).sum() / (2*n*total_income) if total_income > 0 else 0

class TestBar(unittest.TestCase):

	def test_get_gini_coefficient(self):
		'''
		Test case based on https://goodcalculators.com/gini-coefficient-calculator/
		plus one test for case where all inputs are zero
		'''
		self.assertAlmostEqual(0,get_gini_coefficient(np.array([6,6,6])),delta=0.01)
		self.assertAlmostEqual(0,get_gini_coefficient(np.array([0,0,0])),delta=0.01)
		self.assertAlmostEqual(0.28571,get_gini_coefficient(np.array([1000,2000,3000,4000,5000,6000,7000])),delta=0.00005)

if __name__ == '__main__':
	unittest.main()
