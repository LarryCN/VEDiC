# by larry Mar 17th, 2015
import simple9
import config
import hbit_vector

vec = hbit_vector.vec_dic

""" input m, bv1, bv2, bv3, ... ,bvm, n, bv1, bv2, ..., bvn, .... 
    bv is the tmp value of bitvector, we need to convert the bv to huffman code
    
    output bit length array --> like  (m) bv1, bv2, ..., bvm bit lenght of huffman code
           huffman code     -->           ...   the hufffman code data                            
"""
def huffman_code(bv):
    global vec
    lbit = []
    hcode = []
    count = 0
    off = 0
    bicode = 0
    while count < len(bv):
        m = bv[count]
        count += 1
        l = 0
        code = []
        for i in xrange(m):
            tmp = bv[count + i]
            vinfo = vec[tmp]
            bicode = (vinfo[3] << (l + off)) | bicode
            l += vinfo[2]
        count += m
        lbit.append(l)
        off += l
    return lbit, bicode

""" docid compress by increasing diff
    like 51, 59, 69, 80 -> 51, 8, 10, 11
    input docid list
    return transfer list
"""
def docid_compress_by_inc(docid):
    r = [docid[0]]
    for i in xrange(1, len(docid)):
        r.append(docid[i] - docid[i - 1])
    return r
   
""" pos is a list of postions
    here just change the value by inc
"""
def position_compress_by_inc(pos, n):
    for i in reversed(range(1, n)):
        pos[i] = pos[i] - pos[i - 1]
    return pos

""" term ---> inverted index | block | block | block | ...
    block -->  metadata |doc id| freq | pos | ...                           
    list chunk ->  128 doc ids| 128 freqs | 128 docs` positions | ...  

    metadata : metadata size, last doc id, chunk size
                              last doc id, chunk size
                              ...
"""

class iblock:
    def __init__(self):
        self.metadata = ''         
        self.chunkdata = ''        # encode with simple9
        self.size = 0              # final size
        self.off = 0               # metadata size
        self.chunk_num = 0         # chunk num

    """ pack metadata info
    """
    def metadata_pack(self):
        l = self.off + 8 + self.size
        self.off = hex(self.off | (1 << 23))
        """ pack 0 until size to 64KB """
        if l > config.C_BLOCKSIZE:
            print('---------------------- ', l, self.off, self.size)
        for i in xrange(config.C_BLOCKSIZE - l):
            self.chunkdata += ' '

class iindex:
    def __init__(self):
        self.block = [iblock()]       # blocks
        self.n = 1                    # block num

    """ seperate inverted index into docic, bit vector
    """
    def iidex_info_seperate(self, data):
        #self.c = [0]
        docid, bvoff, bv = [], [], []
        boff, off, length = 0, 0, len(data)
        #pos_c = 0
        while off < length:
            docid.append(data[off])    # doc id
            n = data[off + 1]
            bv.append(n)              # freq
            off += 2
            for i in xrange(n):
                bv.append(data[off + i])
            off += n
            bvoff.append(boff + 1 + n)
            boff += (1 + n)
            #pos_c += n
            #self.c.append(pos_c)
        return docid, bvoff, bv

    """ index has stored enough data
        deal with the unpack metadata
    """
    def iindex_done(self):
        block = self.block[self.n - 1]
        block.metadata_pack()

    """ store chunck into block
        update metadata info
    """
    def chunk_store(self, last_docid, chunksize, chunkdata, doc_off, bv_off):
        block = self.block[self.n - 1]
        #if block.size + chunksize >= BLOCKSIZE:
        if block.size + chunksize + block.off + 32 + len(str(last_docid)) + len(str(block.size)) + len(str(doc_off)) + len(str(bv_off))>= config.C_BLOCKSIZE:   # 15 is max of last docid + size + _
            block.metadata_pack()    # block full, pack its metadata
            block = iblock()
            self.block.append(block)
            self.n += 1
        block.chunkdata += chunkdata
        block.size += chunksize
        block.metadata += ' ' + str(last_docid)
        block.metadata += ' ' + str(doc_off)
        block.metadata += ' ' + str(bv_off)
        block.metadata += ' ' + str(block.size)
        block.off = len(block.metadata)
        if not self.info:
            self.info.append(self.n)
            self.info.append(self.block[self.n - 1].chunk_num)
        block.chunk_num += 1

    """ max 128 per chunk; per chunk <= 128
        input docid, bit vector
        return 
    """
    def chunk_pack(self, docid, bvoff, bv):
        off, length = 0, len(docid)
        while off < length:
            if length - off >= config.CHUNKSIZE:
                inc = config.CHUNKSIZE
            else: inc = length - off
            chunksize = config.C_BLOCKSIZE
            while chunksize >= config.C_BLOCKSIZE:
                if inc == 0:
                    print('!!!!!!!!!!!!!!!!!!!!!!', chunksize, docid[off: off + 1], fre[off: off + 1])
                    print(pos[self.c[off]:self.c[off + 1]])
                    print(len(rp), len(rdoc), len(rfre))
                    print(rp)
                    print(rdoc)
                    print(rfre)
                short = docid_compress_by_inc(docid[off: off + inc])           # compress doc id
                rdoc = simple9.simple9_encode(short, len(short))                    # encode with simple9
                rdoc = [hex(x)[2:] for x in rdoc]                                    
                rdoc = str(rdoc)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')

                # TODO add bit vector like bit length array and bit data.
                if not off: s = 0
                else: s = bvoff[off - 1]
                e = bvoff[off + inc - 1]
                data = bv[s: e]  
                lbit, hcode = huffman_code(data)   # lbit is the length of each related huffmancode of docid, hcode is the huffman code of the whole chunk
               
                """ metadata   0xxxxx <-- length   lastdocid, docoff, bvoff, chunkaddr
                    start --- docoff -> docid simple9
                    docff --- bvoff  -> each bit vector huffman code length
                    bvoff --- chunkaddr -> huffman code of the all chunk
                """
                #rlbit = simple9.simple9_encode(data, len(lbit))                    # encode with simple9
                rlbit = simple9.simple9_encode(lbit, len(lbit))                    # encode with simple9
                rlbit = [hex(x)[2:] for x in rlbit]                                    
                rlbit = str(rlbit)[1:-1].replace('\'', '').replace(',', '').replace(' ', '')
                
                rh = hex(hcode)
                rh = rh[2:].replace('L', '')
                rh = rh[::-1]

                r = rdoc + rlbit + rh
                chunksize = len(r)
                if chunksize >= config.C_BLOCKSIZE:
                    inc = inc >> 1
                    print('-----', inc)
            self.chunk_store(docid[off + inc - 1], len(r), r, len(rdoc), len(rlbit))              # chunk store
            off += inc                                                     # updata off

    """ this is the inferface for outside
        input inverted index, then store by chunk-wise compression  [int, int, ...]  int list
        output store position
    """
    def store(self, data):
        docid, bvoff, bv = self.iidex_info_seperate(data)   # seperate docid, bit vector
        self.info = []
        self.chunk_pack(docid, bvoff, bv)                   # chunk pack
        p = self.n
        self.info.append(p)
        self.info.append(self.block[p - 1].chunk_num - 1)
        return self.info   # start_block_num, start_chunk_num, end_block_num, end_chunk_num

