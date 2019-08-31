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

def freqs(r):
    result={}
    total=0
    for c in r:
        if c.isalpha():
            if c.isupper():
                c=c.lower()
            if c in result:
                result[c]+=1
            else:
                result[c]=1
            total+=1
    return {c:result[c]/total for c in result.keys()}

if __name__=='__main__':
    import requests   
    url = 'https://www.gutenberg.org/files/1342/1342-0.txt'
    r   = requests.get(url)
    ps  = freqs(r.text)
    for l in sorted(ps.keys()):
        print (l,ps[l])