#ifndef HUFFMAN_H__
#define HUFFMAN_H__

struct tnode{
    int v;
    struct tnode *left;
    struct tnode *right;
};

extern struct tnode *huffman_tree;
extern void hfman_init(void);
extern void stoi_block(char *data, int *buff);
extern int hfman_decode(int sbit, int ebit, char *data, int *output); 

#endif /* huffman.h */
