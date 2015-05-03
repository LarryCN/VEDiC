import config
import time
import cProfile

class PQuerier:

	def __init__(self):
		self.indexf=open(config.P_INDEX_INDEX_PATH,"r")
		self.fsize=self.loadfsize()
		self.dvf=self.loaddvf()
		self.lexicon=self.loadlexicon()
		
	def getPositions(self,docid,versid,terms):
		lists=self.loadlists(self.indexf,terms,self.lexicon)
		poss=[]
		frags=[]
		fragsdict={}
		#f1=time.time()
		for i in xrange(len(docid)):
			curfrags=self.dvf[docid[i]][versid[i]]
			frags.append(curfrags)
			for f in curfrags:
				fragsdict[f]=i
		poss=self.locate(fragsdict,frags,lists,self.fsize)
		return poss
		
	def loadfsize(self):
		fsizef=open(config.P_INDEX_FSIZE_PATH,"r")
		records=fsizef.readline()
		fsize=[int(a) for a in records.split()]
		fsizef.close()
		return fsize

	def loaddvf(self):
		dvfmap=[]
		with open(config.P_INDEX_DVF_PATH) as dvff:
			for line in dvff:
				ele=[int(a) for a in line.split()]
				if len(dvfmap)<=ele[0]:
					for i in xrange(len(dvfmap),ele[0]+1):
						dvfmap.append([])
				dvfmap[ele[0]].append(ele[1:])
		return dvfmap
	
	def loadlexicon(self):
		lexicon={}
		with open(config.P_INDEX_LEXICON_PATH) as lexiconf:
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
			lists.append(b)
		return lists
	
	def locate(self,fragsdict,frags,lists,fsize):
		valid=True
		poslists=[]
		for i in xrange(len(frags)):
			poslists.append([])
			for j in xrange(len(lists)):
				poslists[i].append({})
		for i in xrange(len(lists)):
			valid=False
			curlist=lists[i]
			prevfid=0
			lis=0
			for j in xrange(len(curlist)/2):
				fid=int(curlist[2*j])+prevfid
				if fid in fragsdict:
					lis+=1
					valid=True
					if fid in poslists[fragsdict[fid]][i]:
						poslists[fragsdict[fid]][i][fid].append(int(curlist[2*j+1]))
					else:	
						poslists[fragsdict[fid]][i][fid]=[int(curlist[2*j+1])]
				prevfid=fid
			if not valid:return False
		outposlists=[]
		for i in xrange(len(frags)):
			outposlists.append([])
			for j in xrange(len(lists)):
				outposlists[i].append([])
		for i in xrange(len(frags)):
			pos=0
			for fid in frags[i]:
				for j in xrange(len(lists)):
					if fid in poslists[i][j]:
						for x in poslists[i][j][fid]:
							outposlists[i][j].append(x+pos)
				pos+=fsize[fid]
		return outposlists
	
if __name__=='__main__':
	#a testing example: terms=terms,docid=0,vid=0
	pq=PQuerier()
	start=time.time()
	ide=pq.getPositions([1632,1519,375,1295],[22,11,29,25],['international','school'])
	end=time.time()
	print ide
	print end-start
	
