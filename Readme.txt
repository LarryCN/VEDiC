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

About file decription: some of the files are the same as the previous homework
So please reference github/index_and_query/Readme.txt

