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

from abc import ABCMeta
from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
import mesa
import seaborn as sns
import pandas as pd

def parse_arguments():
    N = 100
    max_steps = 52
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--N', default=N, type=int,help = f'Number of people available to attend venue [{N}]')
    parser.add_argument('--max_steps', default=max_steps, type=int, help = f'Number of steps for running simulation [{max_steps}]')
    return parser.parse_args()

class PrimaryProducer(mesa.Agent):
    def __init__(self,model):
        super().__init__(model)

class Consumer(mesa.Agent):
    def __init__(self,model):
        super().__init__(model)

    def say_hi(self):
        print(f"Hi, I am an agent {type(self)}, you can call me {str(self.unique_id)}.")

class Consumer1(Consumer):
    def __init__(self,model):
        super().__init__(model)

class Consumer2(Consumer):
    def __init__(self,model):
        super().__init__(model)

class Ecology(mesa.Model):
    def __init__(self,
                N = 100,
                width = 25,
                height = 25,
                seed = None):
        super().__init__(seed=seed)
        Consumer1.create_agents(model=self, n=N)
        Consumer2.create_agents(model=self, n=10)
        self.grid = mesa.space.MultiGrid(width, height, True)
        x = self.rng.integers(0, self.grid.width, size=(N+10,))
        y = self.rng.integers(0, self.grid.height, size=(N+10,))
        for a, i, j in zip(self.agents, x, y):
            self.grid.place_agent(a, (i, j))

    def step(self):
        self.agents.shuffle_do("say_hi")

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
    ecology = Ecology(N = args.N,
            seed = args.seed)

    for _ in range(1):#args.max_steps):
        ecology.step()

    with PlotContext(figs=args.figs) as axes:
        pass

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
