import re
import os

bigbrother=0
curbytes=0

def parse():
	dataPath='predata'
	outfile=open("data","w")
	state=0
	versions=[]
	title=None
	time=None
	content=None
	for root, dirs, files in os.walk(dataPath): 
		for f in files:
			print f
			with open(os.path.join(root,f)) as wikiin:
				for line in wikiin:
					#print state
					#print line
					if state==0 and re.search(r'<page>',line):
						state=1
						versions=[]
						continue
					if state==1 and re.search(r'<title>',line):
						#print line
						p=re.compile(r'<title>(.*)</title>')
						m=p.search(line)
						if m:
							title=m.group(1)
						state=2
						continue
					if state==2 and re.search(r'<redirect',line):
						state=0
						continue
					if state==2 and re.search(r'<revision>',line):
						state=3
						continue
					if state==3 and re.search(r'<timestamp>',line):
						#print line
						state=4
						p=re.compile('<timestamp>(.*)</timestamp>')
						m=p.search(line)
						if m:
							time=m.group(1)
						continue
					if state==4 and re.search(r'<text xml:space="preserve">',line):
						#print line
						state=5
						content=""
						p1=re.compile(r'<text xml:space="preserve">>(.*)</text>')
						p2=re.compile(r'<text xml:space="preserve">>(.*)$')
						m1=p1.search(line)
						m2=p2.search(line)
						if m1:
							content+=m1.group(1)
							state=6
						elif m2:
							content+=m2.group(1)
						continue
					if state==5:
						if re.search(r'</text>',line):
							p=re.compile(r'^(.*)</text>')
							m=p.search(line)
							if m:
								content+=m.group(1)
							state=6
						else:
							content+=line
						continue
					if state==6 and re.search(r'</revision>',line):
						versions.append([title,time,content])
						state=7
						continue
					if state==7 and re.search(r'<revision>',line):
						state=3
						continue
					if state==7 and re.search(r'</page>',line):
						print "ha"
						state=0
						writeversions(versions,outfile)
						continue

def gparse():
	global bigbrother
	global curbytes
	bigbrother=0
	curbytes=0
	outfile=open("/media/Seagate Expansion Drive/wiki/versioned/data","w")
	indexfile=open("/media/Seagate Expansion Drive/wiki/versioned/map","w")
	state=0
	versions=[]
	title=None
	time=None
	content=None
	with open("/media/Seagate Expansion Drive/wiki/versioned/enwiki-20140811-pages-meta-history1.xml-p000000010p000003354") as wikiin:
		for line in wikiin:
			#print state
			#print line
			if state==0 and re.search(r'<page>',line):
				state=1
				versions=[]
				continue
			if state==1 and re.search(r'<title>',line):
				#print line
				p=re.compile(r'<title>(.*)</title>')
				m=p.search(line)
				if m:
					title=m.group(1)
				state=2
				continue
			if state==2 and re.search(r'<redirect',line):
				state=0
				continue
			if state==2 and re.search(r'<revision>',line):
				state=3
				continue
			if state==3 and re.search(r'<timestamp>',line):
				#print line
				state=4
				p=re.compile('<timestamp>(.*)</timestamp>')
				m=p.search(line)
				if m:
					time=m.group(1)
				continue
			if state==4 and re.search(r'<text xml:space="preserve">',line):
				#print line
				state=5
				content=""
				p1=re.compile(r'<text xml:space="preserve">(.*)</text>')
				p2=re.compile(r'<text xml:space="preserve">(.*)$')
				m1=p1.search(line)
				m2=p2.search(line)
				if m1:
					content+=m1.group(1)
					state=6
				elif m2:
					content+=m2.group(1)
				continue
			if state==5:
				if re.search(r'</text>',line):
					p=re.compile(r'^(.*)</text>')
					m=p.search(line)
					if m:
						content+=m.group(1)
					state=6
				else:
					content+=line
				continue
			if state==6 and re.search(r'</revision>',line):
				versions.append([title,time,content])
				state=7
				continue
			if state==7 and re.search(r'<revision>',line):
				state=3
				continue
			if state==7 and re.search(r'</page>',line):
				print "ha"
				state=0
				writeversions(versions,outfile,indexfile)
				continue
						
def writeversions(versions,outfile,indexfile):
	global bigbrother
	global curbytes
	vlen=len(versions)
	if vlen>30:
		versions=versions[-30:]
	title=str(versions[0][0]).replace(' ','_')
	indexfile.write(str(bigbrother)+" "+title+" "+str(len(versions))+" ")
	bigbrother+=1
	for v in versions:
		indexfile.write(str(v[1])+" "+str(curbytes)+" "+str(len(v[2]))+" ")
		curbytes+=len(v[2])
		outfile.write(str(v[2]))
	indexfile.write("\n")

def test():
	path='Drive/wiki/versioned/enwiki-20140811-pages-meta-history1.xml-p000000010p000003354'
	with open(path) as wikiin:
		for line in wikiin:
			if(re.search(r'<title>',line)):
				count+=1
	print count
		
if __name__=='__main__':
	gparse()
