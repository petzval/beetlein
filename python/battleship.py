#!/usr/bin/python3
from btle import *
from random import randint

pr = None
play1 = None
play2 = None
mess = None
waitingdevice = 0
sea = None
but = None
shots = None
hits = None
mode = None
enemy = None
type = [" Missed"," Submarine"," Destroyer"," Frigate"," Cruiser"," Battleship"]

def onEvent(event,device,handle,member,text):
  global sea,but,pr,play1,play2,mess,shots
  global hits,type,mode,enemy,waitingdevice
      
  if event == SERVER_START:
    pr = btle_handles()
    play1 = btle_handles()
    play2 = btle_handles()
    mess = btle_handles()
     
    for n in range(10):
      for k in range(10):
        sea[n][k] = btle_handles()
        but[n][k] = btle_handles()

    for n in range(256):
      mode[n] = 0
    waitingdevice = 0 # 2-player waiting   

  
  if event == BTLE_CONNECT:
    if(device == waitingdevice):
      waitingdevice = 0
    if (mode[device] & 12) != 0 and (mode[enemy[device]] & 12) != 0:  
      btle_change_text(enemy[device],pr[enemy[device]],"Enemy has surrendered")    
      mode[enemy[device]] = mode[enemy[device]] & 15       

    mode[device] = 0
    enemy[device] = 0
    play1[device] = btle_button(device,"1 player")
    play2[device] = btle_button(device,"2 player")
    mess[device] = btle_text(device,"Waiting for enemy to connect")
    btle_remove(device,mess[device])
    btle_newline(device)
    btle_text(device,"You must sink: 1 Battleship (5 long)" + chr(10) +
                       "Cruisers (4) 3 Frigates (3)" + chr(10) + 
                       "Destroyers (2) 5 Submarines (1)")
    # end CONNECT
  elif event == BTLE_CLICK_BUTTON:
    if(mode[device] == 0):
      if(handle == play1[device]):
        btle_message(device,"Wait...")
        mode[device] = 1 + 16
        start(device)
      elif(handle == play2[device]):
        if(waitingdevice == 0):   # first 2-player
          btle_message(device,"Wait...")
          mode[device] = 4 
          btle_restore(device,mess[device]) # waiting message
          waitingdevice = device
        else:     # there is a waiting enemy device
          enemy[device] = waitingdevice
          waitingdevice = 0
          enemy[enemy[device]] = device
          mode[device] = 8 + 16  
          mode[enemy[device]] |= 16  # 4+16

          btle_change_text(enemy[device],mess[enemy[device]],"Enemy connecting..")
          start(device)
          start(enemy[device])
      return(BTLE_CONTINUE)
    
    
    if((mode[device] & 16) == 0 or (mode[device] & 8) != 0):
      return(BTLE_CONTINUE)  # not started or enemy's turn - ignore button
      

    row = 0
    col = 0
    getout = 0
    for n in range(10):     # && getout == 0  ++n)
      for k in range(10):    # && getout == 0  ++k)
        if(handle == but[n][k][device]):
          row = n
          col = k
          getout = 1    
    
    
    val = sea[row][col][device]
    if(getout == 0 or val == 6):
      return(BTLE_CONTINUE)

    sea[row][col][device] = 6
    shots[device] = shots[device] - 1
    if(val == 0):
       btle_change_colour(device,but[row][col][device],255,255,255)
    else:
      btle_change_colour(device,but[row][col][device],0,0,0)
      hits[device] = hits[device] + 1
  
    if(hits[device] == 35):  
      btle_change_text(device,pr[device],"You win!")
      mode[device] = mode[device] & 15
      if((mode[device] & 4 ) != 0):
        lose(enemy[device])
    elif((mode[device] & 1) != 0 and shots[device] == 0):
      lose(device)  
    else:
      if((mode[device] & 1) != 0):
        s = "Shots " + str(shots[device]) + type[val] 
      else:    
        # prompt for enemy
        if(val == 0):
          s = "Enemy missed. Hits " + str(hits[device]) + "/35"
        else:
          s = "Enemy hit " + type[val] + " " + str(hits[device]) + "/35"
        btle_change_text(enemy[device],pr[enemy[device]],s)
        mode[enemy[device]] = mode[enemy[device]] ^ 12  # flip turn
        # prompt for local 
        s = type[val]
        mode[device] = mode[device] ^ 12 # flip turn
      btle_change_text(device,pr[device],s)
    # end BUTTON
    
  elif event == BTLE_DISCONNECT:
    if device == waitingdevice:
      waitingdevice = 0
    if (mode[device] & 12) != 0 and (mode[enemy[device]] & 12) != 0:  
      btle_change_text(enemy[device],pr[enemy[device]],"Enemy has surrendered")    
      mode[enemy[device]] = mode[enemy[device]] & 15       
    # end DISCONNECT
   
  return(BTLE_CONTINUE)
  # end onEvent



def lose(device):
  global mode
  global pr
  global but
  global sea
  
  mode[device] = mode[device] & 15
  btle_change_text(device,pr[device],"You lose!")
  for row in range(10):
    for col in range(10):
      val = sea[row][col][device]
      if(val > 0 and val < 6):
        btle_change_colour(device,but[row][col][device],255,0,0)
  return  
  # end lose    
 
  
def start(device):
  global shots
  global hits
  global sea
  global but
      
  btle_clear(device)
  shots[device] = 60
  hits[device] = 0
  while(fillsea(device) == 0):
    n = 0    
          
  btle_spacings(device,11,0,3,3)
  btle_font(device,FONT_FIXED)
  if((mode[device] & 1) != 0):
    pr[device] = btle_text(device,"Shots 60")
  elif((mode[device] & 4) != 0):
    pr[device] = btle_text(device,"You shoot first")
  else:
    pr[device] = btle_text(device,"Enemy shoots first")
    
  btle_newline(device)
  for n in range(10):
    for k in range(10):
      but[n][k][device] = btle_button(device,"")
      
    if(n < 9):
      btle_newline(device)
  return
  # end start 

  
def fillsea(dn):
  global sea
      
  for n in range(10):
    for k in range(10):
      sea[n][k][dn] = 0
    
  for n in range(5):
    size = 5 - n
    for n in range(n+1):
      count = 0
      retval = 0
      while(retval == 0 and count < 50):
        retval = addvessel(dn,size)
        count = count + 1
 
      if(retval == 0):
        return(0)
     
  return(1)
  # enf fillsea    
   

def addvessel(dn,size):
  global sea
  
  drow = [1,-1,0,0]
  dcol = [0,0,1,-1]  
       
  row = randint(0,9)
  col = randint(0,9) 
  dirn = randint(0,3)
  dr = drow[dirn]
  dc = dcol[dirn] 
  
         
  for j in range(size):
    rx = (j*dr) + row
    cx = (j*dc) + col
    if(rx < 0 or rx > 9 or cx < 0 or cx > 9):
      return(0)
    if(sea[rx][cx][dn] != 0):
      return(0)
    rx = rx + 1
    if(rx <= 9 and sea[rx][cx][dn] != 0):
      return(0)
    rx = rx - 2
    if(rx >= 0 and sea[rx][cx][dn] != 0):
      return(0)
    rx = rx + 1
    cx = cx + 1
    if(cx <= 9 and sea[rx][cx][dn] != 0):
      return(0)
    cx = cx - 2
    if(cx >= 0 and sea[rx][cx][dn] != 0):
      return(0)        
       
  for j in range(size):
    rx =  (j*dr) + row
    cx =  (j*dc) + col
    sea[rx][cx][dn] = size
       
  return(1)    
  # end addvessel
  
######### START ################

sea = [[None] * 10 for i in range(10)]
but = [[None] * 10 for i in range(10)]
shots = [0 for i in range(256)]
hits = [0 for i in range(256)]
mode = [0 for i in range(256)]
enemy = [0 for i in range(256)]

btle_server(onEvent,"Battleship")

