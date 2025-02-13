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
    review_interval = 5
    minimum_happiness = 0.25
    basket_min = 5
    basket_max = 12
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--capacity', default=capacity, type=int,help = f'Capacity of venue[{capacity}]')
    parser.add_argument('--population', default=population, type=int,help = f'Number of people available to attend venue [{population}]')
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of iterations for running simulation [{iterations}]')
    parser.add_argument('--review_interval', default=review_interval, type=int,
                        help = f'Review strategy every few iterations[{review_interval}]')
    parser.add_argument('--minimum_happiness', default=minimum_happiness, type=float,
                        help = f'Change strategy unless happiness per step is at leaset this value[{minimum_happiness}]')
    parser.add_argument('--basket_min', default=basket_min, type=int,help = f'Minimum size for basket of strategies[{basket_min}]')
    parser.add_argument('--basket_max', default=basket_max, type=int,help = f'Maximum size for basket of strategies[{basket_max}]')
    return parser.parse_args()

class PlotContext:
    '''Used to allocate subplots and save figure to file'''
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

class Strategy(ABC):
    '''An abstract class, each of whose implementations predicts attendance'''
    def __init__(self,random,population=100,log = [],m=1,name=''):
        self.random = random
        self.population = population
        self.log = log
        self.m = m
        self.name = name

    def get_predicted_attendance(self):
        '''
        Predict attendance. If there is too little data in the log, choose a random value,
        otherwise delegate to implementation.
        '''
        if len(self.log) < self.m:
            return self.random.random() * self.population
        else:
            return self.get_predicted()

    @abstractmethod
    def get_predicted(self):
        '''Used to predict attendance if there is sufficient data'''
        pass

class MirrorImage(Strategy):
    '''A Strategy that assumes the this week will be the mirror image of last week'''
    def __init__(self,random,population=100,log = []):
        super().__init__(random,population,log,name='MirrorImage')

    def get_predicted(self):
        return self.population - self.log[-1]

class Cycle(Strategy):
    '''A Strategy that assumes the this week will be the same as an earlier week'''
    def __init__(self,random,population=100,log = [],m=3):
        super().__init__(random,population,log,m=m,name=f'Cycle {m}')

    def get_predicted(self):
        return self.log[-self.m]

class Average(Strategy):
    '''A Strategy that assumes the this week will be the average of the last few weeks'''
    def __init__(self,random,population=100,log = [],m=4):
        super().__init__(random,population,log,name=f'Average {m}')

    def get_predicted(self):
        return  np.mean(self.log[-self.m:])

class Trend(Strategy):
    '''A Strategy that assumes the this week will be the trend from the last few weeks'''
    def __init__(self,random,population=100,log = [],m=4):
        super().__init__(random,population,log,name=f'Average {m}',m=m)

    def get_predicted(self):
        '''
        Fit a trendline to the last `m` attendances, then extrapolate to the current period.
        Clamp into range from [0,population]
        '''
        y = np.array(self.log[-self.m:])
        x = np.arange(0,len(y))
        z = np.polyfit(x,y,1)
        return  min(0,max(z[0] * len(y) + z[1],self.population))

class StrategyFactory:
    '''Used to create strategies'''
    def __init__(self,random):
        self.random = random
    def create(self,population,log):
        '''Create a strategy at random'''
        match(self.random.randint(0,4-1)):
            case 0:
                return MirrorImage(self.random,population,log)
            case 1:
                return Cycle(self.random,population,log,m=self.random.randint(1,4))
            case 2:
                return Average(self.random,population,log,m=self.random.randint(2,4))
            case 3:
                return Trend(self.random,population,log,m=self.random.randint(4,8))


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
        self.happiness_total = 0

    def decide_whether_to_attend(self):
        self.attend = self.strategies[self.index].get_predicted_attendance() < self.capacity

    def calculate_happiness(self):
        self.happiness_total += (1 if self.attend and self.model.is_comfortable() else 0)
        self.happiness.append(1 if self.attend and self.model.is_comfortable() else 0)

    def get_expected_happiness(self):
        return self.model.step_number * self.minimum_happiness

    def review_strategy(self):
        if self.model.step_number % self.review_interval ==0:
            if sum(self.happiness) < self.get_expected_happiness():
                saved_index = self.index
                while saved_index == self.index:
                    self.index = self.random.randint(0,len(self.strategies)-1)

class ElFarol(mesa.Model):
    '''
    The El Farol bar, which has a finite capacity
    '''
    def __init__(self,population=100,seed=None,log=[],capacity = 60,review_interval = 5,minimum_happiness = 0.25):
        super().__init__(seed=seed)
        Patron.create_agents(model=self, n=population,review_interval = 5,minimum_happiness = 0.25)
        self.log = log
        self.capacity = capacity
        self.step_number = 0
        self.datacollector = mesa.DataCollector(
            model_reporters={'Attendance' : self.get_attendance},
            agent_reporters={'Happiness' : 'happiness_total'}
        )

    def step(self):
        self.step_number += 1
        self.agents.shuffle_do('decide_whether_to_attend')
        self.log.append(self.get_attendance())
        self.agents.do('calculate_happiness')
        self.agents.do('review_strategy')
        self.datacollector.collect(self)

    def get_attendance(self):
        '''Calculate the number of Patrons who have decided to attend'''
        return sum(1 for patron in self.agents if patron.attend)

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
                  capacity = args.capacity,
                  review_interval = args.review_interval,
                  minimum_happiness = args.minimum_happiness)
    strategyfactory = StrategyFactory(bar.random)

    for patron in bar.agents:
        m = bar.random.randint(args.basket_min,args.basket_max)
        for _ in range(m):
            patron.strategies.append(strategyfactory.create(args.population,log))
        patron.capacity = args.capacity

    for _ in range(args.iterations):
        bar.step()

    with PlotContext(nrows=2,ncols=1,figs=args.figs,suptitle='El Farol') as axes:
        attendance = bar.datacollector.get_model_vars_dataframe()
        plot1 = sns.lineplot(data=attendance,ax=axes[0],color='blue')
        plot1_2 = sns.lineplot([args.capacity]*args.iterations,ax=axes[0],color='red',label='Capacity')
        plot1_3 = sns.lineplot([np.mean(log)]*args.iterations,
                                   ax=axes[0],
                                   color='green',
                                   linestyle='--',
                                   label=f'Average {np.mean(log):.1f}')
        plot1.set(
            title = 'Weekly attendance',
            xlabel = 'Week',
            ylabel= 'Attendance'
        )
        plot1.legend()

        agent_happiness = bar.datacollector.get_agent_vars_dataframe()
        last_step = agent_happiness.index.get_level_values('Step').max()
        happiness = agent_happiness.xs(last_step, level='Step')['Happiness']
        happiness_median = happiness.median()

        plot2 = sns.histplot(happiness, discrete=True,ax=axes[1],color='blue')
        plot2.axvline(happiness_median,color='r',label=f'Median = {happiness_median}')
        plot2.set(
            title='Overall Happiness',
            xlabel='Happiness',
            ylabel='number of agents',
        );
        plot2.legend()

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
