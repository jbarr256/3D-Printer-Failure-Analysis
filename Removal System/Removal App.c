#include "app.h"
//#include "clock.h"

void AppInit(void){
  //ClocksInit();
  //assign LED0 as OUTPUT
  REG_PORT_DIR0 = LED0_PIN_MASK;

  //set LED0 OFF
  REG_PORT_OUTCLR0 = LED0_PIN_MASK;
}

void AppRun(void){
  while(1){
    //set drive strength to strong
    PORT->Group[LED0_PORT].PINCFG[LED0_PIN_NUMBER].bit.DRVSTR = 1;
    
    //Turn the LED on PA7 ON
    REG_PORT_OUTSET0 = LED0_PIN_MASK;
  }
}
