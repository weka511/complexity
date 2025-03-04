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

'''Q1 renormalization of 105 to 150'''

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

    def two_step(self,superstate):
        if len(superstate) != 6: raise ValueError('superstate should have length 6')
        supercell_bits = []
        for i in range(2):
            triplet = []
            for j in range(3):
                k = 3*i + j
                state = State(bits=superstate[k:k+3])
                triplet.append(self[state])
            supercell_bits.append(self[State(bits=triplet)])
            z=0
    # def execute(self,state):
        # extended_state = [0,0] + state.bits + [0,0]
        # new_state = []
        # for i in range(len(state)+2):
            # x = extended_state[i:i+3]
            # new_state.append(self.bits[4*x[0] + 2*x[1] + x[2]])
        # return new_state

class State:
    def __init__(self,n=None,bits=None):
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
            for i in range(3):
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
        return str(self.bits)

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

    def __getitem__(self,key):
        if len(key) % 2 != 0: raise ValueError('key should have even length')
        return [self.table[2*key[i]+key[i+1]] for i in range(0,len(key),2)]

### old code ###
def convert(state):
    result = 0
    for i in state:
        result = 2 * result + i
    return result



if __name__=='__main__':
    r105 = Rule(105)
    print (r105)
    for i in range(8):
        state = State(n=i)
        print (state,  r105[state])
    P = Projection()
    print(P[0,0,0,1,1,0,1,1])
    r105.two_step([0,1,1,0,0,1])

