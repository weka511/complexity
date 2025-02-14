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
   El Farol simulation

   Inductive Reasoning and Bounded Rationality, Brian Arthur,

   https://sites.santafe.edu/~wbarthur/Papers/El_Farol.pdf
'''

from argparse import ArgumentParser
from os.path import basename, join, splitext
from time import time

from matplotlib.pyplot import subplots, show
import seaborn as sns

from bar import ElFarol

def parse_arguments():
    '''
    Parse command line arguments and display help text.
    '''
    parser = ArgumentParser(__doc__)
    capacity = 60
    population = 100
    iterations = 52
    review_interval = 5
    tolerance = 25
    basket_min = 5
    basket_max = 12
    n_strategies = 100
    parser.add_argument('--seed',type=int,default=None,help='Seed for random number generator')
    parser.add_argument('--figs', default = './figs',help='Path for storing figures')
    parser.add_argument('--show',default=False,action='store_true',help='Show plots')
    parser.add_argument('--capacity', default=capacity, type=int,help = f'Capacity of venue[{capacity}]')
    parser.add_argument('--population', default=population, type=int,help = f'Number of people available to attend venue [{population}]')
    parser.add_argument('--iterations', default=iterations, type=int, help = f'Number of iterations for running simulation [{iterations}]')
    parser.add_argument('--review_interval', default=review_interval, type=int,
                        help = f'Review strategy every few iterations[{review_interval}]')
    parser.add_argument('--tolerance', default=tolerance, type=float,
                        help = f'Change strategy unless accuracy per step is below this value[{tolerance}]')
    parser.add_argument('--basket_min', default=basket_min, type=int,help = f'Minimum size for basket of strategies[{basket_min}]')
    parser.add_argument('--basket_max', default=basket_max, type=int,help = f'Maximum size for basket of strategies[{basket_max}]')
    parser.add_argument('--n_strategies', default=n_strategies, type=int,help = f'Number of strategies at start [{n_strategies}]')

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

    bar = ElFarol(population = args.population,
                  seed = args.seed,
                  capacity = args.capacity,
                  review_interval = args.review_interval,
                  tolerance = args.tolerance,
                  basket_min = args.basket_min,
                  basket_max = args.basket_max)

    for _ in range(args.iterations):
        bar.step()

    with PlotContext(nrows=2,ncols=2,figs=args.figs,suptitle='El Farol') as axes:
        attendance = bar.datacollector.get_model_vars_dataframe()
        attendance_mean = attendance.mean().item()

        plot1 = sns.lineplot(data=attendance,ax=axes[0][0],color='blue')
        plot1.axhline(args.capacity,color='red',label=f'Capacity={args.capacity}')
        plot1.axhline(attendance_mean,color='green', linestyle='--',label=f'Average={attendance_mean:.1f}')
        plot1.set(
            title = 'Weekly attendance',
            xlabel = 'Week',
            ylabel= 'Attendance'
        )
        plot1.legend()

        agent_vars = bar.datacollector.get_agent_vars_dataframe()
        last_step = agent_vars.index.get_level_values('Step').max()
        happiness = agent_vars.xs(last_step, level='Step')['Happiness']
        happiness_median = happiness.median()

        plot2 = sns.histplot(happiness, discrete=True,ax=axes[0][1],color='blue')
        plot2.axvline(happiness_median,color='r',label=f'Median = {happiness_median}')
        plot2.set(
            title='Overall Happiness',
            xlabel='Happiness',
            ylabel='number of agents',
        );
        plot2.legend()

        sns.color_palette('magma', as_cmap=True)
        plot3 = sns.lineplot(data=agent_vars, x='Step', y='Discrepency', hue='AgentID',ax=axes[1][0])
        plot3.set(
            title = f'Accuracy for each Patron for tolerance {args.tolerance}',
            xlabel = 'Week',
            ylabel= 'Discrepency'
        )

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')

    if args.show:
        show()
