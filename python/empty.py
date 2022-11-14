#!/usr/bin/python3
from btle import *

# Declare global handle storage names 
# texthand = None
# buthand = None
# checkhand = None
# selhand = None
# txtinhand = None
# newhand = None
# imagehand = None

def onEvent(event,device,handle,member,text):
  # global texthand 
  # global buthand
  # global checkhand
  # global selhand 
  # global txtinhand
  # global newhand
  # global imagehand

  if event == SERVER_START:
    # Called once on server start
    #   device = invalid
    #   handle = invalid
    #   member = invalid
    #     text = invalid
    # Initialise handle storage
    #   texthand = btle_handles()
    #   buthand = btle_handles()
    #   checkhand = btle_handles()
    #   selhand = btle_handles()
    #   txtinhand = btle_handles()
    #   newhand = btle_handles()
    #   imagehand = btle_handles()
    # Call these two here if required
    #   btle_password("password")
    #   btle_slave()
    pass
    
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts
    #   device = identifies Android device (1-254)
    #   handle = invalid
    #   member = invlaid
    #     text = Invalid
    # Add items to Android screen and store handles if needed
    #   texthand[device] = btle_text(device,"Hello")
    #   buthand[device] = btle_button(device,"OK")
    #   checkhand[device] = btle_check(device,UNCHECKED)
    #   selhand[device] = btle_select(device,"Prompt,Member 0,Member 1,Member 2")
    #   txtinhand[device] = btle_text_input(device,8)
    #   newhand[device] = btle_newline(device)
    #   imagehand[device] = btle_image(device,400,200,4,220,220,220)
    # Send a message to scrollable message area
    #   btle_message(device,"Hello")
    pass

  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked
    #   device = identifies Android device
    #   handle = identifies button item
    #   member = invalid
    #     text = invalid
    # Deal with button click
    #   if handle == buthand[device]:
    #     print("Button clicked")  
    pass
   
  elif event == BTLE_CLICK_CHECK:
    # Check box has been clicked
    #   device = identifies Android device
    #   handle = identifies check box item
    #   member = UNCHECKED or CHECKED
    #     text = invalid
    # Deal with check click
    #   if handle == checkhand[device]:
    #     if member == UNCHECKED: 
    #       print("Unchecked")
    #     elif member == CHECKED:
    #       print("Checked")
    pass
     
  elif event == BTLE_CLICK_SELECT:
    # A member has been selected from a drop-down select
    #   device = identifies Android device
    #   handle = identifies select item
    #   member = index of selection (0 to number of members-1)
    #     text = invalid
    # Deal with selection 
    #   if handle == selhand[device]:
    #     print("Member " + str(member) + " selected")    
    pass   
  elif event == BTLE_CLICK_TEXT:
    # Text has been sent from a text input box
    #   device = identifies Android device
    #   handle = identifies text input item
    #   member = invalid
    #     text = text sent
    # Deal with text 
    # if handle == txtinhand[device]:
    #   print("Text sent = " + text)
    pass

  elif event == BTLE_BROADCAST:
    # Another Pi has broadcast a message to all other Pis
    #   device = identifies Android device that distributed the message
    #   handle = invalid
    #   member = invalid
    #     text = message text 
    # Deal with message 
    #   print("Message from another Pi = " + text)   
    pass  

  elif event == SERVER_TIMER:
    # Called at regular intervals if timer has been 
    # set via btle_timer(ds) where ds is the interval
    # in deci-seconds. So btle_timer(10) is once per second
    # Not associated with any particular Android device
    #   device = invalid
    #   handle = invalid
    #   member = invalid
    #     text = invalid
    # Deal with timer tick 
    #   print("Timer tick")
    # To send any instructions to a device here you must know
    # the device number because the device parameter is invalid
    # To identify all connected devices:
    #   for n in range(1,btle_maxdevice()+1):
    #     if btle_connected(n) == 1:
    #       pass # device n is connected
    pass
  
  elif event == BTLE_DISCONNECT:
    # Called when an Android device disconnects
    #   device = identifies Android device
    #   handle = invalid
    #   member = invalid
    #     text = invalid
    # Do not call any more btle_ instructions for device
    # return(BTLE_EXIT)      to exit from server
    # return(BTLE_CONTINUE)  to continue dealing with other
    #     connected devices, and/or wait for new connections
    pass
   
  return(BTLE_CONTINUE)
  # end onEvent
  
# ******** program START **********

btle_server(onEvent,"Empty")


