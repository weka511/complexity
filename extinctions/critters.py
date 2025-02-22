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

'''Agents for Grass/Sheep/Wplves'''

from abc import ABC, abstractmethod
import numpy as np
from mesa import Agent

class Critter(Agent,ABC):
	'''
	This class encompasses all agents in model: grass, sheep, wolves.
	'''
	def __init__(self,
				 model = None,
				 role = None):
		super().__init__(model)
		self.role = role

	@abstractmethod
	def acquire_energy(self):
		'''
		Agent acquires energy by growing (grass), eating grass, or consuming other agents
		'''

	def replicate(self):
		'''Create a child if appropriate (not grass)'''
		pass

	def move(self):
		'''Change location if appropriate (not grass)'''
		pass

	def retire(self):
		'''Remove agent from model if appropriate (not grass)'''
		pass


class PrimaryProducer(Critter):
	'''This class produces energy directly, and supplies it to the other Agents.'''

	instance = None # There can be only one Primary Producer

	def __init__(self,
				 model = None,
                 width = 26,
                 height = 25,
                 max_energy = 10.0,
                 increment = 1.0):
		super().__init__(model = model,role = 'PP')
		if PrimaryProducer.instance != None: raise RuntimeError('There can be only one Primary Producer')
		PrimaryProducer.instance = self
		self.cell_energy = max_energy * np.ones([width,height])
		self.increment = increment
		self.max_energy = max_energy
		self.energy = self.cell_energy.sum()

	def acquire_energy(self):
		'''
		Grass acquires new energy simply by growing
		'''
		width,height = self.cell_energy.shape
		for i in range(width):
			for j in range(height):
				if self.cell_energy[i,j] < self.max_energy:
					self.cell_energy[i,j] += self.increment
					if self.cell_energy[i,j] > self.max_energy:
						self.cell_energy[i,j] = self.max_energy
		self.energy = self.cell_energy.sum()


class Consumer(Critter):
	'''
	A Consumer depends on energy supplied by grass, either directly, or by consuming lower level consumers.
	'''
	def __init__(self,
				 model = None,
                 efficiency = 0.9,
                 energy = 1,
                 minimum_energy = 0,
				 replication_threshold = 5.0,
				 replication_cost = 3.0,
				 replication_efficiency = 0.9,
				 role = None):
		super().__init__(model = model,
						 role = role)
		self.efficiency = efficiency
		self.energy = energy
		self.minimum_energy = minimum_energy
		self.replication_threshold = replication_threshold
		self.replication_cost = replication_cost
		self.replication_efficiency = replication_efficiency

	def __str__(self):
		return f'{self.unique_id} {self.energy}'

	@abstractmethod
	def create(self):
		'''
		Factory method--used to replicate. It creates a new instance of a type of Consumer.
		'''

	def replicate(self):
		'''
		Create more instances given additional energy
		'''
		if self.energy < self.replication_threshold: return
		child = self.create()
		self.energy -= self.replication_cost
		child.energy += self.replication_cost * self.replication_efficiency
		self.model.grid.place_agent(child, self.get_random_neighbour())


	def move(self):
		'''Move to a neighbouring cell'''
		self.model.grid.move_agent(self,self.get_random_neighbour())

	def get_random_neighbour(self):
		'''Select a neighbouring cell at random'''
		return self.random.choice(
			self.model.grid.get_neighborhood(self.pos,
											 moore=True,
											 include_center=False))

	def retire(self):
		'''
		Used to remove any consumers that don't have enough energy to continue
		'''
		if self.energy < self.minimum_energy:
			self.model.retire(self)


class Consumer1(Consumer):
	'''
	A Consumer1 depends on energy supplied by grass directly.
	'''
	def __init__(self,
				 model = None,
                 efficiency = 0.9,
                 delta_energy = 1,
                 minimum_energy = 0,
				 replication_threshold = 5.0,
				 replication_cost = 3.0,
				 replication_efficiency = 0.9):
		super().__init__(model = model,
                         efficiency = efficiency,
                         minimum_energy = minimum_energy,
						 replication_threshold = replication_threshold,
						 replication_cost = replication_cost,
						 replication_efficiency = replication_efficiency,
						 role = 'C1')
		self.delta_energy = delta_energy

	def create(self):
		'''
		Factory method--used to replicate. It creates a new instance of a Consumer1.
		'''
		return Consumer1(self.model,
						 efficiency=self.efficiency,
						 delta_energy = self.delta_energy,
						 minimum_energy = self.minimum_energy,
						 replication_threshold = self.replication_threshold,
						 replication_cost = self.replication_cost,
						 replication_efficiency = self.replication_efficiency)

	def acquire_energy(self):
		'''
		If there is enough grass, eat it
		'''
		i,j = self.pos
		if PrimaryProducer.instance.cell_energy[i,j] > self.delta_energy:
			PrimaryProducer.instance.cell_energy[i,j] -= self.delta_energy
			self.energy += self.delta_energy * self.efficiency


class Consumer2(Consumer):
	'''
	A Consumer depends on energy ultimately supplied by grass, by consuming lower level consumers.
	'''
	def __init__(self,
				 model = None,
                 efficiency = 0.9,
                 minimum_energy = 0,
				 replication_threshold = 5.0,
				 replication_cost = 3.0,
				 replication_efficiency = 0.9):
		super().__init__(model = model,
                         efficiency = efficiency,
                         minimum_energy = minimum_energy,
						 replication_threshold = replication_threshold,
						 replication_cost = replication_cost,
						 replication_efficiency = replication_efficiency,
						 role = 'C2')

	def create(self):
		'''
		Factory method--used to replicate. It creates a new instance of a Consumer2.
		'''
		return Consumer2(self.model,
						 efficiency=self.efficiency,
						 delta_energy = self.delta_energy,
						 minimum_energy = self.minimum_energy,
						 replication_threshold = self.replication_threshold,
						 replication_cost = self.replication_cost,
						 replication_efficiency = self.replication_efficiency)

	def acquire_energy(self): #FIXME
		cellmates = self.model.grid.get_cell_list_contents([self.pos])
		cellmates.pop(
            cellmates.index(self)
        )
		if len(cellmates) == 0: return
		other = self.random.choice(cellmates)
