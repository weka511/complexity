'''
Simulate evolution as modelled by the quasi-species equation.
'''
# Copyright (C) 2022 Greenweaves Software Limited

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

# This program simulates evolution for a population of instances of a Genome that can be
# represented as a bitstring. It repeatedly evolves the population to compare the density of
# the master sequence with mutated copies; the evolution is performed for two mutation rates which
# bracket the ErrorThreshold.

from matplotlib.pyplot import figure, legend, plot, savefig, show, subplot, tight_layout, title, xlabel, ylabel
from numpy             import  log,  zeros, sort
from numpy.random      import default_rng
from os.path           import basename, splitext

L              = 1024        # Number of bits in genome
M              = 1000      # Number of instances in Population
K              = 500       # Number of generations
n              = 10        # Number of iterations
f0             = 2         # Fitness of master sequence
f1             = 1         # Fitness of all other sequences
epsilon        = 0.25      # Used to simulate evolution mutation rate just above and below master sequence.

def replicate(Population, NextGeneration):
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
            u = 0.1):
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
            NextGeneration[i,bit_to_flip] = not NextGeneration[i,bit_to_flip]

def select(NextGeneration,m,Population):
    '''
    Used to decide which raplicated and mutated elements will for the population for next period.
    '''
    Selection = rng.choice(m,M,
                           replace = False)
    assert Selection.size == M
    for i,j in enumerate(Selection):
        Population[i,:] = NextGeneration[j,:]

def evolve(Population,NextGeneration,u=0.1):
    '''
    Perform one cycle of evolution: replicate elements in accordance with fitness,
    mutate them, and select data for next cycle.

    '''
    m = replicate(Population, NextGeneration)
    mutate(NextGeneration, m, u=u)
    select(NextGeneration, m, Population)

def get_histogram(Population, density=True):
    '''
    Generate a histogram: counts for each instance that is eactually present
    '''
    Sorted = sort(Population,axis=0)
    cursor = zeros(L,dtype=bool)
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

if __name__=='__main__':
    figure(figsize=(12,12))
    rng            = default_rng(1)
    ErrorThreshold = log(f0/f1)/L
    for i,u in enumerate([ErrorThreshold*(1-epsilon),ErrorThreshold*(1+epsilon)]):
        print (f'Mutation rate={u}')
        subplot(2,1,i+1)                                     # Plot each run in a separate region of the figure
        for j in range(n):
            print (f'Iteration {j}')
            Population     = zeros((M,L),dtype=bool)
            for k in range(K):
                NextGeneration = zeros((f0*M,L), dtype=bool)
                evolve(Population,NextGeneration,u=u)
            plot(get_histogram(Population), label=f'{j}')
        legend(title='Iteration')
        title(f'Population after {K} generations for u={u:.4f}')
        xlabel('Genome')
        ylabel('Population')

    tight_layout()
    savefig(get_plot_file_name())
    show()
