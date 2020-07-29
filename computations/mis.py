
def mis(T):
    unprocessed = []
    score       = {}
    weights     = {}
    children    = {}
    def build_tree(T):
        if len(T)==0:
            return None
        else:
            node            = len(weights)
            weights[node]   = T[0]
            children [node] = []
            unprocessed.append(node)
            for rest in T[1:]:
                nn = build_tree(rest)
                if nn != None:
                    children [node].append(nn)
            return node
    build_tree(T)
 
    while len(unprocessed)>0:
        node = unprocessed.pop()
        if len(children[node])==0:
            score[node]=weights[node]
        else:
            score[node] = max(sum([score[child] for child in children[node]]),
                              weights[node]+sum([score[grandchild] for child in children[node] for grandchild in children[child]]))
    return score[0]
    
print (f'Score for maximal independent set = {mis([3,[4,[1],[2]],[1,[2]],[5,[1],[1]]])}')