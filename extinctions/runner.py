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
   Batch runner for Thinking Like a Wolf, a Sheep, or a Firefly
'''

from argparse import ArgumentParser
from os.path import basename, splitext
from time import time
import numpy as np
import pandas as pd
import mesa
from ecology import Ecology

def parse_arguments():
    '''
    Parse command line arguments and display help text.
    '''
    iterations = 5
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
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of times to run simulation [{iterations}]')
    parser.add_argument('--output',default = basename(splitext(__file__)[0]))
    parser.add_argument('--N1', default=N1, type=int,help = f'Initial number of sheep[{N1}]')
    parser.add_argument('--N2', default=N2, type=int,help = f'Initial number of wolves [{N2}]')
    parser.add_argument('--nsteps', default=nsteps, type=int, help = f'Number of steps for running simulation [{nsteps}]')
    parser.add_argument('--freq', default=freq, type=int, help = f'Notify user every [{freq}] steps')
    parser.add_argument('--width', default=width, type=int,help = f'Width of grid [{width}]', nargs = '*')
    parser.add_argument('--height', default=height, type=int,help = f'Height of grid [{height}]', nargs = '*')
    parser.add_argument('--R1', default=R1, type=float,help = f'Probability of a sheep reproducing [{R1}]', nargs = '*')
    parser.add_argument('--R2', default=R2, type=float,help = f'Probability of a wolf reproducing [{R2}]', nargs = '*')
    parser.add_argument('--E0', default=E0, type=float,help = f'Starting energy for a wolf [{E0}]', nargs = '*')
    parser.add_argument('--E1', default=E1, type=float,help = f'Cost of movement for a wolf [{E1}]', nargs = '*')
    parser.add_argument('--E2', default=E2, type=float,help = f'Energy gain for a wolf that eats a sheep [{E2}]', nargs = '*')
    parser.add_argument('--E3', default=E3, type=float,help = f'Energy gain for a sheep that eats a patch of grass [{E3}]', nargs = '*')
    parser.add_argument('--E4', default=E4, type=float,help = f'Cost of movement for a sheep [{E4}]', nargs = '*')
    parser.add_argument('--T1', default=T1, type=float,help = f'Time for grass to regrow [{T1}]', nargs = '*')

    return parser.parse_args()

def get_param(argvalue):
    '''
    Extract the parameters for mesa.batch_run.
    If there is only one value, return it.
    If there are 2 or 3, construct the appropriate range object. Use argvalue[1]+1 for upper limit,
    so range is inclusive.
    '''
    if type(argvalue)==type([]):
        match (len(argvalue)):
            case 1:
                return argvalue
            case 2:
                if all(type(value)==int for value in argvalue):
                    return range(argvalue[0],argvalue[1]+1)
                return np.arange(argvalue[0],argvalue[1]+np.finfo(float).eps)
            case 3:
                if all(type(value)==int for value in argvalue):
                    return range(argvalue[0],argvalue[1]+1,argvalue[2])
                return np.arange(argvalue[0],argvalue[1]+np.finfo(float).eps,argvalue[2])
            case _:
                raise ValueError(f'{argvalue} is too long to use for a range')
    else:
        return argvalue

if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()
    results = mesa.batch_run(
        Ecology,
        parameters = {
            'N1' : get_param(args.N1),
            'N2' : get_param(args.N2),
            'width' : get_param(args.width),
            'height' : get_param(args.height),
            'R1' : get_param(args.R1),
            'R2' : get_param(args.R2),
            'E0' : get_param(args.E0),
            'E1' : get_param(args.E1),
            'E2' : get_param(args.E2),
            'E3' : get_param(args.E3),
            'E4' : get_param(args.E4),
            'T1' : get_param(args.T1)
        },
        iterations = args.iterations,
        max_steps = args.nsteps,
        number_processes = 1,
        data_collection_period = 1,
        display_progress = True,
    )

    results_df = pd.DataFrame(results)
    output_file = args.output if len(splitext(args.output)[1])>0 else f'{args.output}.csv'
    results_df.to_csv(output_file)
    print (f'Saved results to {output_file}')

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
