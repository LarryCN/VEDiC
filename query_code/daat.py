import index_op
import time
import config
import heapq
import bm25tp

from index_if import openlist as openlist
from index_op import get_doc_v_len as get_doc_v_len
from index_op import get_term_wt as get_term_wt

info = 0

import pquery

pq = None

def init():
    global info, pq
    info = index_op
    info.index_init()
    print("positional index init")
    pq = pquery.PQuerier()
    print("positional index done")

import cindex

def cdaat(terms, date):
    terms = terms.split(' ')
    """open list"""
    #mtime = time.time()
    tobj = []
    try:
        for t in terms:
            tobj.append([index_op.lexicon[t][3], t])
        tobj.sort()  # sort by doc_nums include term
    except Exception as e:
        print(e)
        print('there is some terms not in the index, so no result')
        return []

    """ DAAT """
    tlist = []
    for t in tobj:
        tlist.append(openlist(t[1]))
    #print('############### DAAT ##################')
    ret = cindex.subdaat(tlist, info.doc_dic, date)
    #print('--- ', ret)
    rdocid = [ret[x * 3] for x in xrange(len(ret) / 3)]
    result = []
    count = 0
    for i in xrange(len(rdocid)):
        docid = rdocid[i]
        title, vtime = index_op.get_title_vtime(docid, ret[i * 3 + 1])
        # title, dlen, bm25, [[postion, wt num], ...], v, vtime, docid
        result.append([title, get_doc_v_len(docid, ret[i * 3 + 1]), ret[i * 3 + 2], [], ret[i * 3 + 1], vtime, docid]) 
        count += 1
        if count >= config.TOP_NUM:
            break
    result.sort()
    result.reverse()
    #print(ret[-1], time.time() - mtime)
    return result, ret[-1]


def lexicon_test():
    l = info.lexicon
    """
    for t in sorted(l):
        print(t)
        if t == 'warzones':
            print("------------------------ ")
    """ 
    date = '2014-06-15T01:01:01Z'
    for t in sorted(l):
        mtime = time.time()
        r , count = cdaat(t, date)
        c = l[t][3]
        print(t, c, count, time.time() - mtime)
        if c!= count:
            print('----------------------------------->')
    
    print('done')

def query():
    global pq
    q = raw_input("Please enter here(return to query): ")
    date = raw_input("Please enter date here(like 20140615, other or wrong use 20150503 not deal with wrong date):")
    date.rstrip()
    if len(date) != 10 or not date.isdigital():
        date = '20150503'
    date = '0x' + date + '235555'
    doc_dic = index_op.doc_dic
    try:
        s = "query " + q
        print(s, date)
        print("")
        term = q.rstrip()
        mtime = time.time()
        r ,count = cdaat(term, int(date, 16))
        mtime = time.time() - mtime

        term = term.split(' ')
        print("bm25 results: ")
        r = sorted(r, key = lambda x:x[2])  
        r.reverse()
        docid_dic = {}
        for i in r:
            docid_dic[i[6]] = 1
            s = i[0] + ' bm25: ' + str(i[2]) + ' v: ' + str(i[4]) + ' ' + hex(i[5])[2:] + ' docid ' + str(i[6])
            print(s)
        term = list(term)
        if len(term) > 1:
            doc = []
            v = []
            for info in r:
                doc.append(info[-1])
                v.append(info[4])
            ptime = time.time()
            ret = pq.getPositions(doc, v, term)
            ptime = time.time() - ptime

            nterm = len(term)
            for i in xrange(len(r)):
                info = r[i]
                for j in ret[i]:
                    info[3] += j
                info[3].sort()
            w = []
            for i in xrange(nterm):
                w.append(get_term_wt(term[i]))
            index_op.tp.compute(r, w)
            r = sorted(r, key = lambda x:x[-1]) 
            r.reverse()
            print("")
            print("bm25 term proximity results: ")
            docid_dic = {}
            cc = 0
            for i in r:
                if cc >= config.TOP_K:
                    break
                cc += 1
                docid_dic[i[6]] = 1
                s = i[0] + ' bm25tp: ' + str(i[-1]) + ' v: ' + str(i[4]) + ' ' + hex(i[5])[2:] + ' docid: ' + str(i[6])
                print(s) 
            
            print("")
            s = "Non-positional time cost: " + str(mtime) + 's' + " Positional time cost: " + str(ptime) + "s   total " + str(count) + ' query results'
            print(s)
            print("")
                
        else:
            print("")
            print("Only one word so do not need to extract positon")
            s = "Non-positional time cost: " + str(mtime) + 's' + " total " + str(count) + ' query results'
            print(s)
            print("")


        q = raw_input("If want to see the version change please enter the docid you see(only above results, wrong docid or other will skip this step): ")
        term = q.rstrip()
        docid = int(term)
        if docid in docid_dic:
            title = doc_dic[docid][0]
            dtime = doc_dic[docid][2]
            size = doc_dic[docid][1]
            diff = [0]
            for i in xrange(len(size) - 1):
                diff.append(size[i + 1] - size[i])
            print(" ")
            print(title + ' version changes:')
            for i in reversed(xrange(len(size))):
                if diff[i] > 0:
                    s = 'version:' + str(i) + ' words count:' + str(size[i]) + ' change words: +' + str(diff[i]) + " " + hex(dtime[i])[2:]
                else:
                    s = 'version:' + str(i) + ' words count:' + str(size[i]) + ' change words: ' + str(diff[i]) + " " + hex(dtime[i])[2:]
                print(s)
            print(" ")
    except Exception as e:
        print(e)
        print("please reenter correctly")

import cProfile
if __name__ == '__main__':
    print('Versioned Document Collections------')
    mtime = time.time()
    init()
    print("init done", time.time() - mtime)
    print("")
    print("")
    while 1:
        query()
    #lexicon_test()
