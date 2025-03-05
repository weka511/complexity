#!/usr/bin/env python

# Copyright (C) 2019-2025 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

'''
    Q1 Demonstrate the renormalization of Rule 105 to Rule 150.
    What other projections work?
'''

from argparse import ArgumentParser
from time import time

class Rule:
    '''
    Attributes:
        bits A list containing reversed binary expansion of rule
    '''
    def __init__(self,N):
        '''
        Generate a bit string corresponding to the rule number (Wolfram)

        Parameters:
            N    Rule number
        '''
        n = N
        self.bits = []
        while len(self.bits) < 8:
            n,r = divmod(n,2)
            self.bits.append(r)

    def __str__(self):
        return str(self.bits)

    def __getitem__(self, state):
        return self.bits[state.n]

    def two_step(self,superstate): #FIXME
        if len(superstate) != 6: raise ValueError('superstate should have length 6')
        supercell = []
        for i in range(2):
            triplet = []
            for j in range(3):
                k = i + j
                state = State(bits=superstate[k:k+3])
                triplet.append(self[state])
            supercell.append(self[State(bits=triplet)])
        return supercell

class State:
    def __init__(self,n=None,bits=None,N=3):
        '''
        Create a state

        Parameters:
            n
        Returns:
            A list of bits
        '''
        if n != None and bits == None:
            m = n
            result = []
            for i in range(N):
                m,r = divmod(m,2)
                result.append(r)
            self.bits = result[::-1]
            self.n = n
        elif n == None and bits != None:
            self.bits = bits.copy()
            self.n = 0
            for i in self.bits:
                self.n *= 2
                self.n += i
        else:
            raise ValueError('Need either n or bits, but not both')

    def __str__(self):
        return f'n={self.n},bits={self.bits}'

    def __len__(self):
        return len(self.bits)

    def __getitem__(self,key):
        return self.bits[key]

class Projection:
    '''
    Project a state using a function defined by a table.

    Parameters:
        state an array represening pairs of states
        table A four element of a list containing projection of (0,0), (0,1), etnc
    '''
    def __init__(self,table=[0,1,1,0]):
        self.table = table

    def __str__(self):
        return str(self.table)

    def __getitem__(self,key):
        if len(key) % 2 != 0: raise ValueError('key should have even length')
        return [self.table[2*key[i]+key[i+1]] for i in range(0,len(key),2)]

class Matcher:
    def __init__(self):
        def to_binary(n,N=4):
            result = []
            m = n
            for i in range(N):
                m,r = divmod(m,2)
                result.append(r)
            return result[::-1]

        self.Rules = [Rule(i) for i in range(256)]
        self.Projections = []
        for i in range(1,15):
            self.Projections.append(Projection(to_binary(i)))

    def find_matches(self,m):
        matches = []
        for i in range(256):
            if i == m: continue
            match = self.match(m,i)
            if len (match) > 0:
                matches.append((i,match))
        return matches

    def match(self,m,n):
        matches = []
        f = matcher.Rules[m]
        g = matcher.Rules[n]
        for P in matcher.Projections:
            if self.match1(f,g,P):
                matches.append(P)
        return matches

    def match1(self,f,g,P,verbose=False):
        for i in range(2 ** 6):
            state = State(n=i,N=6)
            ss = str(state)
            f1 = f.two_step(state)
            Pf = P[f1][0]
            g1 = State(bits=P[state])
            gp = g[g1]
            if Pf != gp:
                if verbose: print (i, state,Pf,gp, f'mismatch for {P}')
                return False
        return True

def parse_args():
    parser = ArgumentParser(__doc__)
    parser.add_argument('--list', nargs='*', default=[],type=int, help = 'List of rules to be searched for')
    parser.add_argument('--first', default=None,type=int, help = 'First rule to be searched for (only if --list not specified)')
    parser.add_argument('--last',  default=None,type=int, help = 'First rule to be searched for (only if --list not specified)')
    return parser.parse_args()

def sp(n,pl,s):
    '''
    Correctly pluralize text
    '''
    return pl if n>1 else s

def create_worklist(args):
    product = []
    if len(args.list) > 0:
        if args.first != None or args.last != None:
            raise ValueError('If there is a list of rules, there must not be a first rule or a last')
        product = args.list
    else:
        if args.first == None or args.last == None:
            raise ValueError('If there is no list of rules, there must be a first rule and a last')
        product = range(args.first,args.last+1)
    return product

if __name__=='__main__':
    start  = time()
    args = parse_args()
    worklist = create_worklist(args)
    matcher = Matcher()
    with open('matches.txt','w') as matches_file,open('mismatches.txt','w') as mis_matches_file:
        for i in worklist:
            matches = matcher.find_matches(i)
            if len(matches) ==0:
                mis_matches_file.write(f'{i}\n')
            else:
                matches_file.write (f'{i} matches {len(matches)} other {sp(len(matches),'rules','rule')}\n')
                for M in matches:
                    matches_file.write( f'\tRule {M[0]} with the following projections\n')
                    for P in M[1]:
                        matches_file.write(f'\t\t{P}\n')

    elapsed = time() - start
    minutes = int(elapsed/60)
    seconds = elapsed - 60*minutes
    print (f'Elapsed Time {minutes} m {seconds:.2f} s')
