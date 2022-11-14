#!/usr/bin/python3
from btle import *

class keys:
  def __init__(self):
    self.display = btle_handles()
    self.one = btle_handles()
    self.two = btle_handles()
    self.three = btle_handles()
    self.four  = btle_handles()
    self.five  = btle_handles()
    self.six   = btle_handles()
    self.seven = btle_handles()
    self.eight = btle_handles()
    self.nine  = btle_handles()
    self.zero  = btle_handles()
    self.add = btle_handles()
    self.subtract = btle_handles()
    self.multiply = btle_handles()
    self.divide = btle_handles()
    self.clear  = btle_handles()
    self.delete = btle_handles()
    self.equals = btle_handles()
    self.point = btle_handles()

class devs:
  def __init__(self):
    self.op = 0
    self.value = 0.0
    self.vals = []
    for n in range(15):
      self.vals.append(' ')


def onEvent(event,device,handle,member,text):
  global key
  global dev
  
  if event == BTLE_CONNECT:

    dev[device].op = 0
    dev[device].value = 0.0
    for n in range(15):
      dev[device].vals[n] = ' '
      
    btle_font(device,FONT_FIXED)
    valstr = ''.join(str(e) for e in dev[device].vals)  
    key.display[device] = btle_text(device,valstr)
    btle_change_colour(device,key.display[device],160,220,160)

    btle_newline(device)
    key.one[device] = btle_button(device," 1 ")
    key.two[device] = btle_button(device," 2 ")
    key.three[device] = btle_button(device," 3 ")
    key.add[device] = btle_button(device," + ")
    btle_change_colour(device,key.add[device],0,170,245)
    btle_newline(device) 
    key.four[device] = btle_button(device," 4 ")
    key.five[device] = btle_button(device," 5 ")
    key.six[device] = btle_button(device," 6 ")
    key.subtract[device] = btle_button(device," - ")
    btle_change_colour(device,key.subtract[device],0,170,245)
    btle_newline(device)
    key.seven[device] = btle_button(device," 7 ")
    key.eight[device] = btle_button(device," 8 ")
    key.nine[device] = btle_button(device," 9 ")
    key.multiply[device] = btle_button(device," x ")
    btle_change_colour(device,key.multiply[device],0,170,245)
    btle_newline(device)
    key.zero[device] = btle_button(device," 0 ")
    key.point[device] = btle_button(device," . ")
    key.equals[device] = btle_button(device," = ")
    btle_change_colour(device,key.equals[device],0,170,245)
    key.divide[device] = btle_button(device," / ")
    btle_change_colour(device,key.divide[device],0,170,245)
    btle_newline(device)
    key.clear[device] = btle_button(device," C ")
    btle_change_colour(device,key.clear[device],255,120,120)
    key.delete[device] = btle_button(device," < ")

  elif event == BTLE_CLICK_BUTTON:
    dhand = key.display[device]
    
    if(dev[device].op == 6):    # z
      addvals(device,dhand,"C")
      dev[device].op = 0

    if(handle == key.point[device]):
      for n in range(15):
        if(dev[device].vals[n] == '.'):
          return(BTLE_CONTINUE)
      
    if(handle == key.add[device]):
      newop = 1  #'+'
    elif(handle == key.subtract[device]):
      newop = 2 # '-'
    elif(handle == key.multiply[device]):
      newop = 3 # 'x'
    elif(handle == key.divide[device]):
      newop = 4 # '/'
    elif(handle == key.equals[device]):
      newop = 5  #'='
    else: 
      newop = 0

    leadminus = 0
    if(newop == 2):   #'-'
      if( (dev[device].op & 128) != 0 or (dev[device].op == 0 and dev[device].vals[0] == ' ')):
        leadminus = 1
        newop = 0
    
    if(dev[device].op == 0):
      if(newop == 5):   # '='
        return(BTLE_CONTINUE)
      if(dev[device].vals[0] == ' ' and (newop == 1 or  newop == 3 or newop == 4)):  # + * /
        return(BTLE_CONTINUE)

    if((dev[device].op & 128) != 0):
      if(newop == 1 or newop == 3 or newop == 4 or newop == 5):   # + * / =  
        return(BTLE_CONTINUE)
      addvals(device,dhand,"C")   

    if(handle == key.one[device]):
      addvals(device,dhand,"1")
    elif(handle == key.two[device]):
      addvals(device,dhand,"2")
    elif(handle == key.three[device]):
      addvals(device,dhand,"3")
    elif(handle == key.four[device]):
      addvals(device,dhand,"4")
    elif(handle == key.five[device]):
      addvals(device,dhand,"5")
    elif(handle == key.six[device]):
      addvals(device,dhand,"6")
    elif(handle == key.seven[device]):
      addvals(device,dhand,"7")
    elif(handle == key.eight[device]):
      addvals(device,dhand,"8")
    elif(handle == key.nine[device]):
      addvals(device,dhand,"9")
    elif(handle == key.zero[device]):
      addvals(device,dhand,"0")
    elif(handle == key.point[device]):
      addvals(device,dhand,".")
    elif(leadminus != 0): 
      addvals(device,dhand,"-")
    elif(handle == key.delete[device]):
      addvals(device,dhand,"<")
    elif(handle == key.clear[device]):
      addvals(device,dhand,"C")
      dev[device].value = 0
      dev[device].op = 0
      
    dev[device].op = dev[device].op & 127
    
    if(newop == 0):
      return(BTLE_CONTINUE)       

    valstr = ''.join(str(e) for e in dev[device].vals)          
    newvalue = float(valstr)
          
    if(dev[device].op == 0):
      dev[device].value = newvalue
    elif(dev[device].op == 1):   #'+'):
      dev[device].value = dev[device].value + newvalue
    elif(dev[device].op == 2):   # '-'):
      dev[device].value = dev[device].value - newvalue
    elif(dev[device].op == 3):   #'x'):
      dev[device].value = dev[device].value * newvalue
    elif(dev[device].op == 4):   #'/'):
      if(newvalue != 0):
        dev[device].value = dev[device].value / newvalue
      else:
        for n in range(15):
          dev[device].vals[n] = ' '
        addvals(device,dhand,"Divide by zero")
        dev[device].value = 0
        dev[device].op= 6   #'z'
        return(BTLE_CONTINUE)
        
    for n in range(15):
      dev[device].vals[n] = ' '
    s = '{:g}'.format(dev[device].value)

    addvals(device,dhand,s)

    if(newop == 5):   # '='
      dev[device].op = 0
    else:
      if newop == 1:
        s = " +"
      elif newop == 2:
        s = " -"
      elif newop == 3:
        s = " x"
      else:
        s = " /"
             
      addvals(device,dhand,s)      
      dev[device].op = newop + 128

  elif event == BTLE_DISCONNECT:
    # Android has disconnected
    # return(BTLE_EXIT) 
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent



def addvals(device,handle,s):
  global dev
   
  if(s[0] == 'C' or (dev[device].op & 128) != 0):
    dev[device].op = dev[device].op & 127
    for n in range(15):
      dev[device].vals[n] = ' '
    
  if(s[0] != 'C'):
    if s[0] == '.':
      for n in range(0,15):
        if(dev[device].vals[n] == '.'):
          return
          
    n = 0
    while(dev[device].vals[n] != ' ' and n < 15):
      n = n + 1
    if(s[0] == '<'):
      if(n == 0):
        return
      dev[device].vals[n-1] = ' '
    else:
      if(n == 15):
        return
      k = 0
      while(k < len(s) and n+k < 15):
        dev[device].vals[n+k] = s[k]
        k = k + 1
    
  btle_change_text(device,handle,dev[device].vals)
  return
  # end addvals
      
######## code start #########
  
key = keys()
dev = []
for n in range(256):
  dev.append(devs())
 
btle_server(onEvent,"Calculator")
