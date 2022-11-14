#!/usr/bin/python3
from btle import *

def onEvent(event,device,handle,member,text):
  
  if event == BTLE_CONNECT:

    btle_font(device,FONT_CONDENSED)
    hand = btle_text(device,"195,195,195")
    btle_change_colour(device,hand,195,195,195)
    hand = btle_text(device,"120,120,120")
    btle_change_colour(device,hand,120,120,120)
    hand = btle_text(device,"200,100,100")
    btle_change_colour(device,hand,200,100,100)
    hand = btle_text(device,"250,80,80")
    btle_change_colour(device,hand,250,80,80)
    btle_newline(device)
    hand = btle_text(device,"140,255,250")
    btle_change_colour(device,hand,140,255,250)
    hand = btle_text(device,"0,168,243")
    btle_change_colour(device,hand,0,168,243)
    hand = btle_text(device,"100,100,200")
    btle_change_colour(device,hand,100,100,200)
    hand = btle_text(device,"255,127,39")
    btle_change_colour(device,hand,255,127,39)
    btle_newline(device)
    hand = btle_text(device,"255,202,24")
    btle_change_colour(device,hand,255,202,24)
    hand = btle_text(device,"253,236,166")
    btle_change_colour(device,hand,253,236,166)
    hand = btle_text(device,"255,242,0")
    btle_change_colour(device,hand,255,242,0)
    hand = btle_text(device,"196,255,14")
    btle_change_colour(device,hand,196,255,14)
    btle_newline(device)
    hand = btle_text(device,"14,209,69")
    btle_change_colour(device,hand,14,209,69)
    hand = btle_text(device,"184,61,186")
    btle_change_colour(device,hand,184,61,186)
    hand = btle_text(device,"255,174,200")
    btle_change_colour(device,hand,255,174,200)
    hand = btle_text(device,"185,122,86")
    btle_change_colour(device,hand,185,122,86)


  elif event == BTLE_DISCONNECT:    
    # return(BTLE_EXIT) 
    pass
    
  return(BTLE_CONTINUE)

btle_server(onEvent,"Colours")

