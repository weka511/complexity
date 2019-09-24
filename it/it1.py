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

import math

def get_probability(z):
    counts = {}
    for v in set(z):
        counts[v]=0
    for v in z:
        counts[v]+=1
    total = sum(counts.values())
    return {v:count/total for v,count in counts.items()}
    
def get_entropy(P):
    return sum(- p * math.log(p,2) for p in P.values())

def get_conditional_entropy(P_XY,P_Other,index=0):
    return sum([p_xy*math.log(P_Other[x if index==0 else y]/p_xy,2) for (x,y),p_xy in P_XY.items()])

if __name__=='__main__':
    with open('santafe-temps.csv') as f:
        x_raw      = []
        y_raw      = []
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                continue
            parts = line.strip().split(',')
            x_raw.append(int(parts[2]))
            y_raw.append(float(parts[1]))
            
        x    =  [t>=80 for t in x_raw]
        y    =  [p>0 for p in y_raw]
        xy   =  [(t,p) for t in x for p in y]
        
        P_X  =  get_probability(x)
        P_Y  =  get_probability(y)
        P_XY =  get_probability(xy)
        
        I_X  =  get_entropy(P_X)
        I_Y  =  get_entropy(P_Y)
        I_XY =  get_entropy(P_XY)
        I_Y_X = get_conditional_entropy(P_XY,P_X)
        I_X_Y = get_conditional_entropy(P_XY,P_Y,index=1)        
        print ('I(X)={0:.3f}, I(Y)={1:.3f}, I(XY)={2:.3f}, I(X_Y)= {3:.3f}, I(Y_X)= {4:.3f}'.format(
            I_X, I_Y, I_XY, I_X_Y, I_Y_X))
 
        # Calculate mutual information 3 different ways       
        print (('I(X:Y)= {0:.5f}, {1:.5f}, {2:.5f}').format(I_X-I_X_Y, I_Y-I_Y_X, I_XY-I_X_Y-I_Y_X))
        