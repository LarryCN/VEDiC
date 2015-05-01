import parser
import sys

def partition(tokens,t,k):
	w=t-k+1
	kgrams=[]
	gramn=len(tokens)-k+1
	for i in xrange(gramn):
		tmp=""
		for j in xrange(k):
			tmp+=tokens[i+j]
		kgrams.append(tmp)
	hashs=[hash(g) for g in kgrams]
	minh=0
	minidx=0
	record=[0 for i in xrange(gramn)]
	fingerprint=[]
	windown=gramn-w+1
	for i in xrange(windown):
		minh=sys.maxint
		for j in xrange(w):
			if hashs[i+j]<=minh:
				minh=hashs[i+j]
				minidx=i+j
		if record[minidx]==0:
			fingerprint.append(minh)
			record[minidx]=1
	previ=0
	fragments=[]
	for i in xrange(1,gramn):
		if record[i]==1:
			fragments.append(tokens[previ:i])
			previ=i
	fragments.append(tokens[previ:])
	return fragments
