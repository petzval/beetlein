#!/usr/bin/python3
from btle import *

buthand = None
texthand = None
selhand = None
checkhand = None
broadhand = None


def onEvent(event,device,handle,member,text):
  global buthand
  global texthand 
  global selhand 
  global checkhand 
  global broadhand 
 
  if event == SERVER_START:
    # Called once on server start
    # Initialise handle storage 
    buthand = btle_handles()
    texthand = btle_handles()
    selhand = btle_handles()
    checkhand = btle_handles()
    broadhand = btle_handles()
        
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts
    # The Master and all slaves must have this design
    buthand[device] = btle_button(device,"OK")
    selhand[device] = btle_select(device,"Select,Zero,One,Two")
    checkhand[device] = btle_check(device,UNCHECKED)
    btle_newline(device)
    texthand[device] = btle_text_input(device,16)
    btle_newline(device)
    btle_text(device,"Broadcast from Pi to slaves")
    broadhand[device] = btle_button(device,"OK")
 
  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked
    if(handle == buthand[device]):
      print("OK clicked")
    elif(handle == broadhand[device]):
      btle_broadcast("Hello")
   
  elif event == BTLE_CLICK_CHECK:
    # Check box has been clicked
    if(handle == checkhand[device]):
      if member == UNCHECKED: 
        print("Unchecked")
      else:
        print("Checked") 
      
   
  elif event == BTLE_CLICK_SELECT:
    # A member has been selected from a drop-down select
    if(handle == selhand[device]):
      print("Member " + str(member) + " selected")    
  
  elif event == BTLE_CLICK_TEXT:
    # Text has been sent from a text input box
    if(handle == texthand[device]):
      print("Text sent = " + text)
 
  elif event == BTLE_BROADCAST:
    print("Got broadcast = " + text)
    
  elif event == BTLE_DISCONNECT:
    # return(BTLE_EXIT)  
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Master")
  

