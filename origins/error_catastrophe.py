def evolve(A,replication=1.0,advantage=10,q=0.2):
    def mutations(i):
        unmutated = (1-q) * A1[i]
        from_lower = 0 if i==0 else A1[i-1]* q * (n-i+1) / n
        from_upper = 0 if i==n else A1[i+1] * q * (i+1) / n
        return from_lower + unmutated + from_upper
    
    def grow(i,a):
        return a * replication * (advantage if i==0 else 1)
    
    n     = len(A) - 1
    A1    = [grow(i,A[i]) for i in range(len(A)) ]
    A2    = [mutations(i) for i in range(len(A1))]
    total = sum(A2)
    return [a/total for a in A2]

if __name__=='__main__':
    A=[1]+20*[0]
    for i in range(100):
        A=evolve(A)
        print (A)