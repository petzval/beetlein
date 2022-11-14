#!/usr/bin/python3
from btle import *

# Declare global handle storage
ihand = None
left = None
right = None
up = None
down = None
points = None

# Set up other storage
xx = []
yy = []
xmin = [0.0 for n in range(256)]
xmax = [0.0 for n in range(256)]
ymin = [0.0 for n in range(256)]
ymax = [0.0 for n in range(256)]
pointsflag = [UNCHECKED for n in range(256)]

def onEvent(event,device,handle,member,text):
  global xx,yy,ihand,left,right,up,down,points
  global xmin,xmax,ymin,ymax,pointsflag
    
  if event == SERVER_START:
    # Set up handle storage
    ihand = btle_handles()
    left = btle_handles()
    right = btle_handles()
    up = btle_handles()
    down = btle_handles()
    points = btle_handles()

    # calculate float data
     
    lasty = 0
    flip = -1
    for n in range(51):
      if((n % 8) == 0):
        flip = -flip 
      slope = (4 - (n % 8)) * flip
      xx.append(n)
      yy.append(lasty)
      lasty = yy[n] + slope
      yy[n] = yy[n] * (2 - (0.04 * n))     

    return(BTLE_CONTINUE)

  elif event == BTLE_CONNECT:
    xmin[device] = 0
    xmax[device] = 50
    ymin[device] = -20
    ymax[device] = 20
    pointsflag[device] = UNCHECKED

    # set up an image area 600 pixels wide, 350 pixels height
    # scaled to a height on the screen of 6 lines
    # background colour = 230,230,230 = light grey  
    ihand[device] = btle_image(device,600,350,6,230,230,230)

    btle_newline(device)
  
    # buttons to shift plot and turn points on/off    

    left[device] = btle_button(device," < ")
    right[device] = btle_button(device," > ")
    up[device] = btle_button(device,"Up")
    down[device] = btle_button(device,"Down")
    btle_text(device,"Points")
    points[device] = btle_check(device,pointsflag[device])

    plot(device)
    return(BTLE_CONTINUE)

  elif event == BTLE_CLICK_BUTTON:
    # shift plot
    if(handle == left[device]):
      xmin[device] = xmin[device] + 5
      xmax[device] = xmax[device] + 5
    elif(handle == right[device]):
      xmin[device] = xmin[device] - 5
      xmax[device] = xmax[device] - 5
    elif(handle == up[device]):
      ymin[device] = ymin[device] - 5
      ymax[device] = ymax[device] - 5
    elif(handle == down[device]):
      ymin[device] = ymin[device] + 5
      ymax[device] = ymax[device] + 5

    plot(device)
    
    return(BTLE_CONTINUE)

  elif event == BTLE_CLICK_CHECK:
    # turn points on/off
    if(handle == points[device]):
      pointsflag[device] = member   # 1 CHECKED or 0 UNCHECKED
      plot(device)
    return(BTLE_CONTINUE) 
    
  elif event == BTLE_DISCONNECT:
    # return(BTLE_EXIT) 
    pass
    
  return(BTLE_CONTINUE)
  # end onEvent


def plot(device):
  global xx,yy,ihand,xmin,xmax,ymin,ymax,pointsflag
  
  handle = ihand[device]
  # clear existing image
  btle_image_clear(device,handle)
  # x axis 500 pixels long, from origin at 80,270 to 580,270
  btle_image_line(device,handle,80,270,580,270,1,0,0,0)
  # y axis 240 pixels long from origin at 80,270 to 80,30
  btle_image_line(device,handle,80,30,80,270,1,0,0,0)

  # axis labels
  btle_image_text(device,handle,"Y axis label",25,200,DIRN_VERT,FONT_FIXED,20,0,0,0)
  btle_image_text(device,handle,"X axis label",150,330,DIRN_HORIZ,FONT_FIXED,20,0,0,0)
 
  # axis ticks and numbers
     
  for n in range(6):
    # x tick
    btle_image_line(device,handle,100*n+80,270,100*n+80,280,1,0,0,0);
    # x tick number
    s = str(int(xmin[device] + n*10))
    btle_image_text(device,handle,s,100*n+65,300,DIRN_HORIZ,FONT_FIXED,16,0,0,0);

  for n in range(5):  
    # y tick   
    btle_image_line(device,handle,70,60*n+30,80,60*n+30,1,0,0,0);
    # y tick number
    s = str(int(ymin[device] + n*10))
    btle_image_text(device,handle,s,37,278-60*n,DIRN_HORIZ,FONT_FIXED,16,0,0,0);
       
  # scale xx,yy float data [0]-[50] to image area integer coordinates px,py
  # x,y axis float limits relative to xx,yy = xmin,xmax,ymin,ymax
  # origin is at image pixel coordinates 80,270
  # top right is at 580,30
  # length of the x axis is 500 pixels, and y axis 240
  # suppress points outside the 500x240 plot area
  # px and py must be empty lists
  # returns end = last px/py index, so px[0] to px[end] have been calculated
  # px,py and end must be passed to btle_image_multiline
    
  px = []
  py = []
  end = btle_scale_data(xx,yy,0,50,xmin[device],xmax[device],ymin[device],ymax[device],80,270,580,30,px,py)
   
  # send scaled data px,py and end returned by btle_scale_data to image
  # px py index = [0] to [end] returned by btle_scale_data
  # line width = 1 pixel
  # line colour = 10,150,10 = green
  # pflag sets points on or off, size of points = 2 pixels
  if pointsflag[device] == 0:
    pflag = POINTS_OFF
  else:
    pflag = POINTS_SQUARE  
  btle_image_multiline(device,handle,px,py,0,end,1,10,150,10,pflag,2)
  return
  # end plot() 

# ********** START *************

btle_server(onEvent,"Plot")

