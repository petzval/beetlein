#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

// Declare handle storage names as integer pointers 
int *txthand,*txtprhand,*colhand,*colprhand,*fonthand,*fontprhand;
int *dishand,*disprhand,*disnewhand,*imagehand,*imageprhand,*image;

int flip[256];

int main()
  {
  btle_server(onEvent,"Changes");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n;
    
  if(event == SERVER_START)
    {
    // Called once on server start
    // Set up storage
  
    for(n = 0 ; n < 256 ; ++n)
      flip[n] = 0;

    txthand = btle_handles();
    txtprhand = btle_handles();
    colhand = btle_handles();
    colprhand = btle_handles();
    fonthand = btle_handles();
    fontprhand = btle_handles();
    dishand = btle_handles();
    disprhand = btle_handles();
    disnewhand = btle_handles();
    imagehand = btle_handles();
    imageprhand = btle_handles();
    image = btle_handles();
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device connects or restarts
    
    flip[device] = 0;
  
    txthand[device] = btle_button(device,"OK");
    txtprhand[device] = btle_text(device,"Change text");
    btle_newline(device);
    colhand[device] = btle_button(device,"OK");
    colprhand[device] = btle_text(device,"Change colour");
    btle_newline(device);
    fonthand[device] = btle_button(device,"OK");
    fontprhand[device] = btle_text(device,"Change font");
    btle_newline(device);
    dishand[device] = btle_button(device,"OK");
    disprhand[device] = btle_text(device,"Disappear");
    disnewhand[device] = btle_newline(device);
    imagehand[device] = btle_button(device,"OK");
    imageprhand[device] = btle_text(device,"Change image");
    image[device] = btle_image(device,60,50,3,200,200,200);
    btle_image_rect(device,image[device],10,10,25,25,255,0,0,STYLE_FILL,0);
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    
    if(handle == txthand[device])
      {
      flip[device] ^= 1;
      if((flip[device] & 1) == 0)
        btle_change_text(device,txtprhand[device],"Change text");
      else
        btle_change_text(device,txtprhand[device],"Change text back");
      }
    else if(handle == colhand[device])
      {
      flip[device] ^= 2;
      if((flip[device] & 2) == 0)
        btle_change_colour(device,colprhand[device],255,255,255);
      else
        btle_change_colour(device,colprhand[device],180,255,180);
      }
    else if(handle == fonthand[device])
      {
      flip[device] ^= 4;
      if((flip[device] & 4) == 0)
        btle_change_font(device,fontprhand[device],FONT_DEFAULT);
      else
        btle_change_font(device,fontprhand[device],FONT_THICK);
      }
    else if(handle == dishand[device] && (flip[device] & 8) == 0)
      {
      flip[device] ^= 8;
      btle_remove(device,dishand[device]);
      btle_remove(device,disprhand[device]);
      btle_remove(device,disnewhand[device]);
      }
    else if(handle == imagehand[device])
      {
      flip[device] ^= 16;
      btle_image_clear(device,image[device]);
      if((flip[device] & 16) == 0)
        {
        btle_change_colour(device,image[device],200,200,200);
        btle_image_rect(device,image[device],5,5,20,20,255,0,0,STYLE_FILL,0);
        }
      else
        {
        btle_change_colour(device,image[device],150,150,150);
        btle_image_circle(device,image[device],35,30,15,0,255,0,STYLE_FILL,0);
        }
      }      
    }
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
