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
   Batch runner template
'''

from argparse import ArgumentParser
from os.path import basename, splitext
from time import time
import numpy as np
import pandas as pd
import mesa


def parse_arguments():
    '''
    Parse command line arguments and display help text.
    '''
    iterations = 5
    nsteps = 50

    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of times to run simulation [{iterations}]')
    parser.add_argument('--output',default = basename(splitext(__file__)[0]))
    parser.add_argument('--nsteps', default=nsteps, type=int, help = f'Number of steps for running simulation [{nsteps}]')


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
        Model,    #FIXME
        parameters = {

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
