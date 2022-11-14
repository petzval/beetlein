#!/usr/bin/python3
from btle import *

prompt = None
start  = None
stop = None
count = None
stopstart = None

def onEvent(event,device,handle,member,text):
  global prompt
  global start
  global stop
  global count
  global stopstart

  if event == SERVER_START:
    # Called once on server start

    prompt = btle_handles()
    start = btle_handles()
    stop = btle_handles()
    
    count = [0 for n in range(256)]
    stopstart = [0 for n in range(256)]
 
  elif event == BTLE_CONNECT:
    # Called when an Android device connects or restarts

    count[device] = 0
    stopstart[device] = 0
    
    prompt[device] = btle_text(device,"Count = 0")
    btle_newline(device)
    start[device] = btle_button(device,"Start")
    btle_change_colour(device,start[device],160,220,160) # green
    stop[device] = btle_button(device,"Stop")    
    btle_change_colour(device,stop[device],120,120,120) # grey
    btle_timer(10)  # 1 second timer
  
  elif event == BTLE_CLICK_BUTTON:
    # Button has been clicked

    if(handle == start[device]):
      stopstart[device] = 1
      btle_change_colour(device,stop[device],160,220,160)
      btle_change_colour(device,start[device],150,150,150)
    if(handle == stop[device]):
      stopstart[device] = 0
      btle_change_colour(device,start[device],160,220,160)
      btle_change_colour(device,stop[device],150,150,150)
            
  elif event == SERVER_TIMER:
    # Called at regular intervals if timer has been 
    # set via btle_timer(ds) where ds is the interval
    # in deci-seconds. So btle_timer(10) is once per second
    for n in range(1,btle_maxdevice() + 1):
      if(btle_connected(n) == 1 and stopstart[n] == 1):
        count[n] = count[n] + 1
        s = "Count = " + str(count[n])
        btle_change_text(n,prompt[n],s)
  
  elif event == BTLE_DISCONNECT:
    # Called when an Android device disconnects
    #return(BTLE_EXIT) 
    pass   
   
  return(BTLE_CONTINUE)

####### START #######

btle_server(onEvent,"Counter")



