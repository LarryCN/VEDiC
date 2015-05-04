#include "term_op.h"
#include "index_op.h"
#include "simple9.h"
#include "huffman.h"
#include "hbit_vector.h"

static uint chunkbuf[128];
int term_num = 0;

static inline void set_chunk_bvoff_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_BVOFF);
}

static inline void set_chunk_access_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_ACCESS);
}

static inline void set_chunk_freq_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_FREQ);
}

static inline void set_chunk_hcode_flag(struct tobj* tobj){
    tobj->flag |= (1 << CHUNK_HCODE);
}

static inline void set_meta_flag(struct tobj* tobj){
    tobj->flag |= (1 << META);
}

static inline void clear_chunk_access_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_ACCESS);
}

static inline void clear_chunk_bvoff_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_BVOFF);
}

static inline void clear_chunk_freq_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_FREQ);
}

static inline void clear_chunk_hcode_flag(struct tobj* tobj){
    tobj->flag &= ~ (1 << CHUNK_HCODE);
}

static inline int is_chunk_access(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_ACCESS);
}

static inline int is_chunk_freq(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_FREQ);
}

static inline int is_chunk_bvoff(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_BVOFF);
}

static inline int is_chunk_hcode(struct tobj* tobj){
    return tobj->flag & (1 << CHUNK_HCODE);
}

static inline int is_meta_flag(struct tobj* tobj){
    return tobj->flag & (1 << META);
}

inline static uint strhex_to_i(char *input, int l)
{
    char c;
    int off = 0;
    uint v;
    uint ret = 0;
    
    while(off < l){
        c = input[off];
        if(c < 'a'){
            v = atoi(&c);
        }else if(c == 'a'){
            v = 10;
        }else if(c == 'b'){
            v = 11;
        }else if(c == 'c'){
            v =12;
        }else if(c == 'd'){
            v = 13;
        }else if(c == 'e'){
            v = 14;
        }else if(c == 'f'){
            v = 15;
        }
        ret += (v << ((l - 1 - off) * 4));
        off += 1;
    }

    return ret;
}

static int update_metadata(int start_addr, struct tobj* tobj)
{
    int metadata_l = 0;
    int metasize = 0;
    int i;

    int* metadata = NULL;
    struct tobj *t = tobj;
    struct meta *meta= &t->meta;
   
    //printf("update metadata %d \n", start_addr); 
    metadata_l = get_metadata_l(t->fileindex, start_addr);
    if(is_meta_flag(t)){
        free(meta->doc_list);
    }
    metadata = (int *)malloc(metadata_l * sizeof(int));
    if(metadata == NULL)
        return 1;
    set_meta_flag(t);


    metasize = get_metasize();
    //printf("metasize %d \n", metasize);
    t->chunk_off = metasize + 8;
    metadata_l = metadata_l >> 2;
    meta->doc_list = metadata;
    meta->doc_off = (metadata + metadata_l);
    meta->bv_off = (metadata + metadata_l * 2);
    meta->chunk_addr = (metadata + metadata_l * 3);
    metadata = get_metadata();
    for(i = 0; i < metadata_l; i++){
        meta->doc_list[i] = metadata[(i << 2)];
        meta->doc_off[i] = metadata[(i << 2) + 1];
        meta->bv_off[i] = metadata[(i << 2) + 2];
        meta->chunk_addr[i] = metadata[(i << 2) + 3];
        //printf("%d, %d, %d, %x \n", meta->doc_list[i], meta->doc_off[i], meta->bv_off[i], meta->chunk_addr[i]);
    }
    if(t->cur_block + 1 < t->block_num){
        t->cur_chunk_e = metadata_l;
    }else{
        t->cur_chunk_e = t->chunk_e + 1;
        if(t->cur_chunk_e > metadata_l)
            t->cur_chunk_e = metadata_l;
    }
    
    return 0;
}

struct tobj* term_init(int* info)
{
    int ret = 0; 
    struct tobj *t = NULL;

    t = (struct tobj*)malloc(sizeof(struct tobj));
    if(t == NULL)
        return t;
    t->tindex = term_num;
    term_num += 1;
    t->fileindex = info[0];
    t->chunk_s = info[1];
    t->chunk_e = info[2];
    t->start_addr = info[3];
    t->end_addr = info[4];
    t->doc_num = info[5];
    t->block_num = (info[4] - info[3])/config.c_blocksize;
    t->c_blocksize = config.c_blocksize;
    t->cur_block = 0;
    t->cur_chunk = t->chunk_s;
    t->cur_meta_l = 0;
    t->flag = 0;
    t->maxid = config.maxid;

    file_open(t->fileindex);
    /* update metadata */
    ret = update_metadata(t->start_addr, t);
    if(ret){
        //printf("update metadata fail \n");
        file_close(t->fileindex);
        return NULL;
    }
    //printf("term init done %d s %d e %d \n", t->tindex, t->chunk_s, t->chunk_e);

    return t;
} 

static void update_chunkdata_doc(int start_addr, int end_addr, struct tobj *tobj)
{
    char *chunkdata = NULL;

    int doclist_l = 0;
    int off = 0;
    int count = 0;
    int len = end_addr - start_addr;
    int i;
    struct tobj *t = tobj;
    int* c_doclist = t->chunk.doclist;
    int seek_addr = t->start_addr + t->cur_block * t->c_blocksize + t->chunk_off;

    //printf("update chunkdata doc  %d, %d \n", start_addr, end_addr);
    //printf("----------------------  %d, %d \n", seek_addr, t->chunk_off);
    t->cur_chunk_bvoff_saddr = seek_addr + end_addr;
    //printf("get chunkdata %d\n", seek_addr + start_addr);
    chunkdata = get_chunkdata(t->fileindex, seek_addr + start_addr, len);
    //printf("get chunkdata done, %d\n", len);
    while(off < len){
        chunkbuf[count] = (uint)strhex_to_i((chunkdata + off), 8);
        count += 1;
        off += 8;
    }
    //printf("---- count %d \n", count);
    len = simple9_decode(chunkbuf, c_doclist, count);
    t->cur_chunk_doc_l = len;
    for(i = 1; i < len; i++){
        c_doclist[i] += c_doclist[i - 1];
        //printf("i = %d --- %d \n", i, c_doclist[i]);
    }
    
    t->cur_doc = 0;
    set_chunk_access_flag(t);
    //clear_chunk_freq_flag(t);
    clear_chunk_bvoff_flag(t);
    clear_chunk_hcode_flag(t);
}

static inline void update_chunkdata_freq(int start_addr, int len, struct tobj *tobj)
{
    int off = 0;
    int count = 0;
    int i = 0;

    struct tobj* t = tobj;
    char *chunkdata = NULL;
    int *c_bvoff = t->chunk.bvoff;

    //printf("update chunkdate_freq %d, %d \n", start_addr, len);
    chunkdata = get_chunkdata(t->fileindex, start_addr, len);
    while(off < len){
        chunkbuf[count] = (uint)strhex_to_i((chunkdata + off), 8);
        count += 1;
        off += 8;
        //printf("%d\n", chunkbuf[count]);
    }
    //printf("---- count %d \n", count);
    len = simple9_decode(chunkbuf, c_bvoff, count);
    for(i = 1; i < len; i++){
        c_bvoff[i] += c_bvoff[i - 1];
    }
    //set_chunk_freq_flag(t);
    set_chunk_bvoff_flag(t);
}

static void init_chunkdata(struct tobj* tobj)
{
    struct meta* meta = &tobj->meta;
    int cur = tobj->cur_chunk;
    int start = 0;

    //printf("init chunkdata\n");
    if(cur == 0){
        start = 0;
    }else{
        start = meta->chunk_addr[cur - 1];
    }
    update_chunkdata_doc(start, start + meta->doc_off[cur], tobj);
}

/*
 * TODO only support for cache
 */
static inline void update_chunk_hcode(struct tobj* tobj)
{
    struct tobj *t = tobj;
    int cur_chunk = t->cur_chunk;
    struct meta *m = &t->meta;
    int start = t->cur_chunk_bvoff_saddr + t->meta.bv_off[cur_chunk];  // huffman code chunk addr

    t->hcode_addr = get_chunkdata(t->fileindex, start, 0);
    set_chunk_hcode_flag(t); 
}

#define HBUFF 256

static int hcode_buff[HBUFF];

static inline int *get_bit_vector(struct tobj* tobj)
{
    struct tobj *t = tobj;
    int s_bit, e_bit;
    int cur = t->cur_doc;
    int len, i;
    int *output;

    //printf("get_bit_vector %d, %d, %d\n", t->cur_chunk, t->chunk_s, t->chunk_e);

    if(!cur){
        s_bit = 0;
    }else{
        s_bit = t->chunk.bvoff[cur - 1];
    }
    e_bit = t->chunk.bvoff[cur];
    //printf("-- %d, %d, %d\n", cur, s_bit, e_bit);
    /* huffman decode */
    len = hfman_decode(s_bit, e_bit, t->hcode_addr, hcode_buff);
    /*
    printf("%d \n", len);
    for(i = 0; i < len; i++){
        printf("%d ", hcode_buff[i]);
    }
    printf("\n");
    */
    /* bit vector decode */
    output = get_bv(len, hcode_buff, &len); // output is the pointer to the bit vector array
    /* 
    printf("%d \n", len);
    for(i = 0; i < len; i++){
        printf("%d ", output[i]);
    }
    printf("\n");
    */
    return output;
}

static inline int get_chunk_docid(int docid, struct tobj* tobj)
{
    struct tobj *t = tobj;
    int i = 0;
    int l = t->cur_chunk_doc_l;
    int* doclist = t->chunk.doclist;
    //printf("get_chunk docid \n");
    
    for(i = t->cur_doc; i < l; i++){
        if(doclist[i] >= docid){
            t->cur_doc = i;
            break;  
        }
    }
    return doclist[i];
}

static int check_meta_docid(int docid, struct tobj* tobj)
{
    int i = 0;
    struct tobj* t = tobj;
    struct meta* meta = &t->meta;
    int *l = t->meta.doc_list;
    int n = t->cur_chunk_e;

    //printf("check meta docid cur chunk %d end %d\n", t->cur_chunk, n);
    for(i = t->cur_chunk; i < n; i++){
        if(l[i] >= docid){
            if(t->cur_chunk == i){
                if(!is_chunk_access(t)){
                    init_chunkdata(t);
                }
            }else{
                update_chunkdata_doc(meta->chunk_addr[i - 1], meta->chunk_addr[i - 1] + meta->doc_off[i], t);
                t->cur_chunk = i;
            }
            return get_chunk_docid(docid, t);
        }
    }
    return t->maxid;
}

int get_docid(int docid, struct tobj* tobj)
{
    struct tobj* t = tobj;
    int block_num = t->block_num;
    int ret = 0;
    int maxid = t->maxid;
    //printf("get docid\n");

    while((t->cur_block + 1)<= block_num){
        ret = check_meta_docid(docid, t);
        if(ret != maxid)
            return ret;
        t->cur_block += 1;
        if(t->cur_block + 1 > block_num)
            break;
        update_metadata(t->start_addr + t->cur_block * t->c_blocksize, t);
        clear_chunk_access_flag(t);
        t->cur_chunk = 0;
    }
    return maxid;
}

static int get_version_freq(struct tobj *tobj, int v)
{
    int *freq = get_bit_vector(tobj);

    return freq[v];
}

int get_freq(struct tobj* tobj, int version)
{
    struct tobj* t = tobj;
    //printf("get freq\n");
    if(!is_chunk_access(t))
        init_chunkdata(t);
    if(!is_chunk_bvoff(t))
        update_chunkdata_freq(t->cur_chunk_bvoff_saddr, t->meta.bv_off[t->cur_chunk], t);
    if(!is_chunk_hcode(t))
        update_chunk_hcode(t);
    return get_version_freq(t, version);
}

void term_close(struct tobj* tobj)
{
    file_close(tobj->fileindex);
    free(tobj->meta.doc_list);
    term_num -= 1;
}



