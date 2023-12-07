#!/usr/bin/env python

# Copyright (C) 2022-2023 Simon Crase

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# ILPLIED, INCLUDING BUT NOT LILITED TO THE WARRANTIES OF LERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGELENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIL, DALAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROL,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



'''
Simulate evolution as modelled by the quasi-species equation.

 This program simulates evolution for a population of instances of a Genome that can be
 represented as a bitstring. It repeatedly evolves the population to compare the density of
 the master sequence with mutated copies; the evolution is performed for two mutation rates which
 bracket the ErrorThreshold.

'''

from argparse          import ArgumentParser
from matplotlib.pyplot import figure, legend, plot, savefig, show, subplot, tight_layout, title, xlabel, ylabel
from matplotlib        import __version__ as plt_version
from numpy             import iinfo, int64, log,  zeros, sort
from numpy             import __version__ as np_version
from numpy.random      import default_rng
from os.path           import basename, splitext
from platform          import platform
from sys               import version

def parse_arguments():
    '''
    Read command line arguments so they can be accessed by the program
    '''
    parser = ArgumentParser(description = __doc__)
    parser.add_argument('--L', type=int, default=1024, help='Number of bits in genome')
    parser.add_argument('--M', type=int, default=1000, help='Number of instances in Population')
    parser.add_argument('--K', type=int, default=2000, help='Number of generations')
    parser.add_argument('--n', type=int, default=10, help='Number of iterations')
    parser.add_argument('--seed', type=int, help='For rnamdom number generator')
    parser.add_argument('--fitness', type=float, nargs=2, default=[2,1], help='Fitness of master sequence, all other sequences')
    parser.add_argument('--scale', type=float, nargs='+', default=[0.9,1.1], help='Usedcompare mutation rates')

    parser.add_argument('--show',
                        action = 'store_true',
                        help   = 'Show plot')
    parser.add_argument('--plot',
                        default = None,
                        help    = 'Name of plot file')

    parser.add_argument('--version',
                        default = False,
                        action = 'store_true',
                        help   = 'Display version numbers and exit')
    args = parser.parse_args()
    if args.version:
        print (f'Python {version}')
        print (f'{platform()}')
        print (f'Numerical python version {np_version}')
        print (f'Matplotlib version {plt_version}')
        exit()
    return args

def replicate(Population, NextGeneration,M,f0,f1):
    '''
    Create a new population from the old one. Each instance of the genome is copied one or more times,
    depending on its fitness.

    Parameters:
           Population
           NextGeneration

    Returns:
         Number of elements in next generation
    '''
    j = 0
    for i in range(M):
        fitness = f1 if any(Population[i,:]) else f0
        for _ in range(fitness):
            NextGeneration[j,:] = Population[i,:]
            j += 1
    return j

def mutate(NextGeneration,m,
            u = 0.1,
            L = 1):
    '''
    Mutate elements in population
    Parameters:
        NextGeneration
        m
        u
    '''
    for i in range(m):
        if rng.random() < u*L:
            bit_to_flip = rng.integers(0,L)
            NextGeneration[i,bit_to_flip] = 1 - NextGeneration[i,bit_to_flip]

def select(NextGeneration,m,Population,M=1):
    '''
    Used to decide which raplicated and mutated elements will for the population for next period.
    '''
    Selection = rng.choice(m,M,
                           replace = False)
    assert Selection.size == M
    for i,j in enumerate(Selection):
        Population[i,:] = NextGeneration[j,:]

def evolve(Population,NextGeneration,u=0.1,M=1,f0=1,f1=1,L=1):
    '''
    Perform one cycle of evolution: replicate elements in accordance with fitness,
    mutate them, and select data for next cycle.

    '''
    m = replicate(Population, NextGeneration,M=M, f0=f0,f1=f1)
    mutate(NextGeneration, m, u=u,L=L)
    select(NextGeneration, m, Population,M=M)

def get_histogram(Population, density=True):
    '''
    Generate a histogram: counts for each instance that is eactually present
    '''
    M,L    = Population.shape
    Sorted = sort(Population,axis=0)
    cursor = zeros(L,dtype=int)
    bins   = [0]
    for i in range(M):
        if (cursor==Sorted[i,:]).all():
            bins[-1]+=1
        else:
            cursor = Sorted[i,:]
            bins.append(1)
    assert sum(bins)==M
    if density:
        Z = sum(bins)
        return [count/Z for count in bins]
    else:
        return bins

def get_plot_file_name(plot=None):
    '''Determine plot file name from source file name or command line arguments'''
    if plot==None:
        return f'{splitext(basename(__file__))[0]}.png'
    base,ext = splitext(plot)
    return f'{plot}.png' if len(ext)==0 else plot

def get_seed(seed):
    '''Choose seed for random number generator'''
    if seed == None:
        rng      = default_rng()
        new_seed = rng.integers(iinfo(int64).max)
        print (f'Seed={new_seed}')
        return new_seed
    else:
        return seed

if __name__=='__main__':
    figure(figsize=(12,12))
    args           = parse_arguments()
    rng            = default_rng(get_seed(args.seed))
    ErrorThreshold = log(args.fitness[0]/args.fitness[1])/args.L
    for i,scale in enumerate(args.scale):
        u = scale*ErrorThreshold
        print (f'Mutation rate={u}')
        subplot(len(args.scale),1,i+1)                                     # Plot each run in a separate region of the figure
        for j in range(args.n):
            print (f'Iteration {j}')
            Population     = zeros((args.M,args.L),
                                   dtype = int)
            for k in range(args.K):
                NextGeneration = zeros((args.fitness[0]*args.M,args.L),
                                       dtype = int)
                evolve(Population,NextGeneration,
                       u  = u,
                       M  = args.M,
                       f0 = args.fitness[0],
                       f1 = args.fitness[1],
                       L  = args.L)
            plot(get_histogram(Population),
                 label = f'{j}')
        legend(title='Iteration')
        title(f'Population after {args.K} generations for u={u:.4f}, L={args.L}')
        xlabel('Genome')
        ylabel('Population')

    tight_layout()
    savefig(get_plot_file_name())
    show()
