#include "sam.h"
#include "definitions.h"
#include "app.h"
#include "app.c"

void ClocksInit(void);

int main(void){
  AppInit();
  while(1){
    AppRun();
  }
}
