#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

// Declare global handle storage names here as integer pointers 
// int *buthand,*checkhand,*selhand,*texthand,*txtinhand,*newhand,*imagehand;

int main()
  {
  btle_server(onEvent,"Empty");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  
  if(event == SERVER_START)
    {
    // Called once on server start
    //   device = invalid
    //   handle = invalid
    //   member = invalid
    //     text = invalid
    // Initialise handle storage
    //   texthand = btle_handles();
    //   buthand = btle_handles();
    //   checkhand = btle_handles();
    //   selhand = btle_handles();
    //   txtinhand = btle_handles();
    //   imagehand = btle_handles();
    //   newhand = btle_handles();
    // Call these two here if required
    //   btle_password("password");
    //   btle_slave();
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    //   device = identifies Android device (1-254)
    //   handle = invalid
    //   member = invlaid
    //     text = Invalid
    // Add items to Android screen and store handles if needed
    //   texthand[device] = btle_text(device,"Hello");
    //   buthand[device] = btle_button(device,"OK");
    //   checkhand[device] = btle_check(device,UNCHECKED);
    //   selhand[device] = btle_select(device,"Prompt,Member 0,Member 1,Member 2");
    //   txtinhand[device] = btle_text_input(device,8);
    //   newhand[device] = btle_newline(device);
    //   imagehand[device] = btle_image(device,400,200,4,220,220,220);
    // Send a message to scrollable message area
    //   btle_message(device,"Hello");
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    //   device = identifies Android device
    //   handle = identifies button item
    //   member = invalid
    //     text = invalid
    // Deal with button click
    //   if(handle == buthand[device])
    //     printf("Button clicked\n");  
    }
  else if(event == BTLE_CLICK_CHECK)
    {
    // Check box has been clicked
    //   device = identifies Android device
    //   handle = identifies check box item
    //   member = UNCHECKED or CHECKED
    //     text = invalid
    // Deal with check click
    //   if(handle == checkhand[device])
    //     {
    //     if(member == UNCHECKED) 
    //       printf("Unchecked\n");
    //     else if(member == CHECKED)
    //       printf("Checked\n");
    //     }  
    }
  else if(event == BTLE_CLICK_SELECT)
    {
    // A member has been selected from a drop-down select
    //   device = identifies Android device
    //   handle = identifies select item
    //   member = index of selection (0 to number of members-1)
    //     text = invalid
    // Deal with selection 
    //   if(handle == selhand[device])
    //     printf("Member %d selected\n",member);    
    }
  else if(event == BTLE_CLICK_TEXT)
    {
    // Text has been sent from a text input box
    //   device = identifies Android device
    //   handle = identifies text input item
    //   member = invalid
    //     text = text sent
    // Deal with text 
    // if(handle == txtinhand[device])
    //   printf("Text sent = %s\n",text);
    }
  else if(event == BTLE_BROADCAST)
    {
    // Another Pi has broadcast a message to all other Pis
    //   device = identifies Android device that distributed the message
    //   handle = invalid
    //   member = invalid
    //     text = message text 
    // Deal with message 
    //   printf("Message from another Pi = %s\n",text);   
    }
  
  else if(event == SERVER_TIMER)
    {
    // Called at regular intervals if timer has been 
    // set via btle_timer(ds) where ds is the interval
    // in deci-seconds. So btle_timer(10) is once per second
    // Not associated with any particular Android device
    //   device = invalid
    //   handle = invalid
    //   member = invalid
    //     text = invalid
    // Deal with timer tick 
    //   printf("Timer tick\n");
    // To send any instructions to a device here you must know
    // the device number because the device parameter is invalid
    // To identify all connected devices:
    //   for(n = 1 ; n <= btle_maxdevice() ; ++n)
    //     {
    //     if(btle_connected(n) == 1)
    //       {  // device n is connected
    //       }
    //     }
    }
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    //   device = identifies Android device
    //   handle = invalid
    //   member = invalid
    //     text = invalid
    // Do not call any more btle_ instructions for device
    // return(BTLE_EXIT)      to exit from server
    // return(BTLE_CONTINUE)  to continue dealing with other
    //     connected devices, and/or wait for new connections
    }
     
  return(BTLE_CONTINUE);     
  }  // end onEvent
  
  
