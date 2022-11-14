#!/usr/bin/python3
from btle import *


# Declare handle storage names 
buthand = None
texthand = None
selhand = None
checkhand = None
broadhand = None
messhand = None

def onEvent(event,device,handle,member,text):
  global buthand
  global texthand
  global selhand
  global checkhand
  global broadhand
  global messhand
 
  if event == SERVER_START:
    # Called once on server start
    # Initialise handle storage
    buthand = btle_handles()
    texthand = btle_handles()
    selhand = btle_handles()
    checkhand = btle_handles()
    broadhand = btle_handles()
    messhand = btle_handles()
    
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts
    print(btle_name(device) + " Connect or restart")
    buthand[device] = btle_button(device,"OK")
    selhand[device] = btle_select(device,"Prompt,Member 0,Member 1,Member 2")
    btle_text(device,"Timer")
    checkhand[device] = btle_check(device,UNCHECKED)
    btle_newline(device)
    texthand[device] = btle_text_input(device,16)
    btle_newline(device)
    btle_text(device,"Tell Pi to...")
    btle_newline(device)
    broadhand[device] = btle_button(device,"OK")
    btle_text(device,"..broadcast to other Pis")
    btle_newline(device)
    messhand[device] = btle_button(device,"OK")
    btle_text(device,"..send message to other Androids")

    s = btle_local_name() + " connect or restart"
    btle_message(device,s)

  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked
    if(handle == buthand[device]):
      print(btle_name(device) + " OK clicked")
     
      s = btle_local_name() + " button"
      btle_message(device,s)

    if(handle == broadhand[device]):
      # Broadcast a message to other connected Pis
      print(btle_name(device) + " Broadcasting to other Pis")
      
      btle_broadcast("Hello")
      btle_message(device,"Message broadcast to other Pis")
           
    if(handle == messhand[device]):
      # Send a message to other connected Androids
      print(btle_name(device) + " Sending message to other Androids")
      btle_message_all("Hello all")
      btle_message(device,"Message sent to all Androids")
    
      
  elif event == BTLE_CLICK_CHECK:
    # Check box has been clicked
    if(handle == checkhand[device]):
      if member == UNCHECKED: 
        print(btle_name(device) + " Unchecked timer off")      
        s = btle_local_name() + " timer off"
        btle_message(device,s)
        btle_timer(0)
      else:
        print(btle_name(device) + " Checked timer on")
        s = btle_local_name() + " 3s timer on"
        btle_message(device,s)
        btle_timer(30)
 
  elif event == BTLE_CLICK_SELECT:
    # An member has been selected from a drop-down select
    if(handle == selhand[device]):
      print(btle_name(device) + "Member " + str(member) + " selected") 
      s = btle_local_name() + " select"
      btle_message(device,s)

  elif event == BTLE_CLICK_TEXT:
    # Text has been sent from text input box
    if(handle == texthand[device]):
      print("Text from " + btle_name(device) + " = " + text)
      
      s = btle_local_name() + " text received"
      btle_message(device,s)
  
  elif event == BTLE_BROADCAST:
    # Another Pi has broadcast a message
    print("Broadcast = " + text)
    
    s = btle_local_name() + " has received broadcast"
    btle_message(device,s)
    
  
  elif event == SERVER_TIMER:
    # Called at regular intervals if timer has been set 
    print("Timer tick")
    
    # Send message to all connected devices
    btle_message_all("Timer tick")
    
        
  elif event == BTLE_DISCONNECT:
    #return(BTLE_EXIT)  
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent

btle_server(onEvent,"Commentary")
