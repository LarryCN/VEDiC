# Hierarchical Bit-vector

bit_dic = {} 
vec_dic = {}
bv_count = 1   # for each vector assign a number to represent for tmp

def pack(a, n):
    for i in xrange(n):
        a.append(0)

def check_1(a):
    global bit_dic, bv_count, vec_dic
    key = tuple(a)
    if key in bit_dic: 
        rp = bit_dic[key]
        vec_dic[rp][0] += 1
    else: 
        bit_dic[key] = bv_count
        vec_dic[bv_count] = [1, key]
        rp = bv_count
        bv_count += 1
    for i in a:
        if i: 
            return 1, rp
    return 0, 0

"""
    m = 4
       1            0         1         0        ->        1010
   5, 5, 5, 5, 0, 0, 0, 0, 2, 1, 0, 0                      5555 2100
"""
def encode(v, m):
    result = [[]]
    rv = []
    deep = 0
    l = len(v) / m
    for i in xrange(l):
        ret, rp = check_1(v[i * m : i * m + m])
        result[deep].append(ret)
        if rp: rv.append(rp)
    mod = len(v) % m
    if mod: 
        pack(v, m - mod)
        ret, rp = check_1(v[-m:])
        result[deep].append(ret)
        if rp: rv.append(rp)
        l += 1
    while l > m:
        deep += 1
        mod = l % m
        l = l / m
        result.append([])
        for i in xrange(l):
            ret, rp = check_1(result[deep - 1][i * m : i * m + m])
            result[deep].append(ret)
            if rp: rv.append(rp)
        if mod: 
            pack(result[deep - 1], m - mod)   
            ret, rp = check_1(result[deep - 1][-m:])
            result[deep].append(ret)
            if rp: ret.append(rp)
            l += 1
    pack(result[deep], m - l)
    ret, rp = check_1(result[deep])
    if rp: rv.append(rp)
    return rv

import config

def store():
    global vec_dic
    print('bit vector store begin')
    m = config.BIT_M
    f = open(config.HBITVECTORPATH, 'wb')
    f.write((str(len(vec_dic)) + '\n'))
    for i in sorted(vec_dic):
        v = vec_dic[i][1]
        s = str(v[0])
        for j in xrange(1, m):
            s += ' ' + str(v[j])
        f.write(s + '\n')
    f.close()
    print("done")

