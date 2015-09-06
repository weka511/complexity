# Lindenmayer.py

# Copyright (C) 2015 Greenweaves Software Pty Ltd

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

import turtle

class Lindenmayer:
    def __init__(self,rule,start,rendering):
        self.rule=rule
        self.start=start
        self.rendering=rendering
        self.dist=1
        self.string=start
        self.states=[]
    def subst(self,char):
        return self.rule[char] if char in self.rule.keys() else char        
    def step(self):
        self.string= ''.join([self.subst(x) for x in self.string])    
    def propagate(self):
        for i in range(10):
            self.step()
            print (self.string)  
    def render(self):
        turtle.up()
        w=turtle.window_width()
        self.dist=w/len(self.string)
        turtle.back(w/2)
        turtle.shape("turtle")
        for c in self.string:
            self.draw(c)
        turtle.exitonclick()        
    def draw(self,c):
        for f in self.rendering[c]:
            f()
    def push(self):
        self.states.append((turtle.heading(),turtle.position()))
    def pop(self):
        heading,position=self.states.pop()
        turtle.setheading(heading)
        turtle.setposition(position)        
        
class Cantor(Lindenmayer):
    def __init__(self):
        super().__init__(
            {
                'a':'aba',
                'b':'bbb'
                },
            'a',
            {
                'a':[lambda:turtle.down(),lambda:turtle.forward(self.dist)],
                'b':[lambda:turtle.up(),lambda:turtle.forward(self.dist)]
            }
        )
        
class Koch(Lindenmayer):
    def __init__(self):
        super().__init__(
            {'f':'f+f-f-f+f'},
            'f',
            {
                'f':[lambda:turtle.down(),lambda:turtle.forward(5)],
                '+':[lambda:turtle.left(90)],
                '-':[lambda:turtle.right(90)]
            }
        )

class Pythagorus(Lindenmayer):
    def __init__(self):
        super().__init__(
            {
                '1':'11',
                '0':'1[0]0'
                },
            '0',
        {'0':[lambda:turtle.down(),lambda:turtle.forward(1)],
         '1':[lambda:turtle.down(),lambda:turtle.forward(1)],
         '[':[lambda:self.push(),lambda:turtle.left(45)],
         ']':[lambda:self.pop(),lambda:turtle.right(45)]
         })
    

        
if __name__=='__main__':
    lindenmayer=Pythagorus()
    lindenmayer.propagate()
    lindenmayer.render()

    