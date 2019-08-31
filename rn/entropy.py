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

pp = {
    'a': 0.0777093, 'b': 0.01694125, 'c': 0.02509587, 'd': 0.0415729,
    'e': 0.1293273, 'f': 0.02237207, 'g': 0.01869932, 'h': 0.063514,
    'i': 0.0705279, 'j': 0.00162383, 'k': 0.00598080, 'l': 0.04025481,
    'm': 0.0275251, 'n': 0.0702613, 'o': 0.0746462, 'p': 0.01533419,
    'q': 0.001168940, 'r': 0.0602125, 's': 0.0617264, 't': 0.0869565,
    'u': 0.02793712, 'v': 0.01067520, 'w': 0.0229406, 'x': 0.001564180,
    'y': 0.02368643, 'z': 0.001745021
}

def coarse_grain(pp,coarsen=lambda l: True):
    keys = list(set([coarsen(k) for k in pp.keys()]))
    result = {k:0 for k in keys}
    for k,p in pp.items():
        result[coarsen(k)]+=p
    return result

def get_entropy(ps):
    def get_entropy_contribution(p):
        return - p * math.log2(p)
    
    return sum([get_entropy_contribution(ps[letter]) for letter in ps.keys()])

def vowel(c):
    return c in ['a','e','i','o','u']

def restrict(ps,selector=lambda l: True):
    subset_keys = [k for k in ps.keys() if selector(k)]
    p_subset = sum(ps[k] for k in subset_keys)
    return {k:ps[k]/p_subset for k in subset_keys}

if __name__=='__main__':
    print (get_entropy(pp))
    print (get_entropy(coarse_grain(pp,coarsen=vowel)))
    #print (get_entropy(restrict(pp,selector=vowel)))
    #print (get_entropy(restrict(pp,selector=lambda l: not vowel(l))))
    