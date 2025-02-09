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

'''El Farol simulation'''

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
    parser.add_argument('--capacity', default=70, type=int)
    parser.add_argument('--population', default=100, type=int)
    parser.add_argument('--iterations', default=100, type=int)
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

class Patron(mesa.Agent):
    def __init__(self,model):
        super().__init__(model)

    def decide(self):
        if self.model.strategy.go():
            self.model.attendance += 1

class Strategy:
    def __init__(self,threshold):
        self.threshold = threshold

    def go(self):
        return self.random.random()>self.threshold

class ElFarol(mesa.Model):
    def __init__(self,capacity=70,population=100,seed=None,strategy=None):
        super().__init__(seed=seed)
        self.capacity = capacity
        self.num_agents = population
        Patron.create_agents(model=self, n=population)
        self.log = []
        strategy.random = self.random
        self.strategy = strategy

    def step(self):
        self.attendance = 0
        self.agents.shuffle_do('decide')
        self.log.append(self.attendance)


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    strategy = Strategy(0.75)

    bar = ElFarol(capacity=args.capacity,
                  population=args.population,
                  seed=args.seed,
                  strategy=strategy)

    for _ in range(args.iterations):
        bar.step()

    with PlotContext(figs=args.figs) as axes:
        pass

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
