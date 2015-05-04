import gzip
import sys
import simple9
import config
import hbit_vector

class subindex:
    def __init__(self, blocknum, path):
        self.lexicon = {}
        self.blocknum = blocknum
        self.termid = 0
        self.iindex = {}
        self.path = path
        self.orderlist = []

    def datainfo(self):
        print("term id", self.termid, len(self.lexicon), len(self.iindex))
        for t in self.lexicon:
            print(t, self.lexicon[t])
        for i in self.iindex:
            print(i, self.iindex[i])

    def store(self):
        print("------------store------------")
        f = open(self.path + str(self.blocknum), 'wb')
        l = [s for s in self.lexicon]
        l.sort()
        line = 0
        for t in l:
            tid = self.lexicon[t][0]    # lexicon info
            data = self.iindex[tid]
            data = str(data)[1: -1]
            f.write(data + '\n')        # each line docid, bitvector number, bitv0, bitv1, ....
            self.lexicon[t][0] = line   # line in the inverted index, doc num
            line += 1
        f.close()
        self.orderlist = l
        self.iindex = {}
        print('done')

    def size(self):
        size = 0
        for t in self.iindex:
            size += sys.getsizeof(self.iindex[t])
        return size

    """ build inverted index in this block return term count
    """
    def indexbuild(self, docid, parsed_data):
        vlen = []
        vnum = 0
        vterm = {}  # vterm update tid, v fre, v fre, v fre...   version and frequency
        vl = len(parsed_data)
        print("-----------" , docid, vl)
        for i in xrange(vl):
            v = parsed_data[i].split('\n')
            vlen.append(0) 
            docterm = {}
            for t in v:
                if t:
                    vlen[vnum] += 1
                    s = t.split(' ')
                    s = s[0]         # term
                    if len(s) >= 32 or s == 'nbsp':             # for positon ?
                        continue
                    if s not in docterm:
                        if s not in self.lexicon:
                            self.lexicon[s] = [self.termid, 1]  #for inverted index, doc num
                            tid = self.termid
                            self.termid += 1
                        else:
                            self.lexicon[s][1] += 1
                            tid = self.lexicon[s][0]
                        docterm[s] = 1
                        if tid not in vterm:
                            vterm[tid] = [0] * vl
                            vterm[tid][vnum] = 1
                        else:
                            vterm[tid][vnum] = 1
                    else: 
                        tid = self.lexicon[s][0]
                        vterm[tid][vnum] += 1
            vnum += 1
        # term: docid, bit vector
        for tid in vterm:
            ret = hbit_vector.encode(vterm[tid], config.BIT_M)
            ret.reverse()
            l = len(ret)
            if tid not in self.iindex:
                self.iindex[tid] = [docid, l] + ret
            else:
                self.iindex[tid].append(docid)
                self.iindex[tid].append(l)
                for i in xrange(l):
                    self.iindex[tid].append(ret[i])
        return vlen
