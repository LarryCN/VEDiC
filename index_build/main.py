import gzip
import time
import cPickle
import parser
import sys
import manager
import subindex
import config

PENDING = 0
RUNNING = 1
CHECKING = 2

doc_dic = {}
docid = 0

mgr = manager.manager()

#COUNTNUM = 12000
COUNTNUM = 500
COUNTNUM_L = 20

mgrcount = 0

def blockmanage(docid, parsed_data):
    global mgr, mgrcount
    print(mgrcount)
    mgrcount += 1
    if mgr.state == PENDING:
        block = subindex.subindex(mgr.blocknum, config.DATAPATH)
        mgr.blocknum += 1
        mgr.block.append(block)
        mgr.count = 0
        mgr.state = RUNNING
        print("init new index block", mgr.blocknum - 1)
        termnum = block.indexbuild(docid, parsed_data)
    elif mgr.state == RUNNING:
        block = mgr.block[mgr.blocknum - 1]
        mgr.count += 1
        termnum = block.indexbuild(docid, parsed_data)
        if mgr.count >= COUNTNUM:
            mgr.count = 0
            mgr.state = CHECKING
    else:
        block = mgr.block[mgr.blocknum - 1]
        mgr.count += 1
        termnum = block.indexbuild(docid, parsed_data)
        if mgr.count > COUNTNUM_L:
            size =  block.size()
            mgr.count = 0
            if size > mgr.blocksize:
                print('checking state', block.size())
                block.store()
                mgr.state = PENDING
    return termnum
    

def parse_index_info(docid, data):
    vdata = []
    for i in range(len(data)):
        page = data[i]
        page = "<p>" + page + "</p>"
        try:
            buf = page + page + '1'
            ret = parser.parser('', page, buf, 2 * len(page) + 1)
            vdata.append(ret[1])
            if ret[0] <= 0:
                print("------------------------------------")
        except Exception as e:
            print('error')
            print(e)
            while 1:pass
            continue
    return blockmanage(docid, vdata)

def storedata():
    print("store")
    cPickle.dump(lexicon, gzip.open('lexicon', 'wb'))
    cPickle.dump(doc_dic, gzip.open('doc_dic', 'wb'))
    print('---------------------- done store')

import hbit_vector
import huffman_coding
import collections

huffman_tree = None

def huffman_tree_store(root):
    ret = [root.v]                  # bfs    no node write 0
    q = collections.deque()
    q.append(root)
    count = 1
    root.index = count
    count += 1
    while q:
        node = q.popleft()
        if node.left:
            ret.append(node.left.v)
            node.left.index = count
            count += 1
            q.append(node.left)
        if node.right:
            ret.append(node.right.v)
            node.right.index = count
            count += 1
            q.append(node.right)
    s = str(ret[0])
    for i in xrange(1, len(ret)):
        s += ' ' + str(ret[i])
    ls = str(len(ret))

    ret = []
    q.append(root)
    while q:
        node = q.popleft()
        ret.append([node.index])
        if node.left:
            ret[-1].append(node.left.index)
            q.append(node.left)
        else: ret[-1].append(0)
        if node.right:
            ret[-1].append(node.right.index)
            q.append(node.right)
        else: ret[-1].append(0)

    f = open(config.HUFFMANTREEPATH, 'wb')
    f.write(ls + '\n')
    f.write(s + '\n')
    for i in ret:
        s = str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + '\n'
        f.write(s)
    f.close()

def huffman_gen():
    global huffman_tree
    print('generate huffman code for bit vector')
    vec = hbit_vector.vec_dic
    huffman_tree = huffman_coding.encode(vec)
    tv = 0
    bit = 0
    for i in vec:
        info = vec[i]
        tv += info[0]
        bit += info[0] * info[2]
    print('tv', tv, 'bit', bit)
    while 1:pass
    l = []
    maxl = 0
    for i in vec:
        tmp = vec[i][2]
        l.append(tmp)
        if tmp > maxl:
            maxl = tmp
    print(hbit_vector.bv_count, maxl, 'done')   # vec tmpid: [freq, (bit vector), bit length, huffman code(code 0 at bit 0)]
    huffman_tree_store(huffman_tree)
    print('huffman tree write done')
    
import readdata

def source_file_pasrse_NZ(path):
    global doc_dic
    print("wiki data parser", time.ctime())
    df = open(config.WIKIDATAPATH, "rb")
    idxf = open(config.WIKIMAPPATH, "rb")
    ex = readdata.extractor(df, idxf)
    while ex.nextDoc():
        docid = int(ex.docid)
        if docid not in doc_dic:
            doc_dic[docid] = [ex.title]
            vtime = []
            vdata = []
            count = 0
        while ex.nextVers():
            tmp = ex.versdata[0].replace('T', '').replace('Z', '').replace(':', '').replace('-', '')
            tmp = '0x' + tmp
            tmp = int(tmp, 16)
            vtime.append(tmp)
            vdata.append(ex.versdata[1])
        try:
            termnum = parse_index_info(docid, vdata)
            doc_dic[docid].append(termnum)
            doc_dic[docid].append(vtime)
        except Exception as e:
            print("======================")
    print("------- done ", time.ctime())
    """-----------close all the index block---------"""
    block = mgr.block[mgr.blocknum - 1]
    print('checking state', block.size())
    block.store()
    mgr.state = PENDING
    huffman_gen()              # huffman_coding
    hbit_vector.store()        # store bit vector info
    manager.mergesort(mgr)

    manager.structrestore(doc_dic, 'doc_dic')
    mgr.__init__()
    #storedata()
    print("------- done ", time.ctime())

def test():
    source_file_pasrse_NZ(config.SOURCEDATA_PATH)

import cProfile

if __name__ == '__main__':
    print("index ...... larry")
    #source_file_pasrse_NZ(config.SOURCEDATA_PATH)
    cProfile.run('print test()')
    #test()

