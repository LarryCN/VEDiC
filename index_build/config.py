SIMPLE9 = 1            # 1 use simple9 encode
CHUNKWISE = 1          # 1 use chunkwise compression, enable chunk wise compression, must also enable simple9
CHUNKSIZE = 128
C_BLOCKSIZE = 64 * 1024 # chunkwise block size
INDEXSIZE = 64 * 1024 * 1024   # inverted index block size
BLOCKSIZE = 64 * 1024 * 1024  # tempory block size  manager use
#INDEXSIZE = 4 * 1024 * 1024   # inverted index block size
#BLOCKSIZE = 10 * 1024 * 1024  # tempory block size  manager use
LEXICON = 'lexicon'
DOCDIC = 'doc_dic'
SOURCEDATA_PATH = '/Users/larry/Code/wsn/index/sourcedata/nz2_merged/'  #nz2 source
INDEXFILELIST = 'indexfile_list.txt'
INVERTEDPATH = '/Users/larry/Code/wsn/index/sourcedata/block/inverted_index_'


#nz 
DATAPATH = "/Users/larry/Code/wsn/index/sourcedata/block/"  # store lexicon doc_dic temporary block

NZ10 = 0   # 1 run nz10 0 run nz2
TMEP_COMPRESS = 0 # 1, temporary block compress with simple9 
TOP_NUM = 20      # query return result


CACHE_BLOCK = C_BLOCKSIZE
CACHE_SIZE = 128 * 1024 * 1024

BIT_M = 6  # bit vector
HUFFMANTREEPATH = '/Users/larry/Code/wsn/index/sourcedata/block/huffman_tree' # store huffman tree  bfs, if no left or right, write 1
HBITVECTORPATH = '/Users/larry/Code/wsn/index/sourcedata/block/hbit_vector' # store hierarchical bit vector info first length, then each line, m value.

WIKIDATAPATH = '/Users/larry/Code/wsn/index/sourcedata/data_v1/data'
WIKIMAPPATH = '/Users/larry/Code/wsn/index/sourcedata/data_v1/map'

