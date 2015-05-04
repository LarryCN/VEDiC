#include "huffman.h"
#include "def.h"

#define BUFF_SIZE  1024 * 1024
struct tnode *huffman_tree;

void stoi_block(char *data, int *buff)
{
    int count = 0;
    int rcount = 0;
    int scount = 0;
    char *s = data;

    while( s[count] != '\n'){
        if(s[count] == ' '){
            buff[rcount] = (int)strtol((s + scount), NULL, 10);
            rcount += 1;
            scount = count + 1;
        }
        count += 1;
    }
    buff[rcount] = (int)strtol((s + scount), NULL, 10);
}

void hfman_init(void)
{
    FILE *fp = NULL;
    int len = 0;
    int i = 0;
    int *pval;
    int t = 0;
    int info[3];  // index, left, right

    struct tnode *p;
    char path[FILEPATH_LEN];
    char *buff = (char *)malloc(sizeof(char) * BUFF_SIZE);
    
    strcpy(path, HUFFMANTREEPATH);
    fp = fopen(path, "rb");
    printf("huffman tree init   \n");

    if(fp == NULL)
        return ;
    /* get len */
    fgets(buff, BUFF_SIZE, fp);
    len = atoi(buff);
    p = (struct tnode *)malloc(sizeof(struct tnode) * len);
    huffman_tree = p;
    pval = (int *)malloc(sizeof(int) * len);
    /* get value array */
    fgets(buff, BUFF_SIZE, fp);
    stoi_block(buff, pval);
    /* node.value, node.left, node.right */
    for(i = 0; i < len; i++){
        fgets(buff, BUFF_SIZE, fp);
        stoi_block(buff, info);
        t = info[0] - 1;
        p[t].v = pval[t];
        if(info[1]){
            p[t].left = &p[info[1] - 1];
        }else{
            p[t].left = NULL;
        }
        if(info[2]){
            p[t].right = &p[info[2] - 1];
        }else{
            p[t].right = NULL;
        }
    }
    fclose(fp);
    free(buff);
    free(pval);
    printf("huffman tree init done \n");
}

inline static void strhex_to_i(char *input, uint *output, int len)
{
    int i;
    int cbyte = 0;
    int tmp = 0;
    char c;
    
    for(i = 0; i < len; i++){
        c = input[i];
        switch(c){
            case '0': c = 0; break;
            case '1': c = 1; break;
            case '2': c = 2; break;
            case '3': c = 3; break;
            case '4': c = 4; break;
            case '5': c = 5; break;
            case '6': c = 6; break;
            case '7': c = 7; break;
            case '8': c = 8; break;
            case '9': c = 9; break;
            case 'a': c = 10; break;
            case 'b': c = 11; break;
            case 'c': c = 12; break;
            case 'd': c = 13; break;
            case 'e': c = 14; break;
            case 'f': c = 15; break;
            default: break;
        }
        tmp |= c << cbyte;
        cbyte += 4;
        if(cbyte == 32){
            cbyte = 0;
            output[i >> 3] = tmp;
            tmp = 0;
        }
    }
    if(cbyte)
        output[i >> 3] = tmp;
}

static uint buff[BUFF_SIZE];

/*
 *  data 
 *  sbit is the start bit
 *  ebit is the end bit
 */
int hfman_decode(int sbit, int ebit, char *data, int *output)
{
    int off = sbit & 3;
    int len = ebit - sbit;
    int num = (len + off) >> 2;   // total char number used
    int bit_count = 0;
    int data_count = 0;
    int buff_count = 0;
    char *s = (data + (sbit >> 2));
    int flag = 0;
    int i;
    struct tnode *p = huffman_tree;

    //printf("hfman decode start bit %d, end bit %d, data addr %x, output addr %x \n", sbit, ebit, (uint)data, (uint)output);
    //printf("off %d, len %d, num %d s addr %x \n", off, len, num, (uint)s);

    if((off + len) & 3){
        num += 1;
    }
    //printf("num %d \n", num);
    
    //printf("%*.*s \n", 0, num, s);
    strhex_to_i(s, buff, num);
    /*
    for(i = 0; i < (num >> 3) + 1; i++){
        printf("%x ", buff[i]);
    }
    printf("\n");
    */
    while(bit_count < len){
        //printf("off %d bit count %d data %d \n", off, bit_count, (buff[buff_count] >> off) & 1);
        if(buff[buff_count] & (1 << off)){   // 1 right 0 left
            p = p->right;
        }else{
            p = p->left;
        }
        if(!p->left && !p->right){          // no children to the leaf decode a data
            output[data_count] = p->v;
            data_count += 1;
            //printf("%d, %d, %d, %d \n", bit_count, buff_count, data_count, p->v);
            p = huffman_tree;
        }
        off += 1;
        bit_count += 1;
        if(off == 32){                     // 32bit.. to next data
            buff_count += 1;
            off = 0;
        }
    }
    return data_count;
}


