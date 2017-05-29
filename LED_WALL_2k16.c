#include <msp430G2553.h>
/*-------------------------------------------------
 TECHNITES 2k16

                        MSP430G2553
                      -----------------
            3.3 V -->|Vcc          Gnd |<-- Ground
                     |                 |
          Unused  -->|P1.0         P2.7|--> unused
                     |                 |
               Rx -->|P1.1         P2.6|--> unused
                     |                 |
               Tx <--|P1.2         TST |--> Open
                     |                 |
                  <--|P1.3         RST |<-- Pulled high
                     |                 |
        SCLK_5916 <--|P1.4         P1.7|--> SIN_5916
                     |                 |
        LTCH_5916 <--|P1.5         P1.6|--> unused
                     |                 |
                  <--|P2.0         P2.5|<-- unused
                     |                 |
                  <--|P2.1         P2.4|<--
                     |                 |
                  <--|P2.2         P2.3|<--
                      -----------------
  -------------------------------------------------*/

//PIN 5916 PORT1
#define SIN5916 	 BIT7
#define SCLK5916     BIT4
#define LTCH5916 	 BIT5
#define N_channel	 48
#define arr_size	 (N_channel/8)

void serial_println_8(char val)
{
 while (!(IFG2&UCA0TXIFG));                // USCI_A0 TX buffer ready?
  UCA0TXBUF = val;
}

char rx_count=0,strobe;
unsigned char disp_arr[arr_size]={0xFF,0x00,0xFF,0x00,0xFF,0x00};
void InitializeClocks(void);
void SendData(void);

void main(void)
{
	char temp_disp,i;
    WDTCTL = WDTPW + WDTHOLD;
	//TLC initialization
	P1DIR = 0;
    P1DIR |= (SIN5916 + SCLK5916 + LTCH5916);
    P1OUT=0;
    P1SEL = BIT1 + BIT2 ;                     // P1.1 = RXD, P1.2=TXD
    P1SEL2 = BIT1 + BIT2;
    UCA0CTL1 |= UCSSEL_2;                     // SMCLK
    UCA0BR0 = 104;                           // 1MHz 9600
    UCA0BR1 = 0;                           // 1MHz 9600
    UCA0MCTL = UCBRS2 + UCBRS0;               // Modulation UCBRSx = 5
    UCA0CTL1 &= ~UCSWRST;                     // **Initialize USCI state machine**

    InitializeClocks();						  // Setup clock
    IE2 |= UCA0RXIE;                          // Enable USCI_A0 RX interrupt
    _bis_SR_register(GIE);


    while (1)
    {
		SendData();
		P1OUT|=LTCH5916;
        P1OUT&=~(LTCH5916);
        if(strobe=='S')
        {
        	rx_count=0;
           	serial_println_8('K');
           	strobe=0;
        }

    }

}


void SendData(void)
{
	char i,temp;
    P1OUT &= ~(SIN5916 + LTCH5916 + SCLK5916);
    for (i = 0; i < arr_size; i++)
	{
		temp=disp_arr[i];
		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;

		P1OUT&=~(SIN5916);
		P1OUT|=SIN5916&temp;
		P1OUT|=SCLK5916;
		P1OUT&=~SCLK5916;
		temp=temp<<1;
	}

}

void InitializeClocks(void)
{
  BCSCTL1 = CALBC1_1MHZ;
  DCOCTL = CALDCO_1MHZ;
}

#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
  strobe= UCA0RXBUF;                    // TX -> RXed character
  if(!(strobe=='S'))
  {
	if(rx_count<arr_size)
		disp_arr[rx_count++]=strobe;
  }

}