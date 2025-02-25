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

''' Template for Mesa programs'''

from abc import abstractmethod
from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid
import seaborn as sns
import pandas as pd

def parse_arguments():
    N1 = 100
    N2 = 50
    max_steps = 52
    frequency = 25
    width = 25
    height = 25
    R1 = 0.5
    R2 = 0.1
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--N1', default=N1, type=int,help = f'Number of first level consumers [{N1}]')
    parser.add_argument('--N2', default=N2, type=int,help = f'Number of second level consumers [{N2}]')
    parser.add_argument('--max_steps', default=max_steps, type=int, help = f'Number of steps for running simulation [{max_steps}]')
    parser.add_argument('--frequency', default=frequency, type=int, help = f'Notify user every [{frequency}] steps')
    parser.add_argument('--width', default=width, type=int,help = f'Width of grid [{width}]')
    parser.add_argument('--height', default=height, type=int,help = f'Height of grid [{height}]')
    parser.add_argument('--R1', default=R1, type=float,help = f'Probability of a sheep reproducing [{R1}]')
    parser.add_argument('--R2', default=R2, type=float,help = f'Probability of a wolf reproducing [{R2}]')
    return parser.parse_args()

class Critter(Agent):
    '''
    This class encompasses all agents used by the model: grass, sheep, wolves.
    '''
    def __init__(self,
                 model = None,
                 R = 0.5,
                 role = ''):
        super().__init__(model)
        self.R = R
        self.role = role

    @abstractmethod
    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a type of Consumer.
        '''

    @abstractmethod
    def acquire_energy(self):
        '''
        Agent acquires energy by growing (grass), eating grass, or consuming other agents
        '''

    def replicate(self):
        '''Create a new instance of this critter'''
        if self.random.uniform(0,1) < self.R:
            child = self.create()
            self.model.grid.place_agent(child, self.get_random_neighbour())


    def move(self):
        '''
        Move to a neighbouring cell
        '''
        self.model.grid.move_agent(self,self.get_random_neighbour())

    def retire_if_depleted(self):
        '''
        Used to remove any consumers that don't have enough energy to continue
        '''
        pass
        # if self.energy < 0:
            # self.model.retire(self)

    def get_random_neighbour(self):
        '''Select a neighbouring cell at random'''
        return self.random.choice(self.model.get_neighbours(self.pos))

class Sheep(Critter):
    def __init__(self,model=None,R=0.5):
            super().__init__(model,R=R,role='S')

    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a S.
        '''
        return Sheep(model=self.model,R=self.R)

    def acquire_energy(self):
        pass

class Wolf(Critter):
    def __init__(self,model=None,R=0.5):
            super().__init__(model,R=R,role='W')

    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a Wolf.
        '''
        return Wolf(model=self.model,R=self.R)

    def acquire_energy(self):
        pass

class Ecology(Model):
    '''
    This class represents the Grass/Sheep/Wolf model
    '''
    def __init__(self,
                 N1 = 100,
                 N2 = 50,
                 width = 25,
                 height = 25,
                 seed = None,
                 R1 = 0.5,
                 R2 = 0.5):
        super().__init__(seed=seed)

        Sheep.create_agents(model=self, n=N1, R=R1)
        Wolf.create_agents(model=self, n=N2, R = R2)
        self.grid = MultiGrid(width, height, torus=True)
        for agent in self.agents:
            i = self.rng.choice(self.grid.width)
            j = self.rng.choice(self.grid.height)
            self.grid.place_agent(agent, (i, j))
        self.datacollector = DataCollector(
                                    model_reporters={},
                                    agent_reporters={'role': 'role'}
                    )
        self.retired = []

    def step(self):
        '''
        The is the active heart of the model. Agents acquire and consume energy, move about
        and die.
        '''
        self.agents.shuffle_do('move')
        self.agents.shuffle_do('acquire_energy')
        self.agents.shuffle_do('retire_if_depleted')
        self.agents.shuffle_do('replicate')
        self.remove_all_retired()
        self.datacollector.collect(self)

    def get_neighbours(self,pos):
        return self.grid.get_neighborhood(pos, moore=True, include_center=False)

    def remove_all_retired(self):
        '''
        Remove all retired consumers from grid and list of agents
        '''
        for consumer in self.retired:
            self.remove_retired(consumer)

        self.retired = []


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
                      seed = args.seed,
                      width = args.width,
                      height = args.height)

    for k in range(args.max_steps):
        ecology.step()
        if k%args.frequency == 0 and k > 0:
            print (f'{k} steps')

    # model_vars = ecology.datacollector.get_model_vars_dataframe()
    agent_vars = ecology.datacollector.get_agent_vars_dataframe()

    with PlotContext(figs=args.figs) as axes:
        sheep = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['S']
        plot1 = sns.lineplot(data=sheep,ax=axes,color='blue',label=f'Sheep N={args.N1},R={args.R1}')
        wolves = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['W']
        sns.lineplot(data=wolves,ax=axes,color='red',label=f'Wolves N={args.N2},R={args.R2}')
        plot1.legend()
        plot1.set(title=f'Sheep and Wolves: grid = {args.width}x{args.height};',
                                      xlabel = 'Time',
                                      ylabel = 'Population')

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
