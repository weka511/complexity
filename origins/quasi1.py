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
from numpy             import  bool_, log,  zeros, sort
from numpy.random      import default_rng

L              = 12       # Number of bits in genome
M              = 1000      # Number of instances in Population
K              = 500       # Number of generations
n              = 10        # Number of iterations
f0             = 2         # Fitness of master sequence
f1             = 1         # Fitness of all other sequences
epsilon        = 0.25      # Used to simulate evolution mutation rate just above and below master sequence.

def replicate(Population, NextGeneration):
    m,_ = NextGeneration.shape
    j = 0
    for i in range(M):
        for _ in range(f0 if i==0 else f1):
            NextGeneration[j,:] = Population[i,:]
            j += 1
    assert(j==m)

def mutate(NextGeneration,u=0.1):
    m,_ = NextGeneration.shape
    for i in range(m):
        if rng.random() < u*L:
            bit_to_flip = rng.integers(0,L)
            NextGeneration[i,bit_to_flip] = not NextGeneration[i,bit_to_flip]

def select(NextGeneration,Population):
    m,_     = NextGeneration.shape
    Selection = rng.choice(m,M,replace=False)
    assert Selection.size == M
    for i,j in enumerate(Selection):
        Population[i,:] = NextGeneration[j,:]

def evolve(Population,NextGeneration,u=0.1):
    replicate(Population, NextGeneration)
    mutate(NextGeneration, u=u)
    select(NextGeneration, Population)

def get_histogram(Population):
    S      = sort(Population,axis=0)
    cursor = zeros(L,dtype=bool_)
    bins   = [0]
    for i in range(M):
        if (cursor==S[i,:]).all():
            bins[-1]+=1
        else:
            cursor=S[i,:]
            bins.append(1)
    assert sum(bins)==M
    return bins

if __name__=='__main__':
    figure(figsize=(12,12))
    rng            = default_rng(1)
    Population     = zeros((M,L),dtype=bool_)
    NextGeneration = zeros((f0+f1*(M-1),L), dtype=bool_)
    ErrorThreshold = log(f0/f1)/L
    for k in range(K):
        evolve(Population,NextGeneration,u=1.1*ErrorThreshold)
    bins = get_histogram(Population)
    plot(bins)

    show()
