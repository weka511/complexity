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

'''El Farol simulation--https://sites.santafe.edu/~wbarthur/Papers/El_Farol.pdf'''

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
    capacity = 70
    population = 100
    iterations = 52
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--capacity', default=70, type=int,help = f'Capacity of venue[{capacity}]')
    parser.add_argument('--population', default=1000, type=int,help = f'Number of people available to attend venue [{population}]')
    parser.add_argument('--iterations', default=52, type=int, help = f'Number of iterations for running simulation [{iterations}]')
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
    def __init__(self,random,population=100,log = []):
        self.random = random
        self.population = population
        self.log = log

    def get_predicted_attendance(self):
        if len(self.log) == 0:
            return self.random.random() * self.population
        else:
            return self.get_predicted()

    @abstractmethod
    def get_predicted(self):
        pass

class YesterdaysWeather(Strategy):
    '''
    Predict attendance using a weighted average of the past few weeks.
    '''
    def __init__(self,random,population=100,log = [],n=4,a=0.75,b=0.25):
        super().__init__(random,population,log)
        self.a = a
        self.b = b
        self.n = n

    def get_predicted(self):
        return self.a * np.mean(self.log[-self.n:]) + self.b * self.random.random() * self.population

class Patron(mesa.Agent):
    def __init__(self,model):
        super().__init__(model)
        self.happiness = []

    def decide(self):
        self.attend = self.strategy.get_predicted_attendance() < self.capacity


class ElFarol(mesa.Model):
    def __init__(self,population=100,seed=None,log=[]):
        super().__init__(seed=seed)
        Patron.create_agents(model=self, n=population)
        self.log = log

    def step(self):
        self.agents.shuffle_do('decide')
        self.log.append(sum(1 for agent in self.agents if agent.attend))
        for agent in self.agents:
            agent.happiness.append(1 if agent.attend and self.log[-1] < self.capacity else 0)


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    log = []
    bar = ElFarol(population = args.population,
                  seed = args.seed,
                  log = log)

    strategy = YesterdaysWeather(bar.random,population=args.population,log=log)
    bar.capacity = args.capacity
    for patron in bar.agents:
        patron.strategy = strategy
        patron.capacity = args.capacity

    for _ in range(args.iterations):
        bar.step()

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
