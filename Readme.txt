# VEDiC #
Versioned Document Collections: Build a two-level non-positional(set- and bag-
oriented way) index and a positional(extract common string) index, to support 
versioned documents query like Wiki.


The project mainly has two parts: build index, and query

------------------------------------------------------------------------------
Build index

Data source preprocess Wiki pages(group of versions for the same page): 

docid(1) {version0, version1, version2, ..., verion(m1 - 1)}
docid(2) {version0, version1, version2, ..., verion(m2 - 1)}
docid(3) {version0, version1, version2, ..., verion(m3 - 1)}
   ...                      ...
docid(n) {version0, version1, version2, ..., verion(mn - 1)}
                         |
                         | then parser
                         |
each input one 'group' : docid {term, term, term, ..., term}(version0)
                               {term, term, term, ..., term}(version1)
                                             ...
                               {term, term, term, ..., term}(version(m - 1))}

it is like a docid with a 2D array of terms, term position in the array means 
the positon in the page. We record this each input as src:

for each 
    src --> nonpositional index tmp --> positonal index tmp
    if either tmp size > block size
        store as block
after all src precessed -> merge sort(block) --> nonpositonal index 
                                             |-> positional index

We gonna need several data structures:
lexicon:
term: endchunk|startchunk|fileindex, start_block_addr, end_block_addr, docnum

tmp lexicon: term: blockindex, start_block_addr, end_block_addr

doc_dic:
docid: url, len, [time0, time1, ..., time(m - 1)]  (version related time)


Nonposition
tmp index -> build tmp lexicon
          -> block file context: docid [freq0, freq1, freq2, ..., freq(m - 1)]
          -> hierarchical bit-vector 
          -> count bit-vector frequency 
before mergesort -> Huffman-coding for the bit-vector
then mergsort: for each inverted index, chunk-wise  

Positional 
partition pages -> map((doc, vers) ---> fragments), fragment size table
                -> tmp index
mergesort each inverted index list, chunk-wise compression

Query process:
DAAT-> non-positional index -> top-k` bm25 reuslts
-> extract position information from positional index
-> rerank by bm25tp to get top-k results

------------------------------------------------------------------------------
file struct and code running

Dir index_build has the code to build index:
first config config.py data path
for non-positional index build use: python main.py
for positional index build use: pindexer.py
For one thing to notice is that we use the parsermodule.so from the previous hw.
However as we use seperate version, so, for non-positional use
index_build/parsermodule.so
For positional index, need to use Cparser/parsermodule.so

Dir preprocesss is to deal with raw Wiki data to the data we use.
After config path in the extract.py run: python extract.py

Dir query_code has the code to run query process, just python daat.py
Before running code, need to config config.py
mainly to config data path
And there is cindex_code, which includes the c code of mainly funcitons
To debug could be in the cindex_code to tpye: make  (which depends on Makefile)
To recompile cindexmodule code see readme in the query_code/cindex_code/

About file decription: some of the files are the same as the previous homework
So please reference github/index_and_query/Readme.txt
------------------------------------------------------------------------------
Data
As each wiki dataset is 84GB(too large), and include lots of redirection data,
which is not useful, we need to extract useful data firstly.
Then we use one dataset(each group get most 30 versions), extract 1.4GB data.

Base line: index size 2.1GB

Using our approach: positional index total 144MB
                   
non-positional index 3 temporary files(roughly 67MB), 
as we change bit-vector to a tmp value, roughly total data should be more than 400MB.

doc_dic 1.3 MB 1645 group versions then roughly 48000 pages
average page words number about 4900(about as 15 times as page in hw nz)
lexicon 20 MB roughly 261221 different terms
inverted index 24 MB 

serach mostly keep in 10 ms
data:
https://drive.google.com/a/nyu.edu/folderview?id=0B0XJEhLpK6zYflBmX0daa3pRSFJNa2lwU05XVHlZbWpac284NWtjbWxWa3hQQi1ya3pKMXc&usp=sharing


Aother data set 4.36GB
non-positional index 7 temprorary files(roughly 175MB)
count on bit-vector roughtly at least 1GB
doc_dic 3.5 MB 4555, total roughly 135000 pages
average page words about 5100. 

lexicon 41.5 MB 560929 different terms
inverted index about 64MB 
positional index all data structure 408MB

query time less than 50ms
------------------------------------------------------------------------------
some file description(other could be seen from previous readme)

index_build/hbit_vector.py: This is the file to fulfill hierarchical bit-vector
encode, for each vector we use a tmp value to index, in this way we could shrink
the tmp index file size. 
There is a store function in the file, this is used to store bit vector 
information, when decode get related vector

index_build/huffman_coding.py: This is the file to generate huffman_code depends
on the bit-vector frequency, at the same thime, we get a huffman_coding tree, 
which is used in decode huffman_code.And we add main.py huffman_tree information
by using DFS to access every node, then store into file huffman_tree.

query_code/bm25tp.py: This is the file to computer bm25 term proximity value.
input data format detials written in the bm25tp.py. And just the same formula
from the reference paper.We add the weight of different terms` distance into 
the score.

query_code/cindex_code/ huffman.c huffman.h hbit_vector.h hbit_vector.c
These four files have the function for huffman_coding and hbit_vector get data
structure info from huffman_tree and hbit_vector, as well as init and decode
code.
 
------------------------------------------------------------------------------
How to config
Parameters are mainly in each Dir config.py file. Most are the same as project
index_and_query.(c code in def.h)

Here instroduce some different parameters:
BIT_M  this is used in hierarchical bit vector, as the number of bits to 
       represent one block
TOP_NUM as the Top-k` number
TOP_K   as the final Top-k number

PATH parameters could be known from the name...

