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

   Classes in the module represent the patrons of the El Farol bar
'''
import mesa

class Patron(mesa.Agent):
	'''
	A bar Patron can decide whether or not to attend
	'''
	def __init__(self,model,tolerance=25):
		super().__init__(model)
		self.strategies = []
		self.index = 0
		self.happiness = 0
		self.predictions = []
		self.reality = []
		self.tolerance = tolerance
		self.discrepency = 0

	def decide_whether_to_attend(self):
		'''
		Attend if number is predicted to be within capacity
		'''
		self.predictions.append(self.strategies[self.index].get_predicted_attendance())
		self.attend =  self.predictions[-1] < self.capacity

	def calculate_happiness(self):
		'''
		Patron is happy iff they attend venue, and the number of patrons is within capacity
		'''
		self.happiness += (1 if self.attend and self.model.is_comfortable() else 0)

	def record_outcome(self):
		self.reality.append(self.model.get_attendance())
		self.discrepency = abs(self.reality[-1] - self.predictions[-1])

	def review_strategy(self):
		'''
		Periodically compare predictions with reality: if they don't match well enough, change strategy.
		'''
		if self.model.step_number % self.model.review_interval ==0:
			discrepency = sum(abs(a-b) for a,b in zip(self.predictions,self.reality))
			if discrepency>self.tolerance * len(self.predictions):
				self.change_strategy()
				self.reset_accuracy_estimators()

	def change_strategy(self):
		'''Choose a new strategy at random, making sure it isn't the same as the existing one'''
		self.index += self.random.randint(1,len(self.strategies)-1)
		self.index %= len(self.strategies)

	def reset_accuracy_estimators(self):
		self.predictions = []
		self.reality = []
