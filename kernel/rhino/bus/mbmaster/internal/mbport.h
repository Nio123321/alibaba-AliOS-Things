#ifndef _MB_PORT_H
#define _MB_PORT_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
    EV_READY           = 0x1 << 0,
    EV_PDUDATA_READY   = 0x1 << 1,              /* request PUD data is ready*/
    EV_FRAME_SENT      = 0x1 << 2,             /* request frame sent. */
    EV_FRAME_RECEIVED  = 0x1 << 3,            /* response freme received. */
    EV_FRAME_TIMEOUT   = 0x1 << 4,            /* response freme received. */

    EV_RESPOND_ERROR   = 0x1 << 5,
    EV_RESPOND_PROCESS = 0x1 << 6,            /* process response. */
    EV_RESPOND_TIMEOUT = 0x1 << 7,

    EV_REQU_FINISHED   = 0x1 << 8,
} mb_event_t;

BOOL            mb_event_init( void );
BOOL            mb_event_post( mb_event_t event );
BOOL            mb_event_get(mb_event_t * eEvent );
mb_exception_t    xMBWaitSlaveRespond();


BOOL            mb_serial_init( UCHAR port, ULONG baud_rate, UCHAR data_width, mb_parity_t parity );
void            mb_serial_close( void );
void            mb_serial_enable( BOOL xRxEnable, BOOL xTxEnable );
BOOL            mb_serial_rev_byte( CHAR *data );
BOOL            mb_serial_send_byte( CHAR data );

BOOL            mb_timer_init( USHORT usTimeOut50us );
void            mb_timer_close( void );
void            mb_t35_timer_enable( );
void            mb_turnaround_timer_enable( );
void            mb_response_timer_enable( );
void            mb_timers_disable( void );
void            vMBPortTimersDelay( USHORT usTimeOutMS );

extern          BOOL(*mb_timer_expired_func) ( void );

BOOL            xMBTCPPortInit( USHORT usTCPPort );
void            vMBTCPPortClose( void );
void            vMBTCPPortDisable( void );
BOOL            xMBTCPPortGetRequest( UCHAR **ppucMBTCPFrame, USHORT * usTCPLength );
BOOL            xMBTCPPortSendResponse( const UCHAR *pucMBTCPFrame, USHORT usTCPLength );

#ifdef __cplusplus
}
#endif
#endif
