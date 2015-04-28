import heapq

class hfnode:
    def __init__(self, f, v, l, r):
        self.f = f
        self.v = v
        self.left = l
        self.right = r

def pre_t(root):
    if root.left:
        pre_t(root.left)
    if root.right:
        pre_t(root.right)

def bit_cal(code):               # dealing with bit over 64 bits? python is fine
    l = len(code)
    ret = 0
    for i in xrange(l):
        if code[i]:
            ret |= 1 << i
    return ret

"""
using priority queue to get lowest freq node
left 0
right 1
return root

dic key is the value
    dic[key][0] is the freq
"""
def encode(dic):
    heap = []
    for i in dic:
        f = dic[i][0]
        heapq.heappush(heap, [f, i, hfnode(f, i, None, None)])
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        f = left[0] + right[0]
        heapq.heappush(heap, [f, 1, hfnode(f, 1, left[2], right[2])])
    
    root = heap[0][2]
    stack = [[heap[0][2], 0]]
    pre_t(stack[0][0])
    code = []
    while stack:
        node = stack.pop()
        state = node[1]
        node = node[0]
        if state == 0:
            if node.left: 
                code.append(0)
                stack.append([node, 1])
                stack.append([node.left, 0])
            elif node.right:
                code.append(1)
                stack.append([node, 2])
                statck.append([node.right, 0])
            else:
                dic[node.v].append(len(code))
                dic[node.v].append(bit_cal(code))
                code.pop()
        elif state == 1:
            if node.right:
                code.append(1)
                stack.append([node, 2])
                stack.append([node.right, 0])
        else:
            if code: code.pop()
    return root

def decode(root, data):
    result = []
    for i in data:
        j = 0
        node = root
        while j < len(i):
            if i[j]: node = node.right
            else: node = node.left
            j += 1
        result.append(node.v)
    return result
    

