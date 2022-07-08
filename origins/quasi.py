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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from matplotlib.pyplot import figure, legend, plot, show
from numpy             import int64, zeros
from numpy.random      import default_rng



M                  = 10        # Number of bits in genome
N                  = 2**M      # Number of possible bit strings
population_size    = 100       # Number of indivuduals in gene pool
K                  = 1000      # NUmber of generations

def get_neighbours(n):
    def copy_with_flip(i,j):
        return 1-Bitstring[j] if i==j else Bitstring[j]
    def mutate_string(i):
        return [copy_with_flip(i,j) for j in range(M)]
    Bitstring = []
    for i in range(M):
        n,remainder = divmod(n,2)
        Bitstring.append(remainder)
    return [mutate_string(i) for i in range(M)]

def bits_to_int(bits):
    total = 0
    for i in range(len(bits)):
        total = 2* total + bits[-1-i]
    return total

if __name__=='__main__':
    figure(figsize=(12,12))
    rng        = default_rng()
    Neighbours = [get_neighbours(n) for n in range(N)]
    for mutation_frequency in [0.0001, 0.001, 0.01, 0.1]:
        Counts     = zeros(N,dtype=int64)
        Counts[0]  = population_size

        for k in range(K):
            Counts_next = zeros(N)
            for i in range(N):
                mutated = 0
                for j in range(int(Counts[i])):
                    if rng.random()<mutation_frequency:
                        bit_to_flip         = rng.integers(0,M)
                        replacement         = Neighbours[i][bit_to_flip]
                        index               = bits_to_int(replacement)
                        Counts_next[index] += 1
                        mutated            += 1
                Counts_next[i] += (Counts[i]-mutated)

            Counts = Counts_next
            assert Counts.sum() == population_size

        plot(Counts, label=f'{mutation_frequency}')

    legend()
    show()
