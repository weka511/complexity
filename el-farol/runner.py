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
   Batch runner for El Farol simulation

   Inductive Reasoning and Bounded Rationality, Brian Arthur,

   https://sites.santafe.edu/~wbarthur/Papers/El_Farol.pdf
'''

from argparse import ArgumentParser
from os.path import basename, splitext
from time import time

import pandas as pd
import mesa
import bar
from elfarol import add_common_parameters

def parse_arguments():
    iterations = 5
    parser = ArgumentParser(__doc__)
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of times to run simulation [{iterations}]')
    parser.add_argument('--output',default = basename(splitext(__file__)[0]))
    add_common_parameters(parser)
    return parser.parse_args()

if __name__=='__main__':
    start  = time()
    parser = ArgumentParser(__doc__)

    args = parse_arguments()

    results = mesa.batch_run(
        bar.ElFarol,
        parameters = {
            'review_interval' : args.review_interval,
            'capacity'        : args.capacity,
            'population'      : args.population,
            'tolerance'       : args.tolerance,
            'basket_min'      : args.basket_min,
            'basket_max'      : args.basket_max
        },
        iterations = args.iterations,
        max_steps = args.max_steps,
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
