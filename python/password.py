#!/usr/bin/python3
from btle import *

def onEvent(event,device,handle,member,text):

  if event == SERVER_START:
    # Called once on server start
    print("*************")
    print("  HINT - enter password on Android = btle")
    print("*************")
    btle_password("btle")
    
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts
    # but only after correct password entered
    btle_text(device,"Password correct") 
    
  elif event == BTLE_DISCONNECT:
    # return(BTLE_EXIT)  
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Password")
