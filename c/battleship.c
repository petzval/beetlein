#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);
int fillsea(int dn);
int addvessel(int dn,int size);
int randnum(int n);
void start(int device);
void lose(int device);

int *but[10][10];
int *pr,*play1,*play2,*mess;
int shots[256];
int hits[256];
int enemy[256];
int mode[256];
int waitingdevice;
int *sea[10][10];
char *type[6] = { "Missed","Submarine","Destroyer","Frigate","Cruiser","Battleship"};

int main()
  {
  struct  timespec ts;
  unsigned int seed;

    // random seed for rand()
  clock_gettime(CLOCK_REALTIME,&ts);
  seed = ts.tv_nsec;
  srand(seed);  
    
  btle_server(onEvent,"Battleship");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n,k,row,col,getout,val;
  char s[64];
  
  if(event == SERVER_START)
    {
    pr = btle_handles();
    play1 = btle_handles();
    play2 = btle_handles();
    mess = btle_handles();
     
    for(n = 0 ; n < 10 ; ++n)
      {
      for(k = 0 ; k < 10 ; ++k)
        {
        sea[n][k] = btle_handles();
        but[n][k] = btle_handles();
        }
      }
    for(n = 0 ; n < 256 ; ++n)
      mode[n] = 0;
    waitingdevice = 0;  // 2-player waiting   
    }
  else if(event == BTLE_CONNECT)
    {    
    if(device == waitingdevice)
      waitingdevice = 0;
    if((mode[device] & 12) != 0 && (mode[enemy[device]] & 12) != 0)  // 2 player
      {
      btle_change_text(enemy[device],pr[enemy[device]],"Enemy has surrendered");    
      mode[enemy[device]] &= 15;
      }  

    mode[device] = 0;
    enemy[device] = 0;
    play1[device] = btle_button(device,"1 player");
    play2[device] = btle_button(device,"2 player");
    mess[device] = btle_text(device,"Waiting for enemy to connect");
    btle_remove(device,mess[device]);
    btle_newline(device);
    btle_text(device,"You must sink: 1 Battleship (5 long)\n2 Cruisers (4) 3 Frigates (3)\n4 Destroyers (2) 5 Submarines (1)");
    }
  if(event == BTLE_CLICK_BUTTON)
    {
    if(mode[device] == 0)
      {
      if(handle == play1[device])
        {
        btle_message(device,"Wait...");
        mode[device] = 1 + 16;
        start(device);
        }
      else if(handle == play2[device])
        {
        if(waitingdevice == 0)   // first 2-player
          {
          btle_message(device,"Wait...");
          mode[device] = 4; 
          btle_restore(device,mess[device]);  // waiting message
          waitingdevice = device;
          }
        else     // there is a waiting enemy device
          {
          enemy[device] = waitingdevice;
          waitingdevice = 0;
          enemy[enemy[device]] = device;
          mode[device] = 8 + 16;  
          mode[enemy[device]] |= 16;  // 4+16

          btle_change_text(enemy[device],mess[enemy[device]],"Enemy connecting..");
          start(device);
          start(enemy[device]);
          }
        }
      return(BTLE_CONTINUE);
      }
    
    
    if((mode[device] & 16) == 0 || (mode[device] & 8) != 0)
      return(BTLE_CONTINUE);  // not started or enemy's turn - ignore button
      
    row = 0;
    col = 0;
    getout = 0;
    for(n = 0 ; n < 10 && getout == 0 ; ++n)
      {
      for(k = 0 ; k < 10 && getout == 0 ; ++k)
        {
        if(handle == but[n][k][device])
          {
          row = n;
          col = k;
          getout = 1;
          }
        }
      }
   
    val = sea[row][col][device];
    
    if(getout == 0 || val == 6)
      return(BTLE_CONTINUE);
    
    sea[row][col][device] = 6;
    --shots[device];
    if(val == 0)
      btle_change_colour(device,but[row][col][device],255,255,255);
    else
      {
      btle_change_colour(device,but[row][col][device],0,0,0);
      ++hits[device];
      }

    
    if(hits[device] == 35)  
      {
      btle_change_text(device,pr[device],"You win!");
      mode[device] &= 15;
      if((mode[device] & 4 ) != 0)
        lose(enemy[device]);
      }
    else if((mode[device] & 1) != 0 && shots[device] == 0)
      {
      lose(device);
      }
    else
      {
      if((mode[device] & 1) != 0)
        sprintf(s,"Shots %d  %s",shots[device],type[val]);
      else    
        {
        // prompt for enemy
        if(val == 0)
          sprintf(s,"Enemy missed. Hits %d/35",hits[device]);
        else 
          sprintf(s,"Enemy hit %s %d/35",type[val],hits[device]);
        btle_change_text(enemy[device],pr[enemy[device]],s);
        mode[enemy[device]] ^= 12;  // flip turn
        // prompt for local 
        sprintf(s,"%s",type[val]);
        mode[device] ^=  12;  // flip turn
        }
      btle_change_text(device,pr[device],s);
      }
      
    }
  else if(event == BTLE_DISCONNECT)
    {
    if(device == waitingdevice)
      waitingdevice = 0;
    if((mode[device] & 12) != 0 && (mode[enemy[device]] & 12) != 0)  // 2 player
      {
      btle_change_text(enemy[device],pr[enemy[device]],"Enemy has surrendered");    
      mode[enemy[device]] &= 15;
      }  
    }
     
  return(BTLE_CONTINUE);     
  }
  

void lose(int device)
  {
  int row,col,val;
  
  mode[device] &= 15;
  btle_change_text(device,pr[device],"You lose!");
  for(row = 0 ; row < 10 ; ++row)
    {
    for(col = 0 ; col < 10 ; ++col)
      {
      val = sea[row][col][device];
      if(val > 0 && val < 6)
        btle_change_colour(device,but[row][col][device],255,0,0);
      }
    }   
  }
  
void start(int device)
  {
  int n,k;
    
  btle_clear(device);
  shots[device] = 60;
  hits[device] = 0;
  while(fillsea(device) == 0)
    ;
           
  btle_spacings(device,11,0,3,3);
  btle_font(device,FONT_FIXED);
  if((mode[device] & 1) != 0)
    pr[device] = btle_text(device,"Shots 60");
  else if((mode[device] & 4) != 0)
    pr[device] = btle_text(device,"You shoot first");
  else
    pr[device] = btle_text(device,"Enemy shoots first");
    
  btle_newline(device);
  for(n = 0 ; n < 10 ; ++n)
    {
    for(k = 0 ; k < 10 ; ++k)
      but[n][k][device] = btle_button(device,"");
    if(n < 9)
      btle_newline(device);
    }
  }

int fillsea(int dn)
  {
  int n,k,retval,count,size;
  int max;
  
  max = 0;
  
  for(n = 0 ; n < 10 ; ++n)
    {
    for(k = 0 ; k < 10 ; ++k)
      sea[n][k][dn] = 0;
    }

  for(size = 5 ; size > 0 ; --size)
    {
    for(n = 0 ; n < 6-size ; ++n)
      {
      count = 0;
      retval = 0;
      while(retval == 0 && count < 50)
        {
        retval = addvessel(dn,size);
        ++count;
        }
      if(count > max)
        max = count;
      if(retval == 0)
        return(0);
      }
    }   
  return(1);
  }    
    
  
    

int addvessel(int dn,int size)
  {
  int row,col,dirn,dr,dc,j,rx,cx;
  static int drow[4] = { 1,-1,0,0 };
  static int dcol[4] = { 0,0,1,-1 };  
   
  row = randnum(10);
  col = randnum(10);
 
  dirn = randnum(4);
  dr = drow[dirn];
  dc = dcol[dirn];    
     
  for(j = 0 ; j < size ; ++j)
    {
    rx = row + j*dr;
    cx = col + j*dc;
    if(rx < 0 || rx > 9 || cx < 0 || cx > 9)
      return(0);
    if(sea[rx][cx][dn] != 0)
      return(0);
    ++rx;
    if(rx <= 9 && sea[rx][cx][dn] != 0)
      return(0);
    rx -= 2;
    if(rx >= 0 && sea[rx][cx][dn] != 0)
      return(0);
    ++rx;
    ++cx;
    if(cx <= 9 && sea[rx][cx][dn] != 0)
      return(0);
    cx -= 2;
    if(cx >= 0 && sea[rx][cx][dn] != 0)
      return(0);        
    }    
  
  for(j = 0 ; j < size ; ++j)
    {
    rx = row + j*dr;
    cx = col + j*dc;
    sea[rx][cx][dn] = size;
    }    
  
  
  return(1);    
  
  }

int randnum(int n)
  {
  int ret;
  
  ret = (int)(((double)rand()/(double)RAND_MAX)*(double)n);
  if(ret == n)
    ret = n-1;
  return(ret);
  }
