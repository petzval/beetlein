#!/usr/bin/python3
from btle import *

# Declare handle storage name
image = None

def onEvent(event,device,handle,member,text):
  global image
 
  if event == SERVER_START:
    # Called once on server start
    # Initialise handle memory
    image = btle_handles()
    
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts

    image[device] = btle_image(device,420,260,8,220,220,220)
    btle_image_text(device,image[device],"line",10,30,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_line(device,image[device],5,50,45,50,1,0,0,0)
    btle_image_text(device,image[device],"arc",60,30,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_arc(device,image[device],45,50,95,100,50,CLOCK_SHORT,1,0,0,0)
    
    btle_image_text(device,image[device],"3 pixels",110,30,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_line(device,image[device],105,50,145,50,3,0,0,0)
    btle_image_arc(device,image[device],145,50,195,100,50,CLOCK_SHORT,3,0,0,0)

    # x,y data for btle_multiline   
    x = [0 for n in range(5)]
    y = [0 for n in range(5)] 
    x[0] = 0
    y[0] = 0
    x[1] = 40
    y[1] = 0
    x[2] = 60
    y[2] = 20
    x[3] = 60
    y[3] = 50
    x[4] = 95
    y[4] = 50
    
    for n in range(5):
      x[n] = x[n] + 205
      y[n] = y[n] + 50
   
    btle_image_text(device,image[device],"multiline",210,30,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_multiline(device,image[device],x,y,0,4,1,0,0,0,POINTS_OFF,0)
    
    for n in range(5):
      x[n] = x[n] + 100
    
    btle_image_text(device,image[device],"POINTS_SQUARE",300,30,DIRN_HORIZ,FONT_DEFAULT,14,0,0,0)
    btle_image_multiline(device,image[device],x,y,0,4,1,0,0,0,POINTS_SQUARE,3)
  
    btle_image_rect(device,image[device],15,105,85,190,255,150,150,STYLE_FILL,0)
    btle_image_text(device,image[device],"rect",35,145,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_text(device,image[device],"FILL",35,165,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)

    btle_image_rect(device,image[device],115,105,185,190,255,0,0,STYLE_STROKE,1)

    btle_image_text(device,image[device],"rect",145,160,DIRN_VERT,FONT_DEFAULT,16,0,0,0);
    btle_image_text(device,image[device],"STROKE",165,177,DIRN_VERT,FONT_DEFAULT,16,0,0,0);

    #btle_image_text(device,image[device],"rect",135,145,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    #btle_image_text(device,image[device],"STROKE",120,165,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
        
    btle_image_circle(device,image[device],250,150,40,0,170,240,STYLE_STROKE,3)
    btle_image_text(device,image[device],"circle",230,145,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_text(device,image[device],"STROKE",225,165,DIRN_HORIZ,FONT_DEFAULT,14,0,0,0)
   
    btle_image_oval(device,image[device],310,120,390,180,15,210,70,STYLE_FILL,0)
    btle_image_text(device,image[device],"oval",335,150,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)
    btle_image_text(device,image[device],"FILL",335,165,DIRN_HORIZ,FONT_DEFAULT,16,0,0,0)

    btle_image_text(device,image[device],"THICK font",50,240,DIRN_HORIZ,FONT_THICK,30,255,0,0)
    btle_image_text(device,image[device],"SERIF font",250,240,DIRN_HORIZ,FONT_SERIF,24,0,0,0)

  
  elif event == BTLE_DISCONNECT:
    # Called when an Android device disconnects
    # return(BTLE_EXIT) 
    pass  
   
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Graphics")


