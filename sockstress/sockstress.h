#define PACKETPOOLSIZE 16
#define NBRWORKINGTHREADS 1

#define debug(s) printf("%s:%i %s\n",__FILE__, __LINE__, s)

#define rcd(rc,s) if (rc){printf("%s:%i ",__FILE__,__LINE__);perror(s);exit(EXIT_FAILURE);}
#define rcdmalloc(rc) if (rc==NULL){printf("%s:%i erreur malloc",__FILE__,__LINE__);perror("malloc");exit(EXIT_FAILURE);}

#define ici printf("%s:%i\n",__FILE__,__LINE__)

struct listendata {
  uint32_t destination;
  char *stringdestination;
  char *device;
  int *fin;
  char *request;
  uint16_t port;
};
