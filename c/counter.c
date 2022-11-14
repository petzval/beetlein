#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

int main()
  {
  btle_server(onEvent,"Counter");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n,k,dn;
  char s[32];
  static int count[256],stopstart[256];
  static int *prompt,*start,*stop;

   
  if(event == SERVER_START)
    {
    prompt = btle_handles();
    start = btle_handles();
    stop = btle_handles();
    
    for(n = 0 ; n < 256 ; ++n)
      {
      count[n] = 0;
      stopstart[n] = 0;
      }
    }
  else if(event == BTLE_CONNECT)
    {
    count[device] = 0;
    stopstart[device] = 0;
    
    prompt[device] = btle_text(device,"Count = 0");
    btle_newline(device);

    start[device] = btle_button(device,"Start");
    btle_change_colour(device,start[device],160,220,160);
    
    stop[device] = btle_button(device,"Stop");    
    btle_change_colour(device,stop[device],120,120,120);

    btle_timer(10);  // 1 second timer
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    if(handle == start[device])
      {
      stopstart[device] = 1;
      btle_change_colour(device,stop[device],160,220,160);
      btle_change_colour(device,start[device],150,150,150);
      }
    if(handle == stop[device])
      {
      stopstart[device] = 0;  
      btle_change_colour(device,start[device],160,220,160);
      btle_change_colour(device,stop[device],150,150,150);
      }
    }
  else if(event == SERVER_TIMER)
    {
    // applies to all devices (device/item/handle = 0)
    for(n = 1 ; n <= btle_maxdevice() ; ++n)
      {
      if(btle_connected(n) == 1 && stopstart[n] == 1)
        {
        ++count[n];
        sprintf(s,"Count = %d",count[n]);
        btle_change_text(n,prompt[n],s);
        }
      }
    }
  else if(event == BTLE_DISCONNECT)
    {
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
