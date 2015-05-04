#include "def.h"
#include "index_if.h"
#include "term_op.h"
#include "index_op.h"

#include <time.h>

/*
 * [19129, 255075, 255081, 255088, 255187, 255827, 292155, 292166]
 * [2, 1, 1, 2, 1, 2, 2, 2]
 */
//static int info1[6] = {30, 170, 170, 22020096, 22151168, 8};  // sunda
static int info1[6] = {199, 81, 81, 16056320, 16121856, 49};  // sunda
static int info2[6] = {153, 60, 28, 13631488, 21168128, 728157}; // out

//static int infotest[6] = {1, 947, 947, 65536, 131072, 60}; //swingset 259242409215393793, 65536, 131072, 60
//static int infotest[6] = {0, 8, 18, 4259840, 4325376, 39183}; // vane
//static int infotest[6] = {0, 1290, 1290, 196608, 262144, 94}; // vane
//static int infotest[6] = {0, 884, 884, 196608, 262144, 72}; // vane
static int infotest[6] = {0, 713, 0, 5636096, 5767168, 5513}; // vane
/*
static int infoi[6] = {16, 323, 28, 2359296, 4849664, 165312}; // i
static int infolike[6] = {18, 158, 68, 21495808, 22413312, 97719}; // like
static int infoyou[6] = {36, 113, 50, 12845056, 15204352, 180501}; // you
*/
static int infoi[6] = {106, 198, 13, 13893632, 32374784, 857159}; // i
static int infolike[6] = {123, 310, 37, 10354688, 15466496, 549439}; // like
static int infoyou[6] = {235, 11, 5, 19595264, 38797312, 1183376}; // you
//                                  c blocksize
static int config_data[8] = {128, 64 * 1024, 10, 64 * 1024, 1, 128 * 1024 * 1024, 1645, 1645};
static int indexsize[1] = {24903680};

static void sub_daat(struct tobj **tlist, int len)
{
    int docid = 0, maxid = config.maxid;
    int dmax = 0, i, dtmp, count = 0;
    int dcount = 0;
    struct tobj *t1 = tlist[0];

    while(docid < maxid){
        docid = nextGEQ(t1, docid);
        printf("----------------------------------docid %d count %d\n ", docid, dcount);
        dcount += 1;
        if(docid >= maxid)
            break;

        dmax = docid;
        for(i = 1; i < len; i++){
            dtmp = nextGEQ(tlist[i], docid);
            if(dtmp > dmax)
                dmax = dtmp;
        }

        if(dmax != docid){
            docid = dmax;
        }else{
            printf("--------------------------------freq %d \n", getFreq(t1, 0));
            docid += 1;
            count += 1;
        }
    }
    printf("---- done  %d \n", count);
}

void test(void)
{
    struct tobj *t[3];
    int docid = 0;
    int freq = 0;
    int i;
    clock_t t1, t2;
    double d_avg = 350.0;

    t1 = clock();
    init_config(config_data, d_avg, indexsize);
    //t = openlist(0, info1);
    t[0] = openlist(infotest);
    printf("------------");
    //t[0] = openlist(info2);
    //t[1] = openlist(infolike);
    //t[2] = openlist(infoyou);
    //if(t[0] == NULL | t[1] == NULL | t[2] == NULL){
      //  printf("tobj NULL\n");
      //  return ;
   // }
    sub_daat(t, 1);
    //sub_daat(t, 3);
    for(i = 0; i < 1; i++)
        closelist(t[i]);
    t2 = clock();
    float diff = (((float)t2 - (float)t1) / 1000000.0F ) * 1000;   
    printf("%f %d \n",diff, sizeof(struct tobj *)); 
}

int main(void)
{
    test();

    return 0;
}
