class extractor:

	def __init__(self,datafile,indexfile):
		self.index=[line.split() for line in indexfile]
		self.idxi=0
		self.versionsidx=0
		self.versnum=0
		self.veri=0
		self.title=None
		self.docid=None
		self.data=datafile
		self.versdata=None
		
	def nextDoc(self):
		if self.idxi>=len(self.index):return None
		self.record=self.index[self.idxi]
		#print self.record
		self.idxi+=1
		self.docid=int(self.record[0])
		self.title=self.record[1]
		self.versnum=int(self.record[2])
		self.veri=0
		self.record=self.record[3:]
		return [self.docid,self.title]
	
	def getDoc(self,idx):
		if idx>=len(self.index):return None
		self.record=self.index[idx]
		self.docid=int(self.record[0])
		self.title=self.record[1]
		self.versnum=int(self.record[2])
		self.veri=0
		self.record=self.record[3:]
		return [self.docid,self.title]
		
	def nextVers(self):
		if self.veri>=self.versnum:return None
		time=self.record[self.veri*3]
		self.data.seek(int(self.record[self.veri*3+1]))
		content=self.data.read(int(self.record[self.veri*3+2]))
		self.veri+=1
		self.versdata=[time,content]
		return [time,content]
		
	def getVers(self,idx):
		if idx>=self.versnum:return None
		time=self.record[idx*3]
		self.data.seek(int(self.record[idx*3+1]))
		content=self.data.read(int(self.record[idx*3+2]))
		return [time,content]
		
if __name__=='__main__':
	df=open("/media/Seagate Expansion Drive/wiki/versioned/data","r")
	idxf=open("/media/Seagate Expansion Drive/wiki/versioned/map","r")
	ex=extractor(df,idxf)
	#get document and versions sequentially
	while ex.nextDoc():
		print ex.docid
		print ex.title
		while ex.nextVers():
			i=1
			#print ex.versdata[0]
			#print ex.versdata[1]
	#get specific document and version
	print "***************"
	doc=ex.getDoc(1)
	print doc
	ver=ex.getVers(5)
	print ver
