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

'''Wealth example from tutorial'''

from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import figure, show
import mesa
import seaborn as sns
import pandas as pd

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    return parser.parse_args()

def get_file_name():
    return join(args.figs,basename(splitext(__file__)[0]))

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
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        # Ensure agent is not giving money to itself
        cellmates.pop(cellmates.index(self))
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

    def step(self):
        self.agents.shuffle_do("move")
        self.agents.do("give_money")


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    model = MoneyModel(100,10,10,seed=args.seed)
    all_wealth = []
    for _ in range(100):
        for _ in range(30):
            model.step()

        for agent in model.agents:
            all_wealth.append(agent.wealth)

    g = sns.histplot(all_wealth, discrete=True)
    g.set(title="Wealth distribution", xlabel="Wealth", ylabel="number of agents");

    # fig.savefig(get_file_name())
    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
