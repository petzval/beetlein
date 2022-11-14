#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

// Declare handle storage names as integer pointers e.g.
int *buthand,*texthand,*selhand,*checkhand,*broadhand;

int main()
  {
  btle_server(onEvent,"Master");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  
  if(event == SERVER_START)
    {
    // Called once on server start
    // Initialise handle storage 
    buthand = btle_handles();
    texthand = btle_handles();
    selhand = btle_handles();
    checkhand = btle_handles();
    broadhand = btle_handles();
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    // The Master and all slaves must have this design
    buthand[device] = btle_button(device,"OK");
    selhand[device] = btle_select(device,"Select,Zero,One,Two");
    checkhand[device] = btle_check(device,UNCHECKED);
    btle_newline(device);
    texthand[device] = btle_text_input(device,16);
    btle_newline(device);
    btle_text(device,"Broadcast from Pi to slaves");
    broadhand[device] = btle_button(device,"OK");
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    if(handle == buthand[device])
      printf("OK clicked\n");
    else if(handle == broadhand[device])
      btle_broadcast("Hello");
    }
  else if(event == BTLE_CLICK_CHECK)
    {
    // Check box has been clicked
    if(handle == checkhand[device])
      {
      if(member == UNCHECKED) 
        printf("Unchecked\n");
      else
        printf("Checked\n"); 
      }
    }
  else if(event == BTLE_CLICK_SELECT)
    {
    // A member has been selected from a drop-down select
    if(handle == selhand[device])
      {
      printf("Member %d selected\n",member);    
      }  
    }
  else if(event == BTLE_CLICK_TEXT)
    {
    // Text has been sent from a text input box
    if(handle == texthand[device])
      {
      printf("Text sent = %s\n",text);
      }  
    }
  else if(event == BTLE_BROADCAST)
    printf("Got broadcast = %s\n",text);
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
  
