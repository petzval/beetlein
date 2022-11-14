#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);
void plot(int device);

// Declare handle storage names as integer pointers
int *ihand,*left,*right,*up,*down,*points;

int pointsflag[256];
float xmin[256],xmax[256],ymin[256],ymax[256];
float xx[128],yy[128];

int main()
  {
  btle_server(onEvent,"Plot");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n;
  double slope,flip,lasty;

  if(event == SERVER_START)
    {
    // Called once on server start
    // Initialise handle memory

    ihand = btle_handles();
    left = btle_handles();
    right = btle_handles();
    up = btle_handles();
    down = btle_handles();
    points = btle_handles();

    // calculate float data to be plotted
      
    lasty = 0;
    flip = -1;
    for(n = 0 ; n <= 50 ; ++n)
      {
      if((n % 8) == 0)
        flip = -flip; 
      slope = (4 - (n % 8)) * flip;
      xx[n] = n;
      yy[n] = lasty;
      lasty = yy[n] + slope;
      yy[n] *= 2 - 0.04*n;
      }
    }  
  else if(event == BTLE_CONNECT)
    {
    // Called when an Android device first connects or restarts
    xmin[device] = 0;
    xmax[device] = 50;
    ymin[device] = -20;
    ymax[device] = 20;
    pointsflag[device] = UNCHECKED;
    
    // set up an image area 600 pixels wide, 350 pixels height
    // scaled to a height on the screen of 6 lines
    // background colour = 230,230,230 = light grey  
    
    ihand[device] = btle_image(device,600,350,6,230,230,230);
    btle_newline(device);
  
    // buttons to shift plot and turn points on/off
    
    left[device] = btle_button(device," < ");
    right[device] = btle_button(device," > ");
    up[device] = btle_button(device,"Up");
    down[device] = btle_button(device,"Down");
    btle_text(device,"Points");
    points[device] = btle_check(device,pointsflag[device]);
 
    // draw the plot on the image area
    
    plot(device);     

    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    // Button has been clicked
    // shift plot
    if(handle == left[device])
      {
      xmin[device] += 5;
      xmax[device] += 5;
      }
    else if(handle == right[device])
      {
      xmin[device] -= 5;
      xmax[device] -= 5;
      }
    else if(handle == up[device])
      {
      ymin[device] -= 5;
      ymax[device] -= 5;
      }
    else if(handle == down[device])
      {
      ymin[device] += 5;
      ymax[device] += 5;
      }
      
    // re-draw the plot
      
    plot(device);

    }
  else if(event == BTLE_CLICK_CHECK)
    {
    // Check box has been clicked
    // turn points on/off
    if(handle == points[device])
      {
      pointsflag[device] = member;  // CHECKED or UNCHECKED
      plot(device);
      }

    }
  else if(event == BTLE_DISCONNECT)
    {
    // Called when an Android device disconnects
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }  // end onEvent
   
void plot(int device)
  {
  int n,end,pflag,handle;
  char s[32];
  int px[128],py[128];
  
 
  handle = ihand[device];
 
  btle_image_clear(device,handle);

    // x axis 500 pixels long, from origin at 80,270 to 580,270
  btle_image_line(device,handle,80,270,580,270,1,0,0,0);
    // y axis 240 pixels long from origin at 80,270 to 80,30
  btle_image_line(device,handle,80,30,80,270,1,0,0,0);
    // axis labels
  btle_image_text(device,handle,"Y axis label",25,200,DIRN_VERT,FONT_FIXED,20,0,0,0);
  btle_image_text(device,handle,"X axis label",150,330,DIRN_HORIZ,FONT_FIXED,20,0,0,0);
 
     // axis ticks and numbers
     
  for(n = 0 ; n <= 5 ; ++n)
    {
      // x tick
    btle_image_line(device,handle,100*n+80,270,100*n+80,280,1,0,0,0);
      // x tick number
    sprintf(s,"%d",(int)(xmin[device] + n*10));
    btle_image_text(device,handle,s,100*n+65,300,DIRN_HORIZ,FONT_FIXED,16,0,0,0);
    }
    
  for(n = 0 ; n <= 4 ; ++n)
    {  
      // y tick   
    btle_image_line(device,handle,70,60*n+30,80,60*n+30,1,0,0,0);
      // y tick number
    sprintf(s,"%d",(int)(ymin[device] + n*10));
    btle_image_text(device,handle,s,37,278-60*n,DIRN_HORIZ,FONT_FIXED,16,0,0,0);
    }   

    // scale xx[],yy[] float data [0]-[50] to image pixel coordinates px[],py[]
    // x,y axis float limits relative to xx,yy = xmin,xmax,ymin,ymax
    // Origin is at 80,270 and top right at 580,30 in image pixel coordinates
    // suppress points outside the plot area
    // size of px/py arrays = 128
    
  end = btle_scale_data(xx,yy,0,50,xmin[device],xmax[device],ymin[device],ymax[device],80,270,580,30,px,py,128);
  if(pointsflag[device] == UNCHECKED)
    pflag = POINTS_OFF;
  else
    pflag = POINTS_SQUARE;
    
    // send scaled data px,py returned by btle_scale_data to image
    // px py index = [0] to [end] returned by btle_scale_data
    // line width = 1 pixel
    // line colour = 10,150,0 = green
    // pflag sets points on or off, size of points = 2 pixels
    
  btle_image_multiline(device,handle,px,py,0,end,1,10,150,10,pflag,2);
  }


