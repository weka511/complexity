from numpy import isclose

def evolve(A,s=0.01,nu=0.01):
    
    def grow(i,a):
        return a * (1+s) if i ==0 else 0
    
    L     = len(A) - 1
    A1    = [grow(i,A[i]) for i in range(len(A)) ]
    A2    = (len(A)) * [0]
    for i in range(len(A1)):
        A2[i]     += (1 - L * nu) * A1[i]
        #n_mutants = (1-q) * A1[i]
        #n_ones    = i
        #n_zeroes  = len(A1) - n_ones
        if i>0:
            A2[i-1] += (L-i) * nu
        if i<len(A1)-1:
            A2[i+1] += i * nu
    
    #assert isclose(sum(A1),sum(A2),rtol=1e-5),'Number should be conserved!'       
    total = sum(A2)
    return [a/total for a in A2]

if __name__=='__main__':
    M = 10
    L = 10
    A = [1] + L * [0]
    print (A)
    for i in range(M):
        A = evolve(A)
        print (A)