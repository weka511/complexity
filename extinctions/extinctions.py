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
    The Grass/Sheep/Wolves model exhibits behaviour that I did not
    expect: it appeared stable with the default values of parameters, but when
    I increased the speed at which grass regrows slightly, regrowth time=20,
    the model ran for some 1,200,000 generations, the wolves become extinct
    suddenly. It is not clear whether this is a limitation of the simple
    model. The proposed model seeks to establish whether the well known
    link between diversity and stability emerges from simple dynamics.
'''


from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

import numpy as np
from matplotlib.pyplot import subplots, show
# import mesa
import seaborn as sns
import pandas as pd
from ecology import Ecology

def parse_arguments():
	N1 = 100
	N2 = 50
	max_steps = 52
	parser = ArgumentParser(__doc__)
	parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
	parser.add_argument('--figs', default = './figs',help='Path for storing figures')
	parser.add_argument('--show',default=False,action='store_true',help='Show plots')
	parser.add_argument('--N1', default=N1, type=int,help = f'Number of first level consumers [{N1}]')
	parser.add_argument('--N2', default=N2, type=int,help = f'Number of second level consumers[{N2}]')
	parser.add_argument('--max_steps', default=max_steps, type=int, help = f'Number of steps for running simulation [{max_steps}]')
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
	parser = ArgumentParser(__doc__)

	args = parse_arguments()
	ecology = Ecology(N1 = args.N1,
	                  N2 = args.N2,
	                  seed = args.seed)

	for _ in range(args.max_steps):
		ecology.step()

	with PlotContext(figs=args.figs) as axes:
		pass

	elapsed = time() - start
	minutes = int(elapsed/60)
	seconds = elapsed - 60*minutes
	print (f'Elapsed Time {minutes} m {seconds:.2f} s')
	if args.show:
		show()
