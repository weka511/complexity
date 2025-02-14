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

from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
import mesa
import seaborn as sns
import pandas as pd
import bar

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    return parser.parse_args()

# class PlotContext:
    # '''Used to allocate subplots and save figure to file'''
    # PlotContext.Seq = 0
    # def __init__(self, nrows=1,ncols=1,figs='./figs',suptitle=None):
        # Seq += 1
        # self.nrows = nrows
        # self.ncols = ncols
        # self.figs = figs
        # self.suptitle = suptitle

    # def __enter__(self):
        # self.fig, self.ax = subplots(nrows=self.nrows,ncols=self.ncols)
        # if self.suptitle != None:
            # self.fig.suptitle(self.suptitle)
        # return self.ax

    # def __exit__(self, type, value, traceback):
        # self.fig.tight_layout()
        # self.fig.savefig(self.get_file_name())

    # def get_file_name(self):
        # base = basename(splitext(__file__)[0])
        # return join(self.figs, base if PlotContext.Seq == 1 else f'{base}{PlotContext.Seq - 0}')


if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    params = {}

    results = mesa.batch_run(
        bar.ElFarol,
        parameters=params,
        iterations=5,
        max_steps=100,
        number_processes=1,
        data_collection_period=1,
        display_progress=True,
    )
    # with PlotContext(figs=args.figs) as axes:
        # pass

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
    if args.show:
        show()
