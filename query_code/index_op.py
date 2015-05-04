import config
import cPickle

lexicon = {}
doc_dic = {}
maxid = 0
index_size = []

def get_lexicon():
    return cPickle.load(open(config.DATAPATH + config.LEXICON, 'rb'))

def get_doc_dic():
    return cPickle.load(open(config.DATAPATH + config.DOCDIC, 'rb'))

""" term : chunkend| chunkstart| fileindex, start_addr, end_addr, doc_num
                  48-----------32--------0
"""
def term_info_parser(data):
    fileindex = data[0] & 0xffffffff
    chunkstart = (data[0] >> 32) & 0xffff
    chunkend = data[0] >> 48
    return [fileindex, chunkstart, chunkend] + data[1:]

def get_term_info(term):
    global lexicon
    info = lexicon[term]
    return term_info_parser(info)

def get_doc_len(docid):
    global doc_dic
    if docid not in doc_dic:
        print('-------', docid)
    return doc_dic[docid][1]

def get_doc_v_len(docid, v):
    global doc_dic
    if docid not in doc_dic:
        print('-------', docid)
    return doc_dic[docid][1][v]

def get_url(docid):
    global doc_dic
    return doc_dic[docid][0]

def get_title_vtime(docid, v):
    global doc_dic
    info = doc_dic[docid]
    return info[0], info[2][v]

import os
import cindex
import math
import bm25tp

def get_index_size():
    global index_size
    for i in range(config.INDEX_NUM):
        index_size.append(os.path.getsize(config.INVERTEDPATH + str(i)))

tp = None

def get_term_wt(term):
    global lexicon
    return lexicon[term][-1]

def index_init():
    global lexicon, doc_dic, maxid, method_bm25, lru_cache, index_size, tp
    print('index init..............')
    lexicon = get_lexicon()
    doc_dic = get_doc_dic()
    maxid = len(doc_dic)
    t = 0;
    total_version = 0
    for d in doc_dic:
        l = len(doc_dic[d][1])
        for i in xrange(l):
            t += doc_dic[d][1][i]
            total_version += 1;
    d_avg = t * 1.0 / total_version
    info = [config.CHUNKSIZE, config.C_BLOCKSIZE, config.TOP_NUM, config.C_BLOCKSIZE, config.INDEX_NUM, config.CACHE_SIZE, maxid, total_version]
    tp = bm25tp.BM25TP(d_avg)
    print('doc avg ', d_avg)
    for i in lexicon:
        wt = math.log10(total_version * 1.0 / lexicon[i][3])
        lexicon[i].append(wt)
    get_index_size()
    cindex.init(info, d_avg, index_size)
    print('index init done')

