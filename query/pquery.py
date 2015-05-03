import config
import time

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
			f1=time.time()
			indexf.seek(meta[0])
			a=indexf.read(meta[1])
			b=a.split()
			#print b[:10]
			print "len b:"+str(len(b))
			#tlist=[[b[2*i],b[2*i+1]] for i in xrange(len(b)/2)]
			#for i in xrange(len(b)):
			lists.append(b)
		return lists
	
	def locate(self,fragsdict,frags,lists,fsize):
		valid=True
		poslists=[]
		for i in xrange(len(frags)):
			poslists.append([])
			for j in xrange(len(lists)):
				poslists[i].append([])
		for i in xrange(len(lists)):
			valid=False
			curlist=lists[i]
			prevfid=0
			print curlist[:50]
			for j in xrange(len(curlist)/2):
				fid=int(curlist[2*j])+prevfid
				if fid in fragsdict:
					valid=True
					poslists[fragsdict[fid]][i].append([fid,int(curlist[2*j+1])])
				prevfid=fid
			print valid
			if not valid:return False
		outposlists=[]
		for i in xrange(len(frags)):
			outposlists.append([])
			for j in xrange(len(lists)):
				outposlists[i].append([])
		for i in xrange(len(frags)):
			pos=0
			cursor=[]
			for j in xrange(len(lists)):
				cursor.append(0)
			for fid in frags[i]:
				for j in xrange(len(lists)):
					if cursor[j]<len(poslists[i][j]) and fid==poslists[i][j][cursor[j]][0]:
						outposlists[i][j].append(poslists[i][j][cursor[j]][1]+pos)
						cursor[j]+=1
				pos+=fsize[fid]
		return outposlists
	
if __name__=='__main__':
	#a testing example: terms=terms,docid=0,vid=0
	pq=PQuerier()
	start=time.time()
	ide=pq.getPositions([1299,1320,432],[11,2,21],['actress','best'])
	end=time.time()
	print ide
	print end-start
	
