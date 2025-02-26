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

''' The Wolf and Sheep classes from Thinking Like a Wolf, a Sheep, or a Firefly'''

from abc import abstractmethod, ABC
import numpy as np
from mesa import Agent

class Critter(Agent,ABC):
    '''
    This class encompasses all agents used by the model:  sheep and wolves.
    '''
    def __init__(self,
                 model = None,
                 R = 0.5,
                 role = '',
                 delta_energy = 0):
        super().__init__(model)
        self.R = R
        self.role = role
        self.delta_energy = delta_energy

    def step(self):
        '''
        Executed each step
        '''
        self.move()
        self.acquire_energy()
        if self.retire_if_depleted(): return
        self.replicate()

    @abstractmethod
    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a type of Critter.
        '''

    @abstractmethod
    def acquire_energy(self):
        '''
        Agent acquires energy by eating grass, or consuming other Critters
        '''

    def replicate(self):
        '''Create a new instance of this critter with probability R'''
        if self.rng.uniform(0,1) > self.R: return
        child = self.create()
        self.model.grid.place_agent(child, self.get_random_neighbour())


    def move(self):
        '''
        Move to a neighbouring cell. This expends energy.
        '''
        self.model.grid.move_agent(self,self.get_random_neighbour())
        self.energy -= self.delta_energy

    def retire_if_depleted(self):
        '''
        Used to remove any Critters that don't have enough energy to continue
        '''
        if self.energy >= 0: return False
        self.model.retire(self)
        return True

    def get_random_neighbour(self):
        '''Select a neighbouring cell at random'''
        return self.rng.choice(self.model.get_neighbours(self.get_pos()))

    def get_pos(self):
        '''
        Get position of Critter
        Convert pos from a numpy array to a tuple. This arose as part of
        Issue #38 Replace model.random with model.rn
        '''
        return tuple(self.pos)

class Sheep(Critter):
    '''
    Sheep move around, eat grass, and acquire and expend energy
    '''
    def __init__(self,model=None,R=0.5,E3=1,E4=5):
        super().__init__(model,R=R,role='S',delta_energy=E3)
        self.energy = 1
        self.E3 = E3
        self.E4 = E4

    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a S.
        '''
        return Sheep(model=self.model,R=self.R,E3=self.E3,E4=self.E4)

    def acquire_energy(self):
        '''
        Acquire energy from grass, if it has any.
        '''
        if self.model.grass_is_green(self.get_pos()):
            self.energy += self.E4


class Wolf(Critter):
    '''
    Wolves move around, eat Sheep, and acquire and expend energy
    '''
    def __init__(self,model=None,R=0.5,E1=1,E2=5,E0=5):
        super().__init__(model,R=R,role='W',delta_energy=E1)
        self.energy = E0
        self.E0 = E0
        self.E1 = E1
        self.E2 = E2

    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a Wolf.
        '''
        return Wolf(model=self.model,R=self.R,E0=self.E0, E1=self.E1, E2=self.E2)

    def acquire_energy(self):
        '''
        Eat any sheep that are sharing my location
        '''
        for other in self.model.get_cellmates(self.pos):
            if other.role != self.role:
                self.energy += self.E2
                other.energy = - np.inf
                return
