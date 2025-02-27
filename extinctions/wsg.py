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

from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time
from matplotlib.pyplot import subplots, show
import seaborn as sns
import pandas as pd
from ecology import Ecology

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
    E0 = 5
    E3 = 1
    E4 = 5
    T1 = 15
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default='./figs',help='Path for storing figures')
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
    parser.add_argument('--E3', default=E3, type=float,help = f'Energy gain for a sheep that eats a patch of grass [{E3}]')
    parser.add_argument('--E4', default=E4, type=float,help = f'Cost of movement for a sheep [{E4}]')
    parser.add_argument('--T1', default=T1, type=float,help = f'Time for grass to regrow [{T1}]')
    return parser.parse_args()

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
        if not ecology.is_active:
            print (f'Break after step {k}')
            break

    with PlotContext(figs=args.figs,suptitle='Sheep and Wolves') as axes:
        model_vars = ecology.datacollector.get_model_vars_dataframe()
        agent_vars = ecology.datacollector.get_agent_vars_dataframe()
        sheep = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['S'].to_numpy()
        wolves = agent_vars.groupby('Step')['role'].value_counts().unstack(fill_value=0)['W'].to_numpy()
        grass = model_vars.grass.to_numpy()
        scale = max(sheep.max(),wolves.max())/grass.max()

        plot1 = sns.lineplot(data=sheep,ax=axes,color='blue',label=f'Sheep N={args.N1},R={args.R1},E3={args.E3},E4={args.E4}')
        sns.lineplot(data=wolves,ax=axes,color='red',label=f'Wolves N={args.N2},R={args.R2},E0={args.E0},E1={args.E1},E2={args.E2}')

        sns.lineplot(data=scale*grass,ax=axes,color='green',label=f'Grass: T1={args.T1} (Scaled to match Sheep & Wolves)')
        plot1.legend()
        plot1.set(title=f'Population: grid = {args.width}x{args.height};',
                                      xlabel = 'Time',
                                      ylabel = 'Population')

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
