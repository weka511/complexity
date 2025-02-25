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

''' Thinking Like a Wolf, a Sheep, or a Firefly -- Uri Wilensky'''

from abc import abstractmethod
from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid, PropertyLayer
import seaborn as sns
import pandas as pd

def parse_arguments():
    N1 = 100
    N2 = 100
    nsteps = 50
    freq = 5
    width = 25
    height = 25
    R1 = 0.25
    R2 = 0.25
    E1 = 1
    E2 = 6
    E0 = 5#10
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--N1', default=N1, type=int,help = f'Initial number of sheep[{N1}]')
    parser.add_argument('--N2', default=N2, type=int,help = f'Initial number of wolves [{N2}]')
    parser.add_argument('--nsteps', default=nsteps, type=int, help = f'Number of steps for running simulation [{nsteps}]')
    parser.add_argument('--freq', default=freq, type=int, help = f'Notify user every [{freq}] steps')
    parser.add_argument('--width', default=width, type=int,help = f'Width of grid [{width}]')
    parser.add_argument('--height', default=height, type=int,help = f'Height of grid [{height}]')
    parser.add_argument('--R1', default=R1, type=float,help = f'Probability of a sheep reproducing [{R1}]')
    parser.add_argument('--R2', default=R2, type=float,help = f'Probability of a wolf reproducing [{R2}]')
    parser.add_argument('--E0', default=E0, type=float,help = f'Starting energy for a wolf [{E0}]')
    parser.add_argument('--E1', default=E1, type=float,help = f'Cost of movement for a wolf [{E1}]')
    parser.add_argument('--E2', default=E2, type=float,help = f'Energy gain for a wolf that eats a sheep [{E2}]')
    return parser.parse_args()

class Critter(Agent):
    '''
    This class encompasses all agents used by the model:  sheep and wolves.
    '''
    def __init__(self,
                 model = None,
                 R = 0.5,
                 role = ''):
        super().__init__(model)
        self.R = R
        self.role = role

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
        if self.random.uniform(0,1) > self.R: return
        child = self.create()
        self.model.grid.place_agent(child, self.get_random_neighbour())


    def move(self):
        '''
        Move to a neighbouring cell
        '''
        self.model.grid.move_agent(self,self.get_random_neighbour())

    def retire_if_depleted(self):
        '''
        Used to remove any Critters that don't have enough energy to continue
        '''
        if self.energy >= 0: return False
        self.model.retire(self)
        return True

    def get_random_neighbour(self):
        '''Select a neighbouring cell at random'''
        return self.random.choice(self.model.get_neighbours(self.pos))

class Sheep(Critter):
    def __init__(self,model=None,R=0.5):
            super().__init__(model,R=R,role='S')
            self.energy = 1



    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a S.
        '''
        return Sheep(model=self.model,R=self.R)

    def acquire_energy(self):
        grass = self.model.grid.properties['grass']
        y = grass.data[self.pos]
        if grass.data[self.pos] ==0:
            grass.data[self.pos] += 10 #FIXME
            self.energy += 5 #FIXME
        else:
            grass.data[self.pos] -= 1

class Wolf(Critter):
    def __init__(self,model=None,R=0.5,E1=1,E2=5,E0=5):
        super().__init__(model,R=R,role='W')
        self.energy = E0
        self.E0 = E0
        self.E1 = E1
        self.E2 = E2

    def create(self):
        '''
        Factory method--used to replicate. It creates a new instance of a Wolf.
        '''
        return Wolf(model=self.model,R=self.R,E0=self.E0, E1=self.E1, E2=self.E2)

    def move(self):
        super().move()
        self.energy -= self.E1

    def acquire_energy(self):
        '''
        Eat any sheep that are sharing my location
        '''
        for other in self.model.grid.get_cell_list_contents([self.pos]):
            if other.role != self.role:
                self.energy += self.E2
                other.energy = - np.inf
                return

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
                 R2 = 0.5,
                 E0 = 1,
                 E1 = 2,
                 E2 = 3):
        super().__init__(seed=seed)

        Sheep.create_agents(model=self, n=N1, R=R1)
        Wolf.create_agents(model=self, n=N2, R = R2, E0=E1, E1= E1, E2 = E2)
        self.grid = MultiGrid(width, height, torus=True)
        for agent in self.agents:
            i = self.rng.choice(width)
            j = self.rng.choice(height)
            self.grid.place_agent(agent, (i, j))
        self.datacollector = DataCollector(
                                    model_reporters={},
                                    agent_reporters={'role': 'role'}
                    )
        self.retired = []
        self.grid.add_property_layer(PropertyLayer('grass', width, height, 0, int))


    def step(self):
        '''
        The is the active heart of the model. Agents acquire and consume energy, move about
        and die.
        '''
        self.agents.shuffle_do('step')
        self.remove_all_retired()
        self.datacollector.collect(self)

    def get_neighbours(self,pos):
        return self.grid.get_neighborhood(pos, moore=True, include_center=False)

    def retire(self,consumer):
        '''
        Used to get rid of a (deceased) Consumer. To avoid breaking the list of agents while
        processsing with shuffle_do, we place the consumer on retired list, then use
        remove_all_retired to clean up at the end of the step.
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

    args = parse_arguments()

    ecology = Ecology(N1 = args.N1,
                      N2 = args.N2,
                      seed = args.seed,
                      width = args.width,
                      height = args.height,
                      R1 = args.R1,
                      R2 = args.R2,
                      E0 = args.E0,
                      E1 = args.E1,
                      E2 = args.E2)

    for k in range(args.nsteps):
        ecology.step()
        if k%args.freq == 0 and k > 0:
            print (f'{k} steps')

    # model_vars = ecology.datacollector.get_model_vars_dataframe()
    agent_vars = ecology.datacollector.get_agent_vars_dataframe()

    with PlotContext(figs=args.figs) as axes:
        sheep = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['S']
        plot1 = sns.lineplot(data=sheep,ax=axes,color='blue',label=f'Sheep N={args.N1},R={args.R1}')
        wolves = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['W']
        sns.lineplot(data=wolves,ax=axes,color='red',label=f'Wolves N={args.N2},R={args.R2},E0={args.E0},E1={args.E1},E2={args.E2}')
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
