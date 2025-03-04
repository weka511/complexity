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

    def execute(self,state):
        extended_state = [0,0] + state.bits + [0,0]
        new_state = []
        for i in range(len(state)+2):
            x = extended_state[i:i+3]
            new_state.append(self.bits[4*x[0] + 2*x[1] + x[2]])
        return new_state

class State:
    def __init__(self,n):
        '''
        Create a state

        Parameters:
            n
        Returns:
            A list of bits
        '''
        m = n
        result = []
        for i in range(3):
            m,r = divmod(m,2)
            result.append(r)
        self.bits = result[::-1]
        self.n = n

    def __str__(self):
        return str(self.bits)

    def __len__(self):
        return len(self.bits)

def convert(state):
    result = 0
    for i in state:
        result = 2 * result + i
    return result

def project(state,table=[0,1,1,0]):
    '''
    Project a state using a function defined by a table.

    Parameters:
        state an array represening pairs of states
        table A four element of a list containing projection of (0,0), (0,1), etnc
    '''
    return [table[2*state[i]+state[i+1]] for i in range(0,len(state),2)]

if __name__=='__main__':
    r105 = Rule(105)
    print (r105)
    for i in range(8):
        state = State(i)
        print (state,  r105[state], r105.execute(state))



    # print(execute_rule([0,0,0],r105))
    #print (create_rule(110))
    #print (create_rule(137))
    # r = create_rule(28)
    # state = [1]
    # for i in range(25):
        # state = execute_rule(state,r)
        # print (convert(state))
