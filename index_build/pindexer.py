import sys
import re
import winnowing
import parser
from readdata import extractor
import subprocess

def process():
	df=open("input/data","r")
	idxf=open("input/map","r")
	indexf=open("index/index","w")
	ex=extractor(df,idxf)
	termlist={}
	fragsize=[]
	fragid=0
	dvfmap=[None for i in xrange(len(ex.index))]
	while ex.nextDoc():
		fragdict={}
		fragmap=[]
		while ex.nextVers():
			content="<p>"+ex.versdata[1]+"</p>"
			buf=content+content+"1"
			tokenss=parser.parser(content,buf,len(buf),len(content))
			tokens = [a.split()[0] for a in str(tokenss[1]).split('\n')[:-1]]
			fragments=winnowing.partition(tokens,50,10)
			versfrag=[]
			for f in fragments:
				fstr=' '.join(f)
				if fstr not in fragdict:
					insertlist(termlist,f,fragid)
					fragdict[fstr]=fragid
					fragsize.append(len(f))
					fragid+=1
				versfrag.append(fragdict[fstr])
			fragmap.append(versfrag)
		dvfmap[ex.docid]=fragmap
		print ex.docid
		if sys.getsizeof(termlist)>0x00400000:
			print "out:"+str(sys.getsizeof(termlist))
			outbuf(termlist,indexf)
			termlist={}
	outdvf(dvfmap)
	outfragsize(fragsize)
	outbuf(termlist,indexf)
	indexf.close()

def insertlist(termlist,frag,fragid):
	pos=0
	for t in frag:
		if t in termlist:
			termlist[t].append([fragid,pos])
		else:
			termlist[t]=[[fragid,pos]]
		pos+=1

def outbuf(termlist,indexf):
	for t,l in termlist.iteritems():
		indexf.write(str(t))
		for f in l:
			indexf.write(" "+str(f[0])+" "+str(f[1]))
		indexf.write("\n")
	
def outdvf(dvfmap):
	dvfmapf=open("index/dvfmap","w")
	docid=-1
	for doc in dvfmap:
		docid+=1
		if not doc:continue
		for vers in doc:
			dvfmapf.write(str(docid))
			for frag in vers:
				dvfmapf.write(" "+str(frag))
			dvfmapf.write("\n")
	dvfmapf.close()
	
def outfragsize(fragsize):
	fsizef=open("index/fragsize","w")
	for f in fragsize:
		fsizef.write(str(f)+" ")
	fsizef.close()

def sort():
	subprocess.call(['sort','-f','-d','-k','1,1','-o','index/indexf','index/index'])

def merge():
	lexiconfile=open("index/lexicon","w")
	indexfile=open("index/oindex","w")
	outBuf=[]
	bufSize=0
	bytec=0
	with open("index/indexf") as index:
		dupList=[]
		prev=None
		for line in index:
			#print sys.getsizeof(self.outBuf)
			record=line.split(' ',1)
			bufSize+=sys.getsizeof(record[1])
			if not record[0].isalnum():
				continue
			if record[0].lower()==prev:
				a=re.split(' ',record[1])
				b=[[int(a[2*i]),int(a[2*i+1])] for i in xrange(len(a)/2)]
				dupList.extend(b)
			else:
				dupList=sorted(dupList, key=lambda a:a[0])
				#print str(dupList)
				#generate the difference of fragID instead the actual DocID
				prevf=0
				#print(dupList)
				tmp=[]
				#if prev:print "******************"+prev+"******************"
				#else:print "********************************************"
				for x in dupList:
					try:
						#print(y[0])
						#print str(x[0]-prevf)+" "+str(x[1])
						tmp.append([x[0]-prevf,x[1]])
						prevf=x[0]
						#print(x.split(' ',1)[0])
						#print("************")
					except:
						x=None
				dupList=tmp
				if prev:
					outBuf.append([prev,dupList])
				prev=record[0].lower()
				dupList=[]
				a=re.split(' ',record[1])
				b=[[int(a[2*i]),int(a[2*i+1])] for i in xrange(len(a)/2)]
				dupList.extend(b)
				if bufSize>52428800: #output buffer once beyond 50MB
					for record in outBuf:
						lexiconfile.write(record[0]+' '+str(bytec)+' ')
						for a in record[1]:
							#print a
							outstr=str(a[0])+" "+str(a[1])+" "
							bytec+=len(outstr)
							indexfile.write(outstr)
						indexfile.write('\n')
						bytec+=len('\n')
						lexiconfile.write(str(bytec)+'\n')
					outBuf=[]
					bufSize=0
	print bufSize
	for record in outBuf:
		lexiconfile.write(record[0]+' '+str(bytec)+' ')
		for a in record[1]:
			outstr=str(a[0])+" "+str(a[1])+" "
			bytec+=len(outstr)
			indexfile.write(outstr)
		indexfile.write('\n')
		bytec+=len('\n')
		lexiconfile.write(str(bytec)+'\n')
	outBuf=[]
	bufSize=0
	lexiconfile.close()
	indexfile.close()

def compare(p):
	try:
		q=int(p.split(' ',1)[0])
	except:
		q=-1
	return q
	
if __name__=='__main__':
	#process()
	merge()
