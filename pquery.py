def loadfsize():
	fsizef=open("index/fragsize","r")
	records=fsizef.readline()
	fsize=[int(a) for a in records.split()]
	fsizef.close()
	return fsize

def loaddvf():
	dvfmap=[]
	with open("index/dvfmap") as dvff:
		for line in dvff:
			ele=[int(a) for a in line.split()]
			if len(dvfmap)<=ele[0]:
				for i in xrange(len(dvfmap),ele[0]+1):
					dvfmap.append([])
			dvfmap[ele[0]].append(ele[1:])
	return dvfmap
	
def loadlexicon():
	lexicon={}
	with open("index/lexicon") as lexiconf:
		for line in lexiconf:
			ele=line.split()
			lexicon[ele[0]]=[int(ele[1]),int(ele[2])]
	return lexicon
	
def loadlists(indexf,terms,lexicon):
	lists=[]
	for t in terms:
		meta=lexicon[t]
		indexf.seek(meta[0])
		a=indexf.read(meta[1])
		b=a.split()
		#print b[:10]
		tlist=[[int(b[2*i]),int(b[2*i+1])] for i in xrange(len(b)/2)]
		lists.append(tlist)
	return lists
	
def locate(frags,lists,fsize):
	valid=True
	locatmap=[]
	for l in lists:
		curmap={}
		for f in frags:	curmap[f]=[]
		locatmap.append(curmap)
	for i in xrange(len(lists)):
		valid=False
		curlist=lists[i]
		curmap=locatmap[i]
		prevfid=0
		print curlist[:50]
		for posting in curlist:
			fid=posting[0]+prevfid
			if fid in curmap:
				valid=True
				curmap[fid].append(posting[1])
			prevfid=fid
		print valid
		if not valid:return False
	poslist=[]
	for i in xrange(len(lists)):
		curposlist=[]
		curmap=locatmap[i]
		pos=0
		for fid in frags:
			for rpos in curmap[fid]:
				curposlist.append(pos+rpos)
			pos+=fsize[fid]
		poslist.append(curposlist)
	return poslist
	
if __name__=='__main__':
	indexf=open("index/oindex","r")
	fsize=loadfsize()
	dvf=loaddvf()
	lexicon=loadlexicon()
	#a testing example: terms=terms,docid=0,vid=0
	terms=["philosophy","government"]
	lists=loadlists(indexf,terms,lexicon)
	frags=dvf[0][0]
	poss=locate(frags,lists,fsize)
	print poss
	
