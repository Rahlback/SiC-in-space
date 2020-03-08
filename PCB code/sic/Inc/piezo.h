#include <stdbool.h>
#include <stdint.h>
//function prototypes
//void piezo_recive_data(uint8_t *transmitt, uint8_t *recive);
unsigned char piezo_read_data_records(void);
void piezo_stop_exp(void);
void piezo_start_exp(void);
bool piezo_checksum(int *piezoBufferRx);
void ascii_to_int (char * bufferIn, int * bufferOut);
bool record_was_empty(char * bufferIn);
void piezo_get_data(unsigned char *buf, long data_offset);
int piezo_get_data_length(void);
void convert_to_8bit(uint8_t * buffer, uint16_t length);
void clear_piezo_buffer(void);
void RS485(uint8_t);

#define RS_TRANSMIT_ENABLE 0x1
#define RS_TRANSMIT_DISABLE 0x2
#define RS_RECEIVE_ENABLE 0x3
#define RS_RECEIVE_DISABLE 0x4

#define RS_MODE_TRANSMIT 0x5
#define RS_MODE_RECEIVE 0x6
#define RS_MODE_DEACTIVATE 0x7
