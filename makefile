#! /usr/bin/env make 

SRC = ./conway/
DEST = ./conway/scripts/

CC = gcc -O
CFLAGS = -I$(SRC) -Wall
		 
.PHONY: all
life: $(SRC)life.c
	$(CC) $(CFLAGS) -o $(DEST)$@ $<

.PHONY: clean
clean:
	rm -f $(DEST)life





