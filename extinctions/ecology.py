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

'''Grass/Sheep/Wolf model'''

import unittest
from mesa import Model
from mesa.space import MultiGrid
from critters import Consumer1, Consumer2, PrimaryProducer

class Ecology(Model):
	def __init__(self,
				 N1 = 100,
				 N2 = 50,
				 width = 25,
				 height = 25,
				 seed = None,
				 energy_per_cell = 10.0,
				 increment_per_cell = 1.0):
		super().__init__(seed=seed)

		Consumer1.create_agents(model=self, n=N1)
		Consumer2.create_agents(model=self, n=N2)
		self.grid = MultiGrid(width, height, True)
		for agent in self.agents:
			i = self.rng.choice(self.grid.width)
			j = self.rng.choice(self.grid.height)
			self.grid.place_agent(agent, (i, j))

		PrimaryProducer.create_agents(model = self,
			                          n = 1,
			                          width = width,
			                          height = height,
			                          max_energy = energy_per_cell,
			                          increment = increment_per_cell)

		self.retired = []

	def step(self):
		self.agents.shuffle_do('acquire_energy')
		self.agents.shuffle_do('replicate')
		self.agents.shuffle_do('retire')
		self.agents.shuffle_do('move')
		self.remove_all_retired()

	def retire(self,consumer):
		'''
		Place consumer on retired list
		'''
		self.retired.append(consumer)

	def remove_all_retired(self):
		'''
		Remove all retired consumers from grid and list of agents
		'''
		for consumer in self.retired:
			self.remove_retired(consumer)

		self.retired = []

	def remove_retired(self,consumer):
		'''
		Remove retired consumer from grid and list of agents
		'''
		self.grid.remove_agent(consumer)
		consumer.remove()

class TestRetire(unittest.TestCase):

	def test_retire(self):
		'''
		Remove consumer: verify that it is removed from grid ans list of agents
		'''
		ecology = Ecology(N1 = 2,
						  N2 = 1,
						  seed = 0)
		self.assertEqual(4,len(ecology.agents),'Verify initial total agents')
		self.assertEqual(3,len(ecology.grid.agents),'Verify initial agents in grid')
		retiree = ecology.grid.agents[1]
		ecology.remove_retired(retiree)
		self.assertEqual(3,len(ecology.agents),'Verify final total agents')
		self.assertEqual(2,len(ecology.grid.agents),'Verify final agents in grid')

if __name__ == '__main__':
	unittest.main()


