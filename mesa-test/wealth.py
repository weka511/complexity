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

'''Wealth example from tutorial https://mesa.readthedocs.io/stable/tutorials/intro_tutorial.html'''

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
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    return parser.parse_args()



class MoneyAgent(mesa.Agent):
    '''An agent with fixed initial wealth.'''

    def __init__(self, model):
        super().__init__(model)
        self.wealth = 1

    def say_hi(self):
        print(f'Hi, I am agent {self.unique_id} and my wealth is {self.wealth}')

    def exchange(self):
        if self.wealth <= 0: return
        other_agent = self.random.choice(self.model.agents)
        if other_agent is not None:
            other_agent.wealth += 1
            self.wealth -= 1

    def move(self):
        self.model.grid.move_agent(self,
                                   self.random.choice(self.model.grid.get_neighborhood(self.pos,
                                                                                       moore = True,
                                                                                       include_center = False)))

    def give_money(self):
        if self.wealth <= 0: return
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(cellmates.index(self)) # Ensure agent is not giving money to itself
        if len(cellmates) > 0:
            other_agent = self.random.choice(cellmates)
            other_agent.wealth += 1
            self.wealth -= 1


class MoneyModel(mesa.Model):
    '''A model with some number of agents.'''

    def __init__(self, n, width=10, height=20, seed=None):
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, True)
        for a, i, j in zip(MoneyAgent.create_agents(model=self, n=n),
                           self.rng.integers(0, self.grid.width, size=(n,)),
                           self.rng.integers(0, self.grid.height, size=(n,))):
            self.grid.place_agent(a, (i, j))
        self.datacollector = mesa.DataCollector(
             model_reporters = {'Gini': self.get_gini},
             agent_reporters = {'Wealth': 'wealth'}
         )

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do('move')
        self.agents.do('give_money')

    def get_gini(self):
        '''Compute Gini index'''
        agent_wealths =sorted([agent.wealth for agent in model.agents])
        n = model.num_agents
        B = sum(xi * (n - i) for i, xi in enumerate(agent_wealths)) / (n * sum(agent_wealths))
        return 1 + (1 / n) - 2 * B

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

if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    model = MoneyModel(100,10,10,seed=args.seed)
    all_wealth = []
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for _ in range(100):
        for _ in range(30):
            model.step()

        for agent in model.agents:
            all_wealth.append(agent.wealth)

        for cell_content, (x, y) in model.grid.coord_iter():
            agent_counts[x][y] += len(cell_content)

    with PlotContext(nrows=2,ncols=2,figs=args.figs) as ax:
        g1 = sns.histplot(all_wealth, discrete=True,ax=ax[0,0])
        g1.set(title='Wealth distribution', xlabel='Wealth', ylabel='number of agents')
        g2 = sns.heatmap(agent_counts, cmap='viridis', annot=False, cbar=True, square=True,ax=ax[0,1])
        g2.set(title='number of agents on each cell of the grid');
        gini = model.datacollector.get_model_vars_dataframe()
        g3 = sns.lineplot(data=gini,ax=ax[1,0])
        g3.set(title='Gini Coefficient over Time', ylabel='Gini Coefficient');
        agent_wealth = model.datacollector.get_agent_vars_dataframe()
        last_step = agent_wealth.index.get_level_values("Step").max()
        end_wealth = agent_wealth.xs(last_step, level="Step")["Wealth"]
        g4 = sns.histplot(end_wealth, discrete=True,ax=ax[1,1])
        g4.set(
            title="Distribution of wealth at the end of simulation",
            xlabel="Wealth",
            ylabel="number of agents",
        );

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
