#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

// Declare handle storage names as integer pointers 
int *hellobut,*checkbut,*checktxt,*worldbut,*selecthand,*txtinhand;

int main()
  {
  btle_server(onEvent,"Hello");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  
  if(event == SERVER_START)
    {
    // Called once when server starts
    // Set up handle storage
    hellobut = btle_handles();
    worldbut = btle_handles();
    selecthand = btle_handles();
    checkbut = btle_handles();
    checktxt = btle_handles();
    txtinhand = btle_handles();
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when Android device connects or restarts
    // Add items to Android screen and store handles
    btle_message(device,"Hello world message");      
    btle_text(device,"Hello world text");
    btle_newline(device);
    hellobut[device] = btle_button(device,"Hello");
    worldbut[device] = btle_button(device,"World");
    btle_text(device,"Buttons");
    btle_newline(device);
    btle_text(device,"Check box");
    checkbut[device] = btle_check(device,UNCHECKED);
    checktxt[device] = btle_text(device,"Hello world");
    btle_remove(device,checktxt[device]);
    btle_newline(device);
    btle_text(device,"Send a reply");
    txtinhand[device] = btle_text_input(device,10);
    btle_newline(device);
    btle_text(device,"Select a word");
    selecthand[device] = btle_select(device,"Select,Hello,World");
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    if(handle == hellobut[device])
      printf("Hello button clicked\n");
    else if(handle == worldbut[device])
      printf("World button clicked\n");   
    }
  else if(event == BTLE_CLICK_CHECK)
    {
    // Check box has been clicked
    if(handle == checkbut[device])
      { 
      if(member == 0)
        {
        printf("Box unchecked\n");
        // remove hello world text
        btle_remove(device,checktxt[device]);
        }
      else
        {
        printf("Box checked\n");
        // restore hello world text
        btle_restore(device,checktxt[device]);
        }
      }
    }
  else if(event == BTLE_CLICK_SELECT)
    {
    // A member has been selected from a drop-down select
    if(handle == selecthand[device])
      {  
      if(member == 0)
        printf("Hello selected\n");
      else if(member == 1)
        printf("World selected\n");
      }
    }
  else if(event == BTLE_CLICK_TEXT)
    {
    // Text has been sent from a text input box
    if(handle == txtinhand[device])
      printf("Reply = %s\n",text);
    }
  else if(event == BTLE_DISCONNECT)
    {
    // Android device disconnected
    // return(BTLE_EXIT);  // to exit server 
    }
     
  return(BTLE_CONTINUE);     
  }  // end onEvent
  


