#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

int main()
  {
  btle_server(onEvent,"Password");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
 
  if(event == SERVER_START)
    {
    // Called once on server start
    printf("*************\n");
    printf("  HINT - enter password on Android = btle\n");
    printf("*************\n");
    btle_password("btle");
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    // but only after correct password entry
    btle_text(device,"Password correct");  
    }
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
  
