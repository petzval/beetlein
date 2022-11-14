#!/usr/bin/python3
from btle import *

# Declare global handle storage names 
hpup = None
hpdown = None
vpup = None
vpdown = None
hsup = None
hsdown = None
vsup = None
vsdown = None
pr = None

hpad = [5 for n in range(256)]
vpad = [5 for n in range(256)]
hspace = [5 for n in range(256)]
vspace = [5 for n in range(256)]

def onEvent(event,device,handle,member,text):
  global hpup
  global hpdown
  global vpup
  global vpdown
  global hsup
  global hsdown
  global vsup
  global vsdown
  global pr
  global hpad
  global vpad
  global hspace
  global vspace

  if event == SERVER_START:
    # Called once on server start
    hpup = btle_handles()
    hpdown = btle_handles()
    vpup = btle_handles()
    vpdown = btle_handles()
    hsup = btle_handles()
    hsdown = btle_handles()
    vsup = btle_handles()
    vsdown = btle_handles()
    pr = btle_handles() 

  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts
    hpad[device] = 5
    vpad[device] = 5
    hspace[device] = 5
    vspace[device] = 5    
    pr[device] = btle_text(device,"Defaults Hpad=5 Vpad=5 Hspace=5 Vspace=5")
    btle_newline(device)
    hpup[device] = btle_button(device,"Hpad +")    
    hpdown[device] = btle_button(device,"Hpad -")    
    vpup[device] = btle_button(device,"Vpad +")    
    vpdown[device] = btle_button(device,"Vpad -")    
    btle_newline(device)
    hsup[device] = btle_button(device,"Hspc +")    
    hsdown[device] = btle_button(device,"Hspc -")    
    vsup[device] = btle_button(device,"Vspc +")    
    vsdown[device] = btle_button(device,"Vspc -") 
    btle_newline(device)  
    btle_text(device,"Text")
    btle_select(device,"Select,Zero,One,Two")
    btle_text_input(device,6)   

    
  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked
    if(handle == hpup[device] and hpad[device] < 20):
      hpad[device] = hpad[device] + 1
    elif(handle == hpdown[device] and hpad[device] > 0):
      hpad[device] = hpad[device] - 1
    if(handle == vpup[device] and vpad[device] < 20):
      vpad[device] = vpad[device] + 1
    elif(handle == vpdown[device] and vpad[device] > 0):
      vpad[device] = vpad[device] - 1

    if(handle == hsup[device] and hspace[device] < 20):
      hspace[device] = hspace[device] + 1
    elif(handle == hsdown[device] and hspace[device] > 0):
      hspace[device] = hspace[device] - 1
    if(handle == vsup[device] and vspace[device] < 20):
      vspace[device] = vspace[device] + 1
    elif(handle == vsdown[device] and vspace[device] > 0):
      vspace[device] = vspace[device] - 1
    
    s = "Hpad=" + str(hpad[device]) + " Vpad=" + str(vpad[device]) + " Hspace=" + str(hspace[device]) + " Vspace=" + str(vspace[device])
    btle_change_text(device,pr[device],s) 
    btle_spacings(device,hpad[device],vpad[device],hspace[device],vspace[device])
 
  elif event == BTLE_DISCONNECT:
    # Called when an Android device disconnects
    # return(BTLE_EXIT) 
    pass  
   
  return(BTLE_CONTINUE)
  
# ***** program START ******  
  
btle_server(onEvent,"Spacings")



