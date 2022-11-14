#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

int *hpup,*hpdown,*vpup,*vpdown,*hsup,*hsdown,*vsup,*vsdown,*pr;

int hpad[256];
int vpad[256];
int hspace[256];
int vspace[256];

int main()
  {
  btle_server(onEvent,"Spacings");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  int n;
  char s[128];  
  
  if(event == SERVER_START)
    {
    hpup = btle_handles();
    hpdown = btle_handles();
    vpup = btle_handles();
    vpdown = btle_handles();
    hsup = btle_handles();
    hsdown = btle_handles();
    vsup = btle_handles();
    vsdown = btle_handles();
    pr = btle_handles();
    for(n = 0 ; n < 256 ; ++n)
      {
      hpad[n] = 5;
      vpad[n] = 5;
      hspace[n] = 5;
      vspace[n] = 5;
      }
    }
  if(event == BTLE_CONNECT)
    {
    hpad[device] = 5;
    vpad[device] = 5;
    hspace[device] = 5;
    vspace[device] = 5;    
    pr[device] = btle_text(device,"Defaults Hpad=5 Vpad=5 Hspace=5 Vspace=5");
    btle_newline(device);
    hpup[device] = btle_button(device,"Hpad +");    
    hpdown[device] = btle_button(device,"Hpad -");    
    vpup[device] = btle_button(device,"Vpad +");    
    vpdown[device] = btle_button(device,"Vpad -");    
    btle_newline(device);
    hsup[device] = btle_button(device,"Hspc +");    
    hsdown[device] = btle_button(device,"Hspc -");    
    vsup[device] = btle_button(device,"Vspc +");    
    vsdown[device] = btle_button(device,"Vspc -"); 
    btle_newline(device);  
    btle_text(device,"Text");
    btle_select(device,"Select,Zero,One,Two");
    btle_text_input(device,6);   
    }
  else if(event == BTLE_CLICK_BUTTON)
    {
    if(handle == hpup[device] && hpad[device] < 20)
      ++hpad[device];
    else if(handle == hpdown[device] && hpad[device] > 0)
      --hpad[device];
    if(handle == vpup[device] && vpad[device] < 20)
      ++vpad[device];
    else if(handle == vpdown[device] && vpad[device] > 0)
      --vpad[device];

    if(handle == hsup[device] && hspace[device] < 20)
      ++hspace[device];
    else if(handle == hsdown[device] && hspace[device] > 0)
      --hspace[device];
    if(handle == vsup[device] && vspace[device] < 20)
      ++vspace[device];
    else if(handle == vsdown[device] && vspace[device] > 0)
      --vspace[device];
    
    sprintf(s,"Hpad=%d Vpad=%d Hspace=%d Vspace=%d",hpad[device],vpad[device],hspace[device],vspace[device]);
    btle_change_text(device,pr[device],s); 
    btle_spacings(device,hpad[device],vpad[device],hspace[device],vspace[device]);
    }
  else if(event == BTLE_DISCONNECT)
    {
    // return(BTLE_EXIT); 
    }
     
  return(BTLE_CONTINUE);     
  }
  
