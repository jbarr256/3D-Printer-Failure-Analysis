/*use state machines to fit the following description:

Idle State: 
- Check for any Serial Communication Input
- Program Receives Serial Input; Move to Downward State

Downward State:
- Move motor in the downward direction 
- Once motor recieves input from limit switch A, A2 move to Upward State

Upward State: 
- Move motor in upward direction 
- Once motor receives input from limit switch B, B2 output serial communication (1)
- Move to Idle State 

Emergency State: 
- Active in all states to jump to Emergency
- Triggered by a 'Stop' serial input 
- Stops all motion of motors
- Returns to idle
*/

#include <arduino.h>
#include <WVariant.h>
#include <variant.h>
#include <samd21/include/samd21g18a.h>

enum stateMachine{Idle,Downward,Upward,Emergency}state;
///0000 0000 0000
#define stepPinA 2 //3 on diagram //pulA ========== PA02 (0x400)
#define dirPinA 3  //4 on diagram //dirA ========== PA03 (0x800)
#define stepPinB 0 //1 on diagram //PulB ========== PA00 (0x004)
#define dirPinB 1 //2 on diagram  //dirB ========== PA01 (0x10)
#define ENpin 10 //11 on diagram         ========== PA10 (0x40)
#define LimitSwitchA 4 //5 on diagram    ========== PA04 (0x100)
#define LimitSwitchB 5 //6 on diagram    ========== PA05 (0x200)
#define LimitSwitchA2 8 //9 on diagram    ========== PA08 (0x80)
#define LimitSwitchB2 9 //10 on diagram    ========== PA09 (0x20)

int preVal = HIGH;
int but_press = 0;
int preValB = HIGH;
int but_pressB = 0;
char receivedChar;
boolean newData = false;

/*Values Corresponding to Their Pin Value:
pin 0 = 0x004
pin 1 = 0x10
pin 2 = 0x400
pin 3 = 0x800
pin 4 = 0x100
pin 5 = 0x200
.
pin 6 = 0x100 //dont work (UART)
pin 7 = 0x200 //dont work (UART)
.
pin 8 = 0x80
pin 9 = 0x20
pin 10 = 0x40
*/

/////////////////////////////////////////////////////////////////////////////////////////
void pullup(uint32_t ulPin){

EPortType port = g_APinDescription[ulPin].ulPort;
uint32_t pin = g_APinDescription[ulPin].ulPin;
uint32_t pinMask = (1ul << pin);
  PORT->Group[port].PINCFG[pin].reg=(uint8_t)(PORT_PINCFG_INEN|PORT_PINCFG_PULLEN) ;
  PORT->Group[port].DIRCLR.reg = pinMask ;
  PORT->Group[port].OUTSET.reg = pinMask ;
}
/////////////////////////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(9600);
  Serial.println("Serial Start:");

  pullup(LimitSwitchA);
  pullup(LimitSwitchB);
  pullup(LimitSwitchA2);
  pullup(LimitSwitchB2);

  PORT->Group[0].DIRSET.reg = (0x400);
  PORT->Group[0].DIRSET.reg = (0x800);
  PORT->Group[0].DIRSET.reg = (0x004);
  PORT->Group[0].DIRSET.reg = (0x10);
  PORT->Group[0].DIRSET.reg = (0x40);
  PORT->Group[0].OUTCLR.reg = (0x40);

}
/////////////////////////////////////////////////////////////////////////////////////////
int LScheckA(){
    if ( ((PORT->Group[g_APinDescription[4].ulPort].IN.reg & (1ul << g_APinDescription[4].ulPin)) != 0)  && ((PORT->Group[g_APinDescription[8].ulPort].IN.reg & (1ul << g_APinDescription[8].ulPin)) != 0) )
  {
    but_press = 1;
  }

    return but_press;
}
/////////////////////////////////////////////////////////////////////////////////////////
int LScheckB(){
    if ( (PORT->Group[g_APinDescription[5].ulPort].IN.reg & (1ul << g_APinDescription[5].ulPin)) != 0 && ((PORT->Group[g_APinDescription[9].ulPort].IN.reg & (1ul << g_APinDescription[9].ulPin)) != 0) )
   {
    but_pressB = 1;
  }
    return but_pressB;
}
/////////////////////////////////////////////////////////////////////////////////////////
/*
void SerialReceive() {
    if (Serial.available() > 0) {
        receivedChar = Serial.read();
        newData = true;
    }
}
*/

/////////////////////////////////////////////////////////////////////////////////////////
void MotorControl(){
  switch(state){
    case Idle:
    /*if(newData == true){
    Serial.println("Current State: Downward");
    state = Downward;
    newData = false; 
    }
    */
    if(Serial.read() == 'a'){
    Serial.println("Current State: Downward");
    state = Downward;      
    }
    break;

    case Downward:
    if(Serial.read() == 's'){
      Serial.println(" CRITICAL FAILURE - PLEASE MANUALLY RESTART");
      Serial.println(" EMERGENCY MODE: \n Please clear all objects from the print area \n Please ensure all motors are properly aligned \n In order to leave Emergency Mode, please press both of the bottom limit switches at the same time.");
      state = Emergency;
    }
    if(LScheckA() == 1){
      Serial.println("Current State: Upward");
      state = Upward; 
      but_press = 0;
      //newData = false; 
      }
      break;
    case Upward:
    if(Serial.read() == 's'){
      Serial.println("CRITICAL FAILURE - PLEASE MANUALLY RESTART");
      Serial.println(" EMERGENCY MODE: \n Please clear all objects from the print area \n Please ensure all motors are properly aligned \n In order to leave Emergency Mode, please press both of the bottom limit switches at the same time.");
      state = Emergency;
    }
      if(LScheckB() == 1){
      Serial.println("Current State: Idle");

      for(int i = 0; i <= 20; i++){
      Serial.println("1");
      delayMicroseconds(300);        
      }

      state = Idle;  
      but_pressB = 0;
      //newData = false; 
      }
    break; 
    case Emergency:
    if( ((PORT->Group[g_APinDescription[4].ulPort].IN.reg & (1ul << g_APinDescription[4].ulPin)) != 0)  && ((PORT->Group[g_APinDescription[8].ulPort].IN.reg & (1ul << g_APinDescription[8].ulPin)) != 0) ){
      Serial.println("Returning to Idle State.");
      state = Idle;
    }
    break;
  }

  switch(state){
    case Idle:
    PORT->Group[0].OUTCLR.reg = (0x40);
    break;        
    case Downward:
    MotorBackward();
    break;
    case Upward:
    MotorForward();
    break;
    case Emergency:
    PORT->Group[0].OUTSET.reg = (0x40);    
    break;
  }
      
}

/////////////////////////////////////////////////////////////////////////////////////////
void MotorBackward(){
  


  PORT->Group[0].OUTCLR.reg = (0x800); //dirPinA
  PORT->Group[0].OUTCLR.reg = (0x10); //dirPinB

  PORT->Group[0].OUTSET.reg = (0x400); //stepPinA
  PORT->Group[0].OUTSET.reg = (0x004); //setpPinB

  delayMicroseconds(200); 

  PORT->Group[0].OUTCLR.reg = (0x400); //stepPinA
  PORT->Group[0].OUTCLR.reg = (0x004); //stepPinB

  delayMicroseconds(200); 

}
/////////////////////////////////////////////////////////////////////////////////////////
void MotorForward(){ 

  PORT->Group[0].OUTSET.reg = (0x800); //dirPinA
  PORT->Group[0].OUTSET.reg = (0x10); //dirPinB
  PORT->Group[0].OUTSET.reg = (0x400); //stepPinA
  PORT->Group[0].OUTSET.reg = (0x004); //stepPinB

  delayMicroseconds(200); 


  PORT->Group[0].OUTCLR.reg = (0x400); //stepPinA
  PORT->Group[0].OUTCLR.reg = (0x004); //stepPinB

  delayMicroseconds(200); 
}


/////////////////////////////////////////////////////////////////////////////////////////
void loop() {
//SerialReceive();

MotorControl();
//newData == false;

}
