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
    parser = ArgumentParser(__doc__)
    capacity = 60
    population = 100
    iterations = 52
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--capacity', default=capacity, type=int,help = f'Capacity of venue[{capacity}]')
    parser.add_argument('--population', default=population, type=int,help = f'Number of people available to attend venue [{population}]')
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of iterations for running simulation [{iterations}]')
    return parser.parse_args()

class PlotContext:
    '''Used to allocate subplots and save figure to file'''
    Seq = 0
    def __init__(self, nrows=1,ncols=1,figs='./figs'):
        PlotContext.Seq += 1
        self.nrows = nrows
        self.ncols = ncols
        self.figs = figs

    def __enter__(self):
        self.fig, self.ax = subplots(nrows=self.nrows,ncols=self.ncols)
        return self.ax

    def __exit__(self, type, value, traceback):
        self.fig.tight_layout()
        self.fig.savefig(self.get_file_name())

    def get_file_name(self):
        base = basename(splitext(__file__)[0])
        return join(self.figs, base if PlotContext.Seq == 1 else f'{base}{PlotContext.Seq - 0}')

class Strategy(ABC):
    '''An abstract class, whose implementation predict attendance'''
    def __init__(self,random,population=100,log = [],m=1,name=''):
        self.random = random
        self.population = population
        self.log = log
        self.m = m
        self.name = name

    def get_predicted_attendance(self):
        if len(self.log) < self.m:
            return self.random.random() * self.population
        else:
            return self.get_predicted()

    @abstractmethod
    def get_predicted(self):
        pass

class MirrorImage(Strategy):
    def __init__(self,random,population=100,log = []):
        super().__init__(random,population,log,name='MirrorImage')

    def get_predicted(self):
        return self.population - log[-1]

class Cycle(Strategy):
    def __init__(self,random,population=100,log = [],m=3):
        super().__init__(random,population,log,m=m,name=f'Cycle {m}')

    def get_predicted(self):
        return log[-self.m]

class Average(Strategy):
    def __init__(self,random,population=100,log = [],m=4):
        super().__init__(random,population,log,name=f'Average {m}')

    def get_predicted(self):
        return  np.mean(self.log[-self.m:])

class StrategyFactory:
    def __init__(self,random):
        self.random = random
    def create(self,random,population,log):
        match(self.random.randint(0,3-1)):
            case 0:
                return MirrorImage(random,population,log)
            case 1:
                return Cycle(random,population,log,m=random.randint(2,4))
            case 2:
                return Average(random,population,log,m=random.randint(2,4))


class Patron(mesa.Agent):
    '''
    A bar Patron can decide whether or not to attend
    '''
    def __init__(self,model,review_interval = 5,minimum_happiness = 0.25):
        super().__init__(model)
        self.happiness = []
        self.strategies = []
        self.index = 0
        self.review_interval = review_interval
        self.minimum_happiness = minimum_happiness

    def decide(self):
        self.attend = self.strategies[self.index].get_predicted_attendance() < self.capacity

    def calculate_happiness(self,bar):
        self.happiness.append(1 if self.attend and bar.is_comfortable() else 0)

    def review_strategy(self,step_number,random):
        if step_number>0 and step_number % self.review_interval ==0:
            if sum(self.happiness) < step_number * self.minimum_happiness:
                saved_index = self.index
                while saved_index == self.index:
                    self.index = random.randint(0,len(self.strategies)-1)

class ElFarol(mesa.Model):
    '''
    The El Farol bar, which has a finite capacity
    '''
    def __init__(self,population=100,seed=None,log=[],capacity = 60):
        super().__init__(seed=seed)
        Patron.create_agents(model=self, n=population)
        self.log = log
        self.capacity = capacity

    def step(self,step_number):
        self.agents.shuffle_do('decide')
        self.log.append(sum(1 for agent in self.agents if agent.attend))
        for patron in self.agents:
            patron.calculate_happiness(self)
            patron.review_strategy(step_number,self.random)

    def is_comfortable(self):
        '''
        The bar is comfortable provided the attendance doesn't exceed capacity
        '''
        return self.log[-1] <= self.capacity


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    log = []
    bar = ElFarol(population = args.population,
                  seed = args.seed,
                  log = log,
                  capacity = args.capacity)
    strategyfactory = StrategyFactory(bar.random)

    for patron in bar.agents:
        for _ in range(5): #FIXME
            patron.strategies.append(strategyfactory.create(bar.random,args.population,log))
        patron.capacity = args.capacity


    for step_number in range(args.iterations):
        bar.step(step_number)

    happiness = [sum(agent.happiness) for agent in bar.agents]
    with PlotContext(nrows=2,ncols=1,figs=args.figs) as axes:
        p1 = sns.barplot(log,ax=axes[0],color='blue',label='Attendance')
        p2 = sns.lineplot([args.capacity]*args.iterations,ax=axes[0],color='red',label='Threshold')
        p1.set_title('Weekly attendance')
        p1.legend()
        g1 = sns.histplot(happiness, discrete=True,ax=axes[1],color='blue')
        g1.set_title('Happiness')

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
