import config

P_INDEX_INDEX_PATH="index/oindex"
P_INDEX_FSIZE_PATH="index/fragsize"
P_INDEX_DVF_PATH="index/dvfmap"
P_INDEX_LEXICON_PATH="index/lexicon"

class PQuerier:

	def __init__(self):
		self.indexf=open(P_INDEX_INDEX_PATH,"r")
		self.fsize=self.loadfsize()
		self.dvf=self.loaddvf()
		self.lexicon=self.loadlexicon()
		
	def getPositions(self,docid,versid,terms):
		lists=self.loadlists(self.indexf,terms,self.lexicon)
		frags=self.dvf[docid][versid]
		poss=self.locate(frags,lists,self.fsize)
		return poss
		
	def loadfsize(self):
		fsizef=open(P_INDEX_FSIZE_PATH,"r")
		records=fsizef.readline()
		fsize=[int(a) for a in records.split()]
		fsizef.close()
		return fsize

	def loaddvf(self):
		dvfmap=[]
		with open(P_INDEX_DVF_PATH) as dvff:
			for line in dvff:
				ele=[int(a) for a in line.split()]
				if len(dvfmap)<=ele[0]:
					for i in xrange(len(dvfmap),ele[0]+1):
						dvfmap.append([])
				dvfmap[ele[0]].append(ele[1:])
		return dvfmap
	
	def loadlexicon(self):
		lexicon={}
		with open(P_INDEX_LEXICON_PATH) as lexiconf:
			for line in lexiconf:
				ele=line.split()
				lexicon[ele[0]]=[int(ele[1]),int(ele[2])]
		return lexicon
	
	def loadlists(self,indexf,terms,lexicon):
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
	
	def locate(self,frags,lists,fsize):
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
	#a testing example: terms=terms,docid=0,vid=0
	pq=PQuerier()
	ide=pq.getPositions(1299,11,['actress','best'])
	print ide
	
