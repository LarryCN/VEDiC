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
url_dic = {}

mgr = manager.manager()

#COUNTNUM = 12000
COUNTNUM = 200
COUNTNUM_L = 10

def blockmanage(docid, parsed_data):
    global mgr
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
    

def parse_index_info(data, info):
    global url_dic, docid
    info = info.split('\n')
    offset = 0
    count = 0
    for i in info:
        count += 1
        page_info = i.split(' ')
        if len(page_info) > 3:
            url = page_info[0]
            size = int(page_info[3])
            page = data[offset:offset + size]
            offset += size
            buf = page + page + "1"
            try:
                #ret = parser.parser(url, page, buf, 2 * len(page) + 1)
                ret = parser.parser(url, page, buf, 2 * len(page) + 1)
                vdata = []
                for i in range(20):           # TODO add version here
                    vdata.append(ret[1])
            except Exception as e:
                continue
            if ret[0] > 0:
                if url not in url_dic:
                    url_dic[url] = docid
                    #termnum = blockmanage(docid, ret[1])
                    termnum = blockmanage(docid, vdata)
                    doc_dic[docid] = [url, termnum]    # url, num of terms TODO version time
                    docid += 1


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
    

def source_file_pasrse_NZ(path):
    global doc_dic
    print("source_file parser NZ", time.ctime())
    #for i in range(82):
    for i in range(1):
        fpath = path + str(i)
        print(fpath)
        
        try:
            findex = gzip.open(fpath + '_index', 'rb')
            info = findex.read()
            findex.close()
            fdata = gzip.open(fpath + '_data', 'rb')
            data = fdata.read()
            fdata.close()
        except Exception as e:
            print(e)
            continue
        try:
            parse_index_info(data, info)
        except Exception as e:
            print('=================')
            print(e)
            continue
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

