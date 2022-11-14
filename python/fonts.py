#!/usr/bin/python3
from btle import *


def onEvent(event,device,handle,member,text):
 
  if event == BTLE_CONNECT:
    btle_text(device,"DEFAULT abc")
    btle_font(device,FONT_THIN)
    btle_text(device,"THIN abc")
    btle_font(device,FONT_LIGHT)
    btle_text(device,"LIGHT abc")
    btle_newline(device)
    btle_font(device,FONT_MEDIUM)
    btle_text(device,"MEDIUM abc")
    btle_font(device,FONT_THICK)
    btle_text(device,"THICK abc")
    btle_font(device,FONT_CONDENSED)
    btle_text(device,"CONDENSED abc")
    btle_newline(device)
    btle_font(device,FONT_FIXED)
    btle_text(device,"FIXED abc")
    btle_font(device,FONT_SERIF)
    btle_text(device,"SERIF abc")
    btle_font(device,FONT_SERIF_FIXED)
    btle_text(device,"SERIF_FIXED abc")
    btle_newline(device)
    btle_font(device,FONT_CASUAL)
    btle_text(device,"CASUAL abc")
    btle_font(device,FONT_DANCING)
    btle_text(device,"DANCING abc")
    btle_font(device,FONT_GOTHIC)
    btle_text(device,"GOTHIC abc")
    
  elif event == BTLE_DISCONNECT:
    # return(BTLE_EXIT)  
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Fonts")

