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
    The Grass/Sheep/Wolves model exhibits behaviour that I did not
    expect: it appeared stable with the default values of parameters, but when
    I increased the speed at which grass regrows slightly, regrowth time=20,
    the model ran for some 1,200,000 generations, the wolves become extinct
    suddenly. It is not clear whether this is a limitation of the simple
    model. The proposed model seeks to establish whether the well known
    link between diversity and stability emerges from simple dynamics.
'''

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
import mesa
import seaborn as sns
import pandas as pd

def parse_arguments():
    N1 = 100
    N2 = 50
    max_steps = 52
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--N1', default=N1, type=int,help = f'Number of first level consumers [{N1}]')
    parser.add_argument('--N2', default=N2, type=int,help = f'Number of second level consumers[{N2}]')
    parser.add_argument('--max_steps', default=max_steps, type=int, help = f'Number of steps for running simulation [{max_steps}]')
    return parser.parse_args()

class Critter(mesa.Agent,ABC):
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

    @abstractmethod
    def replicate(self):
        pass

    @abstractmethod
    def move(self):
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
        '''Subsomed by acquire_energy'''

    def move(self):
        '''Grass doesn't move'''
        pass

class Consumer(Critter):
    '''
    A Consumer depends on energy supplied by grass, either directly, or by consuming lower level consumers.
    '''
    def __init__(self,model,efficiency=0.9,energy=1):
        super().__init__(model)
        self.efficiency = efficiency
        self.energy = energy

    def __str__(self):
        return f'{self.unique_id} {self.energy}'

    def replicate(self): #TODO
        '''Create more instances given additional energy
        '''
        pass

    def move(self):
        self.model.grid.move_agent(self,
                                   self.random.choice(
                                       self.model.grid.get_neighborhood(self.pos,
                                                                        moore=True,
                                                                        include_center=False)))

class Consumer1(Consumer):
    '''
    A Consumer1 depends on energy supplied by grass directly.
    '''
    def __init__(self,model,efficiency=0.9,delta_energy = 1):
        super().__init__(model,efficiency=efficiency)
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
    def __init__(self,model,efficiency=0.9):
        super().__init__(model,efficiency=efficiency)

    def acquire_energy(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(
            cellmates.index(self)
        )
        if len(cellmates) == 0: return
        other = self.random.choice(cellmates)

class Ecology(mesa.Model):
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
        self.grid = mesa.space.MultiGrid(width, height, True)
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

    def step(self):
        self.agents.shuffle_do("acquire_energy")
        self.agents.shuffle_do("replicate")
        self.agents.shuffle_do("move")


class PlotContext:
    '''
    Used to allocate subplots and save figure to file

    Class variables:
       Seq    Used if more than one file is created
    '''
    Seq = 0

    def __init__(self, nrows=1,ncols=1,figs='./figs',suptitle=None):
        PlotContext.Seq += 1
        self.nrows = nrows
        self.ncols = ncols
        self.figs = figs
        self.suptitle = suptitle

    def __enter__(self):
        self.fig, self.ax = subplots(nrows=self.nrows,ncols=self.ncols,figsize=(10,6))
        if self.suptitle != None:
            self.fig.suptitle(self.suptitle)
        return self.ax

    def __exit__(self, type, value, traceback):
        self.fig.tight_layout()
        self.fig.savefig(self.get_file_name())

    def get_file_name(self):
        base = basename(splitext(__file__)[0])
        return join(self.figs, base if PlotContext.Seq == 1 else f'{base}{PlotContext.Seq - 0}')


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()
    ecology = Ecology(N1 = args.N1,
                      N2 = args.N2,
                      seed = args.seed)

    for _ in range(args.max_steps):
        ecology.step()

    with PlotContext(figs=args.figs) as axes:
        pass

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
