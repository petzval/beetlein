#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);


int main()
  {
  btle_server(onEvent,"Fonts");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  
  if(event == SERVER_START)
    {
    // Called once on server start
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    btle_text(device,"DEFAULT abc");
    btle_font(device,FONT_THIN);
    btle_text(device,"THIN abc");
    btle_font(device,FONT_LIGHT);
    btle_text(device,"LIGHT abc");
    btle_newline(device);
    btle_font(device,FONT_MEDIUM);
    btle_text(device,"MEDIUM abc");
    btle_font(device,FONT_THICK);
    btle_text(device,"THICK abc");
    btle_font(device,FONT_CONDENSED);
    btle_text(device,"CONDENSED abc");
    btle_newline(device);
    btle_font(device,FONT_FIXED);
    btle_text(device,"FIXED abc");
    btle_font(device,FONT_SERIF);
    btle_text(device,"SERIF abc");
    btle_font(device,FONT_SERIF_FIXED);
    btle_text(device,"SERIF_FIXED abc");
    btle_newline(device);
    btle_font(device,FONT_CASUAL);
    btle_text(device,"CASUAL abc");
    btle_font(device,FONT_DANCING);
    btle_text(device,"DANCING abc");
    btle_font(device,FONT_GOTHIC);
    btle_text(device,"GOTHIC abc");
    }
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
  
