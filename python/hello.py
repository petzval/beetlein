#!/usr/bin/python3
from btle import *

hellobut = None
worldbut = None
selecthand = None
checkhand = None
checktxt = None
txtinhand = None

def onEvent(event,device,handle,member,text):
  global hellobut
  global worldbut
  global selecthand
  global checkhand
  global checktxt
  global txtinhand
  
  if event == SERVER_START:
    # Called once on server start
    # Set up handle storage
    hellobut = btle_handles()
    worldbut = btle_handles()
    selecthand = btle_handles()
    checkhand = btle_handles()
    checktxt  = btle_handles()
    txtinhand = btle_handles()
            
  elif event == BTLE_CONNECT:
    # Called when Android device connects or restarts
    # Add items to Android screen and save handles
    btle_message(device,"Hello world message")
    btle_text(device,"Hello world text")
    btle_newline(device)
    hellobut[device] = btle_button(device,"Hello")
    worldbut[device] = btle_button(device,"World")
    btle_text(device,"Buttons")
    btle_newline(device)
    btle_text(device,"Check box")
    checkhand[device] = btle_check(device,UNCHECKED)
    checktxt[device] = btle_text(device,"Hello world")
    # remove Hello world text
    btle_remove(device,checktxt[device])
    btle_newline(device)
    btle_text(device,"Send a reply")
    txtinhand[device] = btle_text_input(device,20)
    btle_newline(device)
    btle_text(device,"Select a word")
    selecthand[device] = btle_select(device,"Select,Hello,World")
    
  elif event == BTLE_CLICK_BUTTON:
    # A button has been clicked
    if handle == hellobut[device]:
      print("Hello button clicked")
    elif(handle == worldbut[device]):
      print("World button clicked")   
 
  elif event == BTLE_CLICK_CHECK:
    # A check box has been clicked
    if handle == checkhand[device]:
      if(member == 0):
        print("Box unchecked")
        # remove hello world text
        btle_remove(device,checktxt[device])
      else:
        print("Box checked")
        # restore hello world text
        btle_restore(device,checktxt[device])
          
  elif event == BTLE_CLICK_SELECT:
    # A drop-down member has been selected
    if handle == selecthand[device]:
      if member == 0:
        print("Hello selected")
      elif member == 1:
        print("World selected")
     
  elif event == BTLE_CLICK_TEXT:
    # Text has been sent
    if handle == txtinhand[device]:
      print("Reply = " + text)
    
  elif event == BTLE_DISCONNECT:
    # Android has disconnected
    # return(BTLE_EXIT)  # to exit server 
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent
   
# ***** program START ******

btle_server(onEvent,"Hello")

