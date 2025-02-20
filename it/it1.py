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
    Download daily Santa Fe, NM weather data for August 2016 from
    https://figshare.com/s/de109f378939dfc0ed0b(santafe-temps.csv).
    Define X as a random variable that indicates whether it is hot on any given date
    (let X=hot when the MaxTemp for the day is greater than or equal to 80 degrees Fahrenheit and
    X=not-hot otherwise). Define Y as a random variable that indicates whether there is rain on a given date
    (let Y=rain when Precipitation is greater than 0 and Y=no-rain otherwise).
    Compute the following information theoretic quantities:
    I(X), I(Y), I(XY), I(X|Y), I(Y|X), and the mutual information I(X:Y)
'''

import numpy as np

def get_probability(z):
    '''
    Calculate probabilities
        Inputs:
           x    A vector
        Returns:
           A dict whose key is taken from the set of distinct values in x,
           and whose values are the frequency of each key
    '''
    counts = {}
    for v in set(z):
        counts[v] = 0
    for v in z:
        counts[v] += 1
    total = sum(counts.values())
    return {v:count/total for v,count in counts.items()}

def get_entropy(P):
    return sum(- p * np.log2(p) for p in P.values())

def get_conditional_entropy(P_XY,P_Other,index=0):
    return sum([p_xy*np.log2(P_Other[x if index==0 else y]/p_xy) for (x,y),p_xy in P_XY.items()])

def read_data(name='santafe-temps.csv'):
    '''Read temperature data'''
    x_raw = []
    y_raw = []
    with open(name) as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                continue
            parts = line.strip().split(',')
            x_raw.append(int(parts[2]))
            y_raw.append(float(parts[1]))
    return x_raw,y_raw

if __name__=='__main__':
    x_raw,y_raw = read_data()

    x = [t>=80 for t in x_raw]
    y = [p>0 for p in y_raw]
    xy = [(t,p) for t in x for p in y]

    P_X = get_probability(x)
    P_Y = get_probability(y)
    P_XY = get_probability(xy)

    I_X = get_entropy(P_X)
    I_Y = get_entropy(P_Y)
    I_XY = get_entropy(P_XY)
    I_Y_X = get_conditional_entropy(P_XY,P_X)
    I_X_Y = get_conditional_entropy(P_XY,P_Y,index=1)
    print (f'I(X)={I_X:.3f}, I(Y)={I_Y:.3f}, I(XY)={I_XY:.3f}, I(X_Y)= {I_X_Y:.3f}, I(Y_X)= {I_Y_X:.3f}')

    # Calculate mutual information 3 different ways
    print ('I(X:Y)= {I_X-I_X_Y:.5f}, {I_Y-I_Y_X:.5f}, {I_XY-I_X_Y-I_Y_X:.5f}')

    # I(X)=0.981, I(Y)=0.963, I(XY)=1.944, I(X_Y)= 0.981, I(Y_X)= 0.963
    # I(X:Y)= 0.00000, 0.00000, 0.00000

