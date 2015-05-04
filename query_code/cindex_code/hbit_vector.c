#include "def.h"
#include "hbit_vector.h"
#include "huffman.h"

#define BUFF_SIZE 1024
static int *bv_p;
static int maxkey;

void bv_init(void)
{
    FILE *fp = NULL;
    int len = 0;
    int i = 0;
    int *p = NULL;
    char buff[BUFF_SIZE];
    char path[FILEPATH_LEN];

    strcpy(path, HBITVECTORPATH);
    fp = fopen(path, "rb");
    printf("hbit vector init \n");

    if(fp == NULL)
        return ;
    /* get len */
    fgets(buff, BUFF_SIZE, fp);
    len = atoi(buff);
    p = (int *)malloc(sizeof(int) * len * BIT_M);
    maxkey = len;

    /* get info */ 
    for(i = 0; i < len; i++){
        fgets(buff, BUFF_SIZE, fp);
        stoi_block(buff, p + BIT_M * i);
    }
    fclose(fp);
    bv_p = p;
    printf("done \n");
}

inline static void bv_decode(int key, int *output)
{
    int i = 0;
    int *p = &bv_p[BIT_M * (key - 1)];

    for(i = 0; i < BIT_M; i++){
        output[i] = p[i];
    }
}

static int buff[BUFF_SIZE];

int *get_bv(int len, int *data, int *outlen)
{
    int *p = bv_p;
    int i, j;
    int count = 0;
    int s = 0;
    int datalen = 0;

    bv_decode(data[count], buff);
    count += 1;
    datalen += BIT_M;
    len -= 1;
    while(len){
        for(i = 0; i < BIT_M; i++){
            if(buff[s]){
                bv_decode(data[count], (buff + datalen));
                count += 1;
                datalen += BIT_M;
                len -= 1;
            }else{
                for(j = 0; j <BIT_M; j++){
                    buff[datalen] = 0;
                    datalen += 1;
                }
            }
            s += 1;
        }
    }
    count = 1;
    s = 0;
    while(datalen != count * BIT_M){
        datalen -= count *BIT_M;
        s += count * BIT_M;
        count = count * BIT_M;
    }
    *outlen = datalen;
    return buff + s;
}

