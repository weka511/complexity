#!/usr/bin/env python

# Copyright (C) 2019-2023 Simon Crase

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

'''
This program plots the rates at which a genome changes as the results
of mutation, and illustrates the error catastrophe.
'''

from argparse import ArgumentParser
from matplotlib.pyplot import figure, show
import numpy as np

def step(A,s=0.01,nu=0.01):
    '''
    Carry out one breeding step

    Parameters:
           A   Population: A[0} is count of master sequence
                           A[i] is count of sequences with 1 base fiffernt from master, etc.
           s   Advantage of master sequence, which has 1+s copies made, compared to other
               sequences that have 1 copy
           nu  Mutation rate per bit

    Returns: new population following 1 step
    '''
    def grow(i,a):
        return a * (1+s) if i ==0 else a

    L     = len(A) - 1
    A1    = [grow(i,A[i]) for i in range(len(A)) ]
    A2    = (len(A)) * [0]
    for i in range(len(A1)):
        A2[i]     += (1 - L * nu) * A1[i]
        if i>0:
            A2[i-1] += i * nu  * A1[i]
        if i<len(A1)-1:
            A2[i+1] += (L-i) * nu  * A1[i]

    total = sum(A2)
    return [a/total for a in A2]

def evolve(A,s=0.01,nu=0.01, rtol=1e-05, atol=1e-08,N=100):
    '''
    Evolve population

    Paraeters:
           A   Population: A[0} is count of master sequence
                           A[i] is count of sequences with 1 base fiffernt from master, etc.
           s   Advantage of master sequence, which has 1+s copies made, compared to other
               sequences that have 1 copy
           nu  Mutation rate per bit
           rtol
           atol
           N

    Returns: new population following 1 step
    '''
    for i in range(N):
        A1 = step(A,s=s,nu=nu)
        if all(np.isclose(A,A1,rtol=rtol,atol=atol)):
            return A1
        A = [a for a in A1]
    raise Exception('Did not converge within {0} steps, rtol={1},atol={2}'.format(N,rtol,atol))

def parse_arguments():
    parser = ArgumentParser(__doc__)
    parser.add_argument('-L','--Length',default=10,type=int,help='Length of genome in bits')
    parser.add_argument('-n','--nu',default=0.01,type=float,help='Mutation rate per bit')
    parser.add_argument('-s','--advantage',default=[0.8,0.6,0.4, 0.3,0.2,0.1,0.09,0.07,0.0],
                        nargs='+',type=float,help='Advantage for optimal genome')
    parser.add_argument('--N',default=10000,type=int,help='Maximum number of cycles for convergence')
    parser.add_argument('--rtol',default=1e-5,type=float,help='Relative tolerance for convergence')
    parser.add_argument('--atol',default=1e-8,type=float,help='Absolute tolerance for convergence')
    return parser.parse_args()

if __name__=='__main__':
    args = parse_arguments()
    index = 0
    colours = ['r','g','b','y','c','m']
    patterns = ['','/']
    line_styles = ['-','--','-.',':']
    Ss = sorted(args.advantage,reverse=True)
    Populations = [[] for i in range(args.Length+1)]

    fig = figure(figsize=(20,20))
    ax=fig.add_subplot(1,1,1)

    for s in Ss:
        A = evolve([1] + args.Length * [0],s=s,nu=args.nu,N=args.N,rtol=args.rtol,atol=args.atol)
        for i in range(len(Populations)):
            Populations[i].append(A[i])
        x = [i + index/len(Ss) for i in range(len(A))]
        ax.bar(x,A,width=1/len(Ss),color=colours[index%len(colours)],ecolor='face',
                hatch=patterns[index//len(colours)],label='{0:.2f}'.format(s))
        index += 1

    ax.set_title('L={0}, nu={1:.2}'.format(args.Length,args.nu))
    ax.set_xlim(0,len(A))
    ax.set_xlabel('Hamming Distance from optimum')
    ax.set_ylabel('Frequency')
    ax.legend(title='s')
    fig.savefig('figs/ErrorCatastrophe1')

    # Plot dependency on s for each Hamming Distance

    fig = figure(figsize=(20,20))
    ax = fig.add_subplot(1,1,1)
    for i in range(len(Populations)):
        ax.plot(Ss,Populations[i],color=colours[i%len(colours)],
                ls=line_styles[i//len(colours)],label='{0}'.format(i))

    ax.legend(title='Hamming Distance',loc=6)
    ax.set_xlim(min(Ss),max(Ss))
    ax.set_xlabel('s')
    ax.set_ylabel('Frequency')
    ax.set_title('Error catastrophe')
    fig.savefig('figs/ErrorCatastrophe2')

    show()
