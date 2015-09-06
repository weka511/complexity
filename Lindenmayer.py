import turtle

class Lindenmayer:
    def __init__(self,rule,start,rendering):
        self.rule=rule
        self.start=start
        self.rendering=rendering
        self.dist=1
        self.string=start
    def subst(self,char):
        return self.rule[char] if char in self.rule.keys() else char        
    def step(self):
        self.string= ''.join([self.subst(x) for x in self.string])    
    def propagate(self):
        for i in range(6):
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
           
if __name__=='__main__':
    lindenmayer=Koch()
    lindenmayer.propagate()
    lindenmayer.render()

    