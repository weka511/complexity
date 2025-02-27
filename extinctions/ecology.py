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

'''The model class from  Thinking Like a Wolf, a Sheep, or a Firefly'''

import numpy as np
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid, PropertyLayer
from critters import Sheep, Wolf

class Ecology(Model):
    '''
    This class represents the Grass/Sheep/Wolf model

    Attributes:
        retired        List of agents that have insufficiet energy to continue.
                       They will be deleted at the end of each step
        T1             Regrowth time for grass
        is_active      Indicates that no class of agents is empty
        grid           Positionsof agents
        datacollector
    '''
    def __init__(self,
                 N1 = 100,
                 N2 = 50,
                 width = 25,
                 height = 25,
                 seed = None,
                 R1 = 0.5,
                 R2 = 0.5,
                 E0 = 1,
                 E1 = 2,
                 E2 = 3,
                 E3 = 1,
                 E4 = 5,
                 T1 = 10):
        super().__init__(seed=seed)
        self.retired = []
        self.T1 = T1
        self.is_active = False

        Sheep.create_agents(model=self, n=N1, R=R1, E3=E3, E4=E4)
        Wolf.create_agents(model=self, n=N2, R=R2, E0=E1, E1=E1, E2=E2)

        self.grid = MultiGrid(width, height, torus=True)
        self.grid.add_property_layer(PropertyLayer('grass', width, height, 0, int))
        for agent in self.agents:
            i = self.rng.choice(width)
            j = self.rng.choice(height)
            self.grid.place_agent(agent, (i, j))

        self.datacollector = DataCollector(
            model_reporters={'grass': self.get_grass},
            agent_reporters={'role': 'role'}
        )

    def step(self):
        '''
        The is the active heart of the model.
        Agents acquire and consume energy, move about, and die.
        '''
        self.regrow_grass()
        self.agents.shuffle_do('step')
        self.remove_all_retired()
        self.datacollector.collect(self)
        self.is_active = min(len(value) for _,value in self.agents_by_type.items()) > 0

    def grass_is_green(self,pos):
        '''
        Used by Sheep to acquire energy. If grass is green at specified position,
        returns True and sets regrowth counter.

        Parameters:
            pos     A tuple representing position of some agent

        Returns:
            True is grass was green
        '''
        grass = self.grid.properties['grass'].data
        if grass[pos] > 0: return False    # if grass is "brown" do nothing
        grass[pos] = self.T1               # Set grass brown
        return True

    def regrow_grass(self):
        '''
        For each patch of brown grass, reduce the timere by one.
        '''
        grass = self.grid.properties['grass'].data
        grass [grass > 0] -= 1

    def get_neighbours(self,pos):
        '''
        Used when we move to find neighboring cells
        '''
        return self.grid.get_neighborhood(pos, moore=True, include_center=False)

    def retire(self,critter):
        '''
        Used to get rid of a (deceased) critter. To avoid breaking the list of agents while
        processsing with shuffle_do, we place the critter on retired list, then use
        remove_all_retired to clean up at the end of the step.
        '''
        self.retired.append(critter)

    def remove_all_retired(self):
        '''
        Remove all retired critters from grid and list of agents
        '''
        for critter in self.retired:
            self.remove_retired(critter)

        self.retired = []

    def remove_retired(self,critter):
        '''
        Remove retired critter from grid and list of agents
        '''
        self.grid.remove_agent(critter)
        critter.remove()

    def get_grass(self):
        '''
        Count number of squares that contain edible grass
        '''
        grass = self.grid.properties['grass'].data
        return np.count_nonzero(grass == 0)

    def get_cellmates(self,pos):
        '''
        Used by a Wolf to locate others sharing the cell
        '''
        return self.grid.get_cell_list_contents([pos])
