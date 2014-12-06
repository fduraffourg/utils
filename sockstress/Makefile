CC=gcc
CFLAGS=-g -lpthread -lpcap -ldumbnet


all:
	gcc -Wall -lpthread -lpcap -ldnet -g sockstress.c listen.c tcpcreate.c -o sockstress

static:
	gcc -lpthread -lpcap -ldumbnet sockstress.c listen.c tcpcreate.c /usr/lib/libdumbnet.a /usr/lib/libpcap.a /usr/lib/libpthread.a -static -o ssockstress
