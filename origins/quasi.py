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

  I maintain a vector containing the number of instances each bit string.
  Each generation we multiply population of master sequence,
  [0, 0, 0, 0, ...], by f0, and the mutated sequnces by f1, then mutate.
  I assume that the mutation rate is low enough that only one bit is mutated at a time.
 '''

from matplotlib.pyplot import figure,  show
import numpy as np

L              = 12        # Number of bits in genome
N              = 2**L      # Number of possible bit strings
M              = 1000      # Number of instances in Population
K              = 500       # Number of generations
n              = 10        # Number of iterations
f0             = 2         # Fitness of master sequence
f1             = 1         # Fitness of all other sequences
epsilon        = 0.25      # Used to simulate evolution mutation rate just above and below master sequence.


def get_neighbours(n):
    '''
    Get all bitstrings that are one differ from specified bitstring by one bit only.
    We use the convention that 1 is [1,0,0,0,...], 3 [1,1,0,0,0...], and not vice versa
    This function allows us to build a table of possible mutations for a given genome
    once and for all, instead of computing it each time.
    '''

    def mutate_string(i,Bitstring):
        '''Mutate string by flipping one bit'''
        def copy_with_flip(j):
            '''Used to flip the bit that we have chosen to mutate'''
            return 1 - Bitstring[j] if i==j else Bitstring[j]
        return [copy_with_flip(j) for j in range(L)]

    def get_bitstring(n):
        '''Construct bitstring for genome n'''
        Result = []
        for i in range(L):
            n,remainder = divmod(n,2)
            Result.append(remainder)
        return Result

    Bitstring = get_bitstring(n)
    return [mutate_string(i,Bitstring) for i in range(L)]

def bits_to_int(bits):
    '''
    Convert a bitstring to a number
    We use the convention that 1 is [1,0,0,0,...], 3 [1,1,0,0,0...], and not vice versa
    '''
    total = 0
    for i in range(len(bits)):
        total = 2* total + bits[-1-i]
    return total

def select_genomes(C1):
    '''
    Select members of population for next generation, using the known frequencies as probabilities.
    '''
    Z      = sum(C1)            # Partition function
    P      = [c/Z for c in C1]  # C1 normalized to a probability
    Cum    = np.cumsum(P)          # Cumulative probabilities (used for tower sampling)
    Result = np.zeros(N, dtype = np.int64)
    for i in range(M):
        selection = np.searchsorted(Cum,rng.random())  # Make random selection based on probabilities
        Result[selection]+= 1
    return Result

def replicate(C):
    '''
    Make copies of individuals (according to fitness) next generation,
    then reduce so total number matches expected population
    '''
    return select_genomes([C[i] * (f0 if i==0 else f1) for i in range(N)])

def breed(Neighbours,u):
    '''Perform one cycle of evolution. Replicate, and possibly mutate, each instance in population'''
    Counts     = np.zeros(N, dtype = np.int64)  # Number of individuals for each genome - initally just M copies of master sequence
    Counts[0]  = M

    for k in range(K):                        # Iterate over each generation
        # We will accumulate results for next generation in Counts_next
        # Note the number of instances for each possible genome may come from two places:
        # unmutated instances of the same genome, or mutated instances of some other. So
        # we start with zero, and then use '+=' to accumulate counts.
        Counts_next = np.zeros(N)
        for i in range(N):
            number_of_mutations = 0           # book-keeping: used to keep track number of mutated individuals
                                              # so we can subtract from unmutated individuals
            for j in range(int(Counts[i])):
                if rng.random() < u*L:        # Are we going to mutate or not? u is probability for 1 bit
                    bit_to_flip                = rng.integers(0,L)          # Randomly choose which bit to flip
                    mutated_genome             = Neighbours[i][bit_to_flip] # Look mutated genome up from neighbours table
                    genome_index               = bits_to_int(mutated_genome) # Which number corresponds to mutated string?
                    Counts_next[genome_index] += 1
                    number_of_mutations       += 1
            Counts_next[i] += (Counts[i]-number_of_mutations)

        Counts = replicate(Counts_next)
    return Counts

if __name__=='__main__':
    fig = figure(figsize=(12,12))                                # Create a figure to plot into
    rng = np.random.default_rng()                         # Initalize random number generator
    Neighbours = [get_neighbours(n) for n in range(N)] # Build Neighbour table so we can look up mutations
    ErrorThreshold = np.log(f0/f1)/L
    for k,u in enumerate([ErrorThreshold*(1-epsilon),ErrorThreshold*(1+epsilon)]):
        print (f'Mutation rate={u}')
        ax = fig.add_subplot(2,1,k+1)   # Plot each run in a separate region of the figure
        for i in range(n):
            print (f'Iteration {i}')
            Counts = breed(Neighbours,u)
            Z = Counts.sum()                             # Partition function
            ax.plot(range(N), Counts/Z, label=f'{i}')

        ax.legend(title='Iteration')
        ax.set_title(f'Population after {K} generations for u={u:.4f}')
        ax.set_xlabel('Genome')
        ax.set_ylabel('Population')

    fig.tight_layout()
    fig.savefig('quasi')
    show()
