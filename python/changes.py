#!/usr/bin/python3
from btle import *

# Declare global handle storage names 
flip = None
txthand = None
txtprhand = None
colhand = None
colprhand = None
fonthand = None
fontprhand = None
dishand = None
disprhand = None
disnewhand = None
imagehand = None
imageprhand = None
image = None

def onEvent(event,device,handle,member,text):
  global flip,txthand,txtprhand,colhand,colprhand,fonthand,fontprhand
  global dishand,disprhand,disnewhand,imagehand,imageprhand,image


  if event == SERVER_START:
    # Called once on server start
  
    flip = [0 for n in range(256)]
  
    # Initialise handle memory
    txthand = btle_handles()
    txtprhand = btle_handles()
    colhand = btle_handles()
    colprhand = btle_handles()
    fonthand = btle_handles()
    fontprhand = btle_handles()
    dishand = btle_handles()
    disprhand = btle_handles()
    disnewhand = btle_handles()
    imagehand = btle_handles()
    imageprhand = btle_handles()
    image = btle_handles()

  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts

    flip[device] = 0

    txthand[device] = btle_button(device,"OK")
    txtprhand[device] = btle_text(device,"Change text")
    btle_newline(device)
    colhand[device] = btle_button(device,"OK")
    colprhand[device] = btle_text(device,"Change colour")
    btle_newline(device)
    fonthand[device] = btle_button(device,"OK")
    fontprhand[device] = btle_text(device,"Change font")
    btle_newline(device)
    dishand[device] = btle_button(device,"OK")
    disprhand[device] = btle_text(device,"Disappear")
    disnewhand[device] = btle_newline(device)
    imagehand[device] = btle_button(device,"OK")
    imageprhand[device] = btle_text(device,"Change image")
    image[device] = btle_image(device,60,50,3,200,200,200)
    btle_image_rect(device,image[device],10,10,25,25,255,0,0,STYLE_FILL,0)
  
  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked
    if(handle == txthand[device]):
      flip[device] = flip[device] ^ 1
      if((flip[device] & 1) == 0):
        btle_change_text(device,txtprhand[device],"Change text")
      else:
        btle_change_text(device,txtprhand[device],"Change text back")
    elif(handle == colhand[device]):
      flip[device] = flip[device] ^ 2
      if((flip[device] & 2) == 0):
        btle_change_colour(device,colprhand[device],255,255,255)
      else:
        btle_change_colour(device,colprhand[device],180,255,180)
    elif(handle == fonthand[device]):
      flip[device] = flip[device] ^ 4
      if((flip[device] & 4) == 0):
        btle_change_font(device,fontprhand[device],FONT_DEFAULT)
      else:
        btle_change_font(device,fontprhand[device],FONT_THICK)
    elif(handle == dishand[device] and (flip[device] & 8) == 0):
      flip[device] = flip[device] ^ 8
      btle_remove(device,dishand[device])
      btle_remove(device,disprhand[device])
      btle_remove(device,disnewhand[device])
    elif(handle == imagehand[device]):
      flip[device] = flip[device] ^ 16
      btle_image_clear(device,image[device])
      if((flip[device] & 16) == 0):
        btle_change_colour(device,image[device],200,200,200)
        btle_image_rect(device,image[device],5,5,20,20,255,0,0,STYLE_FILL,0)
      else:
        btle_change_colour(device,image[device],150,150,150)
        btle_image_circle(device,image[device],35,30,15,0,255,0,STYLE_FILL,0)
 
  elif event == BTLE_DISCONNECT:
    # Called when an Android device disconnects
    # return(BTLE_EXIT) 
    pass  
   
  return(BTLE_CONTINUE)
  
# ***** program START ******  
  
btle_server(onEvent,"Changes")
