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
	This class encompasses all agents in model: grass, shep, wolves.
	'''
	def __init__(self,model):
		super().__init__(model)

	@abstractmethod
	def acquire_energy(self):
		'''
		Agent acquires energy by growing (grass), eating grass, or consuming other agents
		'''
		pass

	@abstractmethod
	def replicate(self):
		pass

	@abstractmethod
	def move(self):
		pass

	@abstractmethod
	def retire(self):
		pass

class PrimaryProducer(Critter):
	instance = None
	def __init__(self,model,
                 width = 26,
                 height = 25,
                 max_energy = 10.0,
                 increment = 1.0):
		super().__init__(model)
		PrimaryProducer.instance = self
		width = 26
		self.energy = max_energy * np.ones([width,height])
		self.increment = increment
		self.max_energy = max_energy

	def acquire_energy(self):
		'''
		Grass acquires new energy simply by growing
		'''
		width,height = self.energy.shape
		for i in range(width):
			for j in range(height):
				if self.energy[i,j] < self.max_energy:
					self.energy[i,j] += self.increment
					if self.energy[i,j] > self.max_energy:
						self.energy[i,j] = self.max_energy

	def replicate(self):
		'''Subsumed by acquire_energy'''
		pass

	def move(self):
		'''Grass doesn't move'''
		pass

	def retire(self):
		'''Grass doesn't retire'''
		pass

class Consumer(Critter):
	'''
	A Consumer depends on energy supplied by grass, either directly, or by consuming lower level consumers.
	'''
	def __init__(self,model,
                 efficiency = 0.9,
                 energy = 1,
                 minimum_energy = 0):
		super().__init__(model)
		self.efficiency = efficiency
		self.energy = energy
		self.minimum_energy = minimum_energy

	def __str__(self):
		return f'{self.unique_id} {self.energy}'

	def replicate(self): #TODO
		'''Create more instances given additional energy
		'''
		pass

	def move(self):
		'''Move to a neighbouring cell'''
		self.model.grid.move_agent(self,
                                   self.random.choice(
                                       self.model.grid.get_neighborhood(self.pos,
                                                                        moore=True,
                                                                        include_center=False)))

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
	def __init__(self,model,
                 efficiency = 0.9,
                 delta_energy = 1,
                 minimum_energy = 0):
		super().__init__(model,
                         efficiency = efficiency,
                         minimum_energy = minimum_energy)
		self.delta_energy = delta_energy

	def acquire_energy(self):
		'''
		If there is enough grass, eat it
		'''
		i,j = self.pos
		if PrimaryProducer.instance.energy[i,j] > self.delta_energy:
			PrimaryProducer.instance.energy[i,j] -= self.delta_energy
			self.energy += self.delta_energy * self.efficiency
			print (self)


class Consumer2(Consumer):
	'''
	A Consumer depends on energy ultimately supplied by grass, by consuming lower level consumers.
	'''
	def __init__(self,model,
                 efficiency = 0.9,
                 minimum_energy = 0):
		super().__init__(model,
                         efficiency = efficiency,
                         minimum_energy = minimum_energy)

	def acquire_energy(self):
		cellmates = self.model.grid.get_cell_list_contents([self.pos])
		cellmates.pop(
            cellmates.index(self)
        )
		if len(cellmates) == 0: return
		other = self.random.choice(cellmates)
