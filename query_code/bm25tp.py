# bm25 with position info  bm25 term proximity

""" wt = log N/Nt
    acc(Ti) = acc(Ti) + wt * 1 / (dist(Ti + Tj))^2
    acc(Tj) = acc(Tj) + wt * 1 / (dist(Ti + Tj))^2
    
    S = bm25 + sum(min(1, wt)(acc(T)(k1 + 1)) / (acc(T) + K))
   
    k1 = 1.2 K = Ka + Kb * dlen
"""
class BM25TP:
    def __init__(self, d_avg):
        k1 = 1.2
        b = 0.75
        self.Ka = k1 * (1 - b)
        self.Kb = k1 * b / d_avg

    """ info     0      1     2         3                  
        list : [title, dlen, bm25, [[position, w index], ...], ...]
               [title, dlen, bm25, [[position, w index], ...], ...]
        w: [wt, wt]

        len(w) should bigger than 1
    """
    def compute(self, docinfo, w):
        tnum = len(w)
        for doc in docinfo:
            acc = [0] * tnum
            K = self.Ka + self.Kb * doc[1]
            t = doc[3]
            for i in xrange(len(t) - 1):
                if t[i][1] != t[i + 1][1]:
                    ti = t[i][1]
                    tj = t[i + 1][1]
                    v = t[i + 1][0] - t[i][0]
                    v = v * v
                    acc[ti] += w[ti] / v
                    acc[tj] += w[tj] / v
            s = 0
            for i in xrange(tnum):
                s += min(1, w[i]) * 2.2 * acc[i] / (acc[i] + K)
            s += doc[2]
            doc.append(s)
