objects = main.o huffman.o hbit_vector.o index_if.o index_op.o term_op.o lru.o hash.o bm25.o simple9.o

edit : $(objects)
	cc -o edit $(objects)

$(objects) : def.h huffman.h hbit_vector.h index_if.h index_op.h term_op.h lru.h hash.h bm25.h simple9.h

.PHONY : clean
clean:
	rm edit $(objects)
