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

def get_entropy(z):
    counts = {}
    for v in set(z):
        counts[v]=0
    for v in z:
        counts[v]+=1
    total = sum(counts.values())
    P = {v:count/total for v,count in counts.items()}
    return sum(- p * math.log(p,2) for p in P.values())

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
        x = [t>=80 for t in x_raw]
        y = [p>0 for p in y_raw]
        print ('I(X)={0:.3f}, I(Y)={1:.3f}'.format(get_entropy(x),get_entropy(y)))
        