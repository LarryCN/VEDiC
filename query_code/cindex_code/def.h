#ifndef DEF_H__
#define DEF_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned long ulong;
typedef unsigned int uint;

#define FETCHSIZE 2 * 1024 * 1024
#define CHUNKSIZE 128
#define INDEX_NUM   238
#define FILEPATH_LEN  256
#define FILEPATH "/Users/larry/Code/wsn/index/sourcedata/block/inverted_index_"


#define HUFFMANTREEPATH "/Users/larry/Code/wsn/index/sourcedata/block/huffman_tree"  
#define HBITVECTORPATH "/Users/larry/Code/wsn/index/sourcedata/block/hbit_vector"  

#define BIT_M  6

#endif /* def.h */
