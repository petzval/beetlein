#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

// Declare handle storage names as integer pointers 
int *buthand,*texthand,*selhand,*checkhand,*broadhand,*messhand;


int main()
  {
  btle_server(onEvent,"Commentary");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n,flag;
  char s[256];
  
  if(event == SERVER_START)
    {
    // Called once on server start
    // Initialise handle storage
    buthand = btle_handles();
    texthand = btle_handles();
    selhand = btle_handles();
    checkhand = btle_handles();
    broadhand = btle_handles();
    messhand = btle_handles();
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    printf("%s Connected or restarted\n",btle_name(device));
   
    buthand[device] = btle_button(device,"OK");
    selhand[device] = btle_select(device,"Prompt,Member 0,Member 1,Member 2");
    btle_text(device,"Timer");
    checkhand[device] = btle_check(device,UNCHECKED);
    btle_newline(device);
    texthand[device] = btle_text_input(device,16);
    btle_newline(device);
    btle_text(device,"Tell Pi to...");
    btle_newline(device);
    broadhand[device] = btle_button(device,"OK");
    btle_text(device,"..broadcast to other Pis");
    btle_newline(device);
    messhand[device] = btle_button(device,"OK");
    btle_text(device,"..send message to other Androids");
   
    sprintf(s,"%s connect or restart",btle_local_name());
    btle_message(device,s);
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    if(handle == buthand[device])
      {
      printf("%s OK clicked\n",btle_name(device));
      sprintf(s,"%s OK button",btle_local_name());
      btle_message(device,s);
      }
    if(handle == broadhand[device])
      {
      // Broadcast a message to other connected Pis
      printf("%s Broadcasting to other Pis\n",btle_name(device));
      btle_broadcast("Hello broadcast");
      btle_message(device,"Message broadcast to other Pis");
      }
    if(handle == messhand[device])
      {
      // Send a message to other connected Androids
      printf("%s Send message to all Androids\n",btle_name(device));
      btle_message_all("Hello all");
      btle_message(device,"Message sent to all Androids");
      }
    }
  else if(event == BTLE_CLICK_CHECK)
    {
    // Check box has been clicked
    if(handle == checkhand[device])
      {
      if(member == UNCHECKED) 
        {
        printf("%s Unchecked timer off\n",btle_name(device));          
        sprintf(s,"%s timer off",btle_local_name());
        btle_message(device,s);
        btle_timer(0);
        }
      else
        {
        printf("%s Checked timer on\n",btle_name(device));
        sprintf(s,"%s 3s timer on",btle_local_name());
        btle_message(device,s);
        btle_timer(30);
        }
      } 
    }
  else if(event == BTLE_CLICK_SELECT)
    {
    // A member has been selected from a drop-down select
    if(handle == selhand[device])
      {
      printf("%s Member %d selected\n",btle_name(device),member); 
      sprintf(s,"%s select",btle_local_name());
      btle_message(device,s);
      }
    }
  else if(event == BTLE_CLICK_TEXT)
    {
    // Text has been sent from a text input box
    if(handle == texthand[device])
      {
      printf("Text from %s = %s\n",btle_name(device),text);
      sprintf(s,"%s text received",btle_local_name());
      btle_message(device,s);
      }  
    }
  else if(event == BTLE_BROADCAST)
    {
    // Another Pi has broadcast a message
    printf("Broadcast = %s\n",text);
    sprintf(s,"%s has received broadcast",btle_local_name());
    btle_message(device,s);
    }
  else if(event == SERVER_TIMER)
    {
    // Called at regular intervals if timer has been set 
    printf("Timer tick\n");
    
    // Send message to all connected devices  
    btle_message_all("Timer tick");
    }
  else if(event == BTLE_DISCONNECT)
    {
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
  
