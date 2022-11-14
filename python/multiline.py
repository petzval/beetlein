#!/usr/bin/python3
from btle import *


imag = None

def onEvent(event,device,handle,member,text):
  global imag

  if event == SERVER_START:
    imag = btle_handles()
  elif event == BTLE_CONNECT:
 
    imag[device] = btle_image(device,600,350,8,230,230,230)

    x = [0.0 for n in range(8)]
    y = [0.0 for n in range(8)]
    
    flip = 0
    for n in range(8):
      x[n] = 70 * (n+1)
      y[n] = 25 * flip + 50
      flip = 1 - flip 
      
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_OFF,0)
    btle_image_text(device,imag[device],"POINTS_OFF",5,40,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)

    for n in range(8):
      y[n] = y[n] + 50
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_SQUARE,4)
    btle_image_text(device,imag[device],"POINTS_SQUARE",5,90,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)
    
    for n in range(8):
       y[n] = y[n] + 50
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_TRIANGLE,4)
    btle_image_text(device,imag[device],"POINTS_TRIANGLE",5,140,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)
    
    for n in range(8):
       y[n] = y[n] + 50
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_CROSS,4)
    btle_image_text(device,imag[device],"POINTS_CROSS",5,190,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)
    
    for n in range(8):
       y[n] = y[n] + 60
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_SQUARE | POINTS_ONLY,4)
    btle_image_text(device,imag[device],"POINTS_SQUARE | POINTS_ONLY",5,250,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)
 
    for n in range(8):
      y[n] = y[n] + 50
    x[3] = LINE_BREAK
    y[3] = LINE_BREAK
    btle_image_multiline(device,imag[device],x,y,0,7,1,0,0,0,POINTS_OFF,4)
    btle_image_text(device,imag[device],"POINTS_OFF",5,300,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)
    btle_image_text(device,imag[device],"LINE_BREAK",245,325,DIRN_HORIZ,FONT_DEFAULT,12,0,0,0)

    
  elif event == BTLE_DISCONNECT:
    # return(BTLE_EXIT)  
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Multiline")



