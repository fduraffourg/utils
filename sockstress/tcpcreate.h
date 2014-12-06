#include <dnet.h>

#define TCPSTARTPORT 1024
#define TTL 128

void init_packet_creation(char *dev);
void close_packet_creation(void);
size_t send_packet(char *data, size_t len);
int send_tcp_syn(uint32_t destination, uint16_t dport);
int send_tcp_ack(uint32_t destination, uint16_t id, uint16_t dport,
		 uint16_t sport, uint32_t seq, uint32_t ack);
int send_tcp_win_zero(uint32_t destination, uint16_t id, uint16_t dport,
		      uint16_t sport, uint32_t seq, uint32_t ack);
int send_request(uint32_t destination, uint16_t id, uint16_t dport,
		 uint16_t sport, uint32_t seq, uint32_t ack, char *request);
