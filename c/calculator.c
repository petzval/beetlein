#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);
void addvals(int device,int hand,char *s);

char vals[256][16];
double value[256]; 
char op[256];

int main()
  {
  btle_server(onEvent,"Calculator");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n,k,dhand,newop,zflag,leadminus;
  static double result;
  double newvalue;
  char s[32],ops[4];
  
  static int *display,*one,*two,*three,*four,*five,*six,*seven,*eight,*nine,*zero;
  static int *add,*subtract,*multiply,*divide,*clear,*equals,*del,*point;
  
  
  if(event == SERVER_START)
    {
    display = btle_handles();
    one = btle_handles();
    two = btle_handles();
    three = btle_handles();
    four  = btle_handles();
    five  = btle_handles();
    six   = btle_handles();
    seven = btle_handles();
    eight = btle_handles();
    nine  = btle_handles();
    zero  = btle_handles();
    add = btle_handles();
    subtract = btle_handles();
    multiply = btle_handles();
    divide = btle_handles();
    clear  = btle_handles();
    del = btle_handles();
    equals = btle_handles();
    point = btle_handles();
    for(k = 0 ; k < 256 ; ++k)
      {
      for(n = 0 ; n < 15 ; ++n)
        vals[k][n] = ' ';
      vals[k][15] = 0;
      value[k] = 0;
      op[k] = 0;
      }  
    }
  if(event == BTLE_CONNECT)
    {
    for(n = 0 ; n < 15 ; ++n)
      vals[device][n] = ' ';
    vals[device][15] = 0;
    value[device] = 0;
    op[device] = 0;
  
    btle_font(device,FONT_FIXED);

    display[device] = btle_text(device,vals[device]);
    btle_change_colour(device,display[device],160,220,160);
    
    btle_newline(device);
    one[device] = btle_button(device," 1 ");
    two[device] = btle_button(device," 2 ");
    three[device] = btle_button(device," 3 ");

    add[device] = btle_button(device," + ");
    btle_change_colour(device,add[device],0,170,245);

    btle_newline(device); 
    four[device] = btle_button(device," 4 ");
    five[device] = btle_button(device," 5 ");
    six[device] = btle_button(device," 6 ");

    subtract[device] = btle_button(device," - ");
    btle_change_colour(device,subtract[device],0,170,245);
 
    btle_newline(device);
    seven[device] = btle_button(device," 7 ");
    eight[device] = btle_button(device," 8 ");
    nine[device] = btle_button(device," 9 ");

    multiply[device] = btle_button(device," x ");
    btle_change_colour(device,multiply[device],0,170,245);

   
    btle_newline(device);
    zero[device] = btle_button(device," 0 ");
    point[device] = btle_button(device," . ");

    equals[device] = btle_button(device," = ");
    btle_change_colour(device,equals[device],0,170,245);
    divide[device] = btle_button(device," / ");
    btle_change_colour(device,divide[device],0,170,245);
 
    btle_newline(device);

    clear[device] = btle_button(device," C ");
    btle_change_colour(device,clear[device],255,120,120);

    del[device] = btle_button(device," < ");
    }
  if(event == BTLE_CLICK_BUTTON)
    {
    dhand = display[device];
    
    if(op[device] == 'z')
      {
      addvals(device,dhand,"C");
      op[device] = 0;
      }    

    if(handle == point[device])
      {
      for(n = 0 ; n < 15 ; ++n)
        {
        if(vals[device][n] == '.')
          return(BTLE_CONTINUE);
        }
      }
      
    if(handle == add[device])
      newop= '+';
    else if(handle == subtract[device])
      newop = '-';
    else if(handle == multiply[device])
      newop = 'x';
    else if(handle == divide[device])
      newop = '/';
    else if(handle == equals[device])
      newop = '=';
    else 
      newop = 0;

    leadminus = 0;
    if(newop == '-')
      {
      if( (op[device] & 128) != 0 || (op[device] == 0 && vals[device][0] == ' '))
        {
        leadminus = 1;
        newop = 0;
        }
      }  
    
    if(op[device] == 0)
      {
      if(newop == '=')
        return(BTLE_CONTINUE);
      if(vals[device][0] == ' ' && (newop == '+' ||
          newop == 'x' || newop == '/'))
        return(BTLE_CONTINUE);
      }

    if((op[device] & 128) != 0)
      {
      if(newop == '+' || newop == 'x' || newop == '/' || newop == '=')  
        return(BTLE_CONTINUE);
      addvals(device,dhand,"C");
      }     

    if(handle == one[device])
      addvals(device,dhand,"1");
    else if(handle == two[device])
      addvals(device,dhand,"2");
    else if(handle == three[device])
      addvals(device,dhand,"3");
    else if(handle == four[device])
      addvals(device,dhand,"4");
    else if(handle == five[device])
      addvals(device,dhand,"5");
    else if(handle == six[device])
      addvals(device,dhand,"6");
    else if(handle == seven[device])
      addvals(device,dhand,"7");
    else if(handle == eight[device])
      addvals(device,dhand,"8");
    else if(handle == nine[device])
      addvals(device,dhand,"9");
    else if(handle == zero[device])
      addvals(device,dhand,"0");
    else if(handle == point[device])
      addvals(device,dhand,".");
    else if(leadminus != 0) 
      addvals(device,dhand,"-");
    else if(handle == del[device])
      addvals(device,dhand,"<");
    else if(handle == clear[device])
      {
      addvals(device,dhand,"C");
      value[device] = 0;
      op[device] = 0;
      }
   
    op[device] &= 127;
    
    if(newop == 0)
      return(BTLE_CONTINUE);       
          
    newvalue = atof(vals[device]);
          
    if(op[device] == 0)
      value[device] = newvalue;
    else if(op[device] == '+')
      value[device] += newvalue;
    else if(op[device] == '-')
      value[device] -= newvalue;
    else if(op[device] == 'x')
      value[device] *= newvalue;
    else if(op[device] == '/')
      {
      if(newvalue != 0)
        value[device] /= newvalue;
      else
        {
        for(n = 0 ; n < 15 ; ++n)
          vals[device][n] = ' ';
        addvals(device,dhand,"Divide by zero");
        value[device] = 0;
        op[device] = 'z';
        return(BTLE_CONTINUE);
        }
      }

    for(n = 0 ; n < 15 ; ++n)
      vals[device][n] = ' ';
    sprintf(s,"%.6g",value[device]);
    addvals(device,dhand,s);

    if(newop == '=')
      {
      op[device] = 0;
      }
    else
      {
      ops[0] = ' ';
      ops[1] = newop;
      ops[2] = 0;
      addvals(device,dhand,ops);      
      op[device] = newop + 128;
      }
    }
  else if(event == BTLE_DISCONNECT)
    {
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
void addvals(int device,int handle,char *s)
  {
  int n,k;
  
  if(s[0] == 'C' || (op[device] & 128) != 0)
    {
    op[device] &= 127;
    for(n = 0 ; n < 15 ; ++n)
      vals[device][n] = ' ';
    }
    
  if(s[0] != 'C')
    {
    for(n = 0 ; s[0] == '.' && n < 15 ; ++n)
      {
      if(vals[device][n] == '.')
        return;
      }
     
    n = 0;
    while(vals[device][n] != ' ' && n < 15)
      ++n;
    if(s[0] == '<')
      {
      if(n == 0)
        return;
      vals[device][n-1] = ' ';
      }
    else
      {
      if(n == 15)
        return;
      k = 0;
      while(s[k] != 0 && n+k < 15)
        {
        vals[device][n+k] = s[k];
        ++k;
        }
      }
    }
  btle_change_text(device,handle,vals[device]);
  }  
  
