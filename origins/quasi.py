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

from matplotlib.pyplot import figure, legend, plot, savefig, show, title, xlabel, ylabel
from numpy             import cumsum, int64, log, searchsorted, zeros
from numpy.random      import default_rng

# Genome is a bit string. We maintain a vector containg the count for each bit string.
# Each generation we multiply population of master sequence,
# [0, 0, 0, 0, ...], by f0, then mutate.
#
# We assume that the mutation rate is low enough that only one bit is mutated at a time.

L              = 10        # Number of bits in genome
N              = 2**L      # Number of possible bit strings
M              = 1000      # Population
K              = 100       # number of generations
f0             = 2         # Fitness of master sequence
f1             = 1         # Fitness of all other sequences
epsilon        = 0.25       # Used to simulate for mutation rate just above and below master sequence.
ErrorThreshold = log(f0)/L

def get_neighbours(n):
    '''
    Get all bitstrings that are one differ from specified bitstring by one bit only.
    We use the convention that 1 is [1,0,0,0,...], 3 [1,1,0,0,0...], and not vice versa
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
    Cum    = cumsum(P)          # Cumulative probabilities (used for tower sampling)
    Result = zeros(N, dtype = int64)
    for i in range(M):
        selection = searchsorted(Cum,rng.random())  # Make random selection based on probabilities
        Result[selection]+= 1
    return Result

def replicate(C):
    '''
    Make copies of indivuduals (according to fitness) next generation,
    then reduce so total number matches expected population
    '''
    return select_genomes([C[i] * (f0 if i==0 else f1) for i in range(N)])

def breed(Neighbours,u):
    Counts     = zeros(N, dtype = int64)  # Number of individuals for each genome - initally just one copy of master sequence
    Counts[0]  = M

    for k in range(K):
        Counts_next = zeros(N)                     # We will accumulate results for next generation here

        for i in range(N):
            number_of_mutations = 0           # book-keeping: used to reduce number of unmutated individuals
            for j in range(int(Counts[i])):
                if rng.random() < u*L:           # Are we going to mutate or not? u is probability for 1 bit
                    bit_to_flip                = rng.integers(0,L)          # Randomly choose which bit to flip
                    mutated_genome             = Neighbours[i][bit_to_flip] # Look mutated genome up from neighbours table
                    genome_index               = bits_to_int(mutated_genome) # Which number corresponds to mutated string?
                    Counts_next[genome_index] += 1
                    number_of_mutations       += 1
            Counts_next[i] += (Counts[i]-number_of_mutations)
        Counts = replicate(Counts_next)
    return Counts

if __name__=='__main__':
    figure(figsize=(12,12))
    rng        = default_rng()
    Neighbours = [get_neighbours(n) for n in range(N)] # Build Neighbour table so we can look up mutations
    for u in [ErrorThreshold*(1-epsilon),
              ErrorThreshold*(1+epsilon)]:
        Counts = breed(Neighbours,u)
        Z = Counts.sum()                             # Partition function
        plot(range(N), Counts/Z, label=f'{u:.04f}')

    legend(title='Mutation Rate')
    title(f'Population after {K} generations')
    xlabel('Genome')
    ylabel('Population')
    savefig('quasi')
    show()
