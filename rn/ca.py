# Copyright (C) 2019 Greenweaves Software Limited

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

def create_rule(N):
    n    = N
    rule = []
    while len(rule)<8:
        n,r = divmod(n,2)
        rule.append(r)
    return rule

def execute_rule(state,rule):
    extended_state = [0,0] + state + [0,0]
    new_state      = []
    for i in range(len(state)+2):
        x     = extended_state[i:i+3]
        input = 2*(2*x[0] + x[1]) + x[2]
        new_state.append(rule[input])
    return new_state

def convert(state):
    result = 0
    for i in state:
        result = 2 * result + i
    return result

def project(state,table=[0,1,1,0]):
    return [table[2*state[i]+state[i+1]] for i in range(0,len(state),2)]
        
if __name__=='__main__':
    print (create_rule(105))
    #print (create_rule(110))
    #print (create_rule(137))
    #r = create_rule(28)
    #state = [1]
    #for i in range(25):
        #state = execute_rule(state,r)
        #print (convert(state))