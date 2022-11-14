/******* BeetleIN server **********

Full documentation at https://github.com/petzval/beetlein

REQUIRES
  btle.h
  btlib.c Version 4
  btlib.h
COMPILE
  gcc mycode.c btle.c btlib.c -o mycode
RUN
  sudo ./mycode
  
  
Minimum mycode.c =

#include <stdio.h>
#include <stdlib.h>
#include "btle.h"

int onEvent(int event,int device,int handle,int member,char *text);

int main()
  {
  btle_server(onEvent,"My Code");
  return(0);
  }
  
int onEvent(int event,int device,int handle,int member,char *text)
  {
  return(BTLE_CONTINUE);
  }
    
  
**************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "btlib.h"
#include "btle.h"

#define BTLE_VERSION 1
#define BTLE_PROTOCOL 1

#define INST_INIT_REPLY  1
#define INST_SETTINGS    2
#define INST_PAINT       3
#define INST_SET_FONT    4
#define INST_MESSAGE     5
#define INST_PROMPT      6
#define INST_BUTTON      7
#define INST_CHECK       8
#define INST_SELECT      9
#define INST_TEXT        10
#define INST_NEWLINE     11 
#define INST_DATA        12
#define INST_REMOVE      13
#define INST_RESTORE     14
#define INST_CHANGE_TEXT   15
#define INST_CHANGE_COLOUR 16
#define INST_CHANGE_FONT   17
#define INST_CHANGE_CHECK  18
#define INST_CLEAR         19
#define INST_DISCONNECT    20
#define INST_ACKREQUEST    21
#define INST_IMAGE 22
#define INST_IMAGE_LINE 23
#define INST_IMAGE_MULTILINE 24
#define INST_IMAGE_ARC 25
#define INST_IMAGE_RECT 26
#define INST_IMAGE_CIRCLE 27
#define INST_IMAGE_OVAL 28
#define INST_IMAGE_TEXT 29
#define INST_IMAGE_CLEAR 30
#define INST_MAX 30

#define CLICK_ACK     0
#define CLICK_ERROR   3
#define CLICK_INIT    1
#define CLICK_BUTTON  7
#define CLICK_CHECK   8
#define CLICK_SELECT  9
#define CLICK_TEXT    10
#define CLICK_DATA    12
#define CLICK_DISCONNECT 20
#define CLICK_RESTART  2

#define CTICN_NOTIFY 0
#define CTICN_CLICK  1

#define DEFAULT_BATCH 8
#define DEFAULT_BLOCK 16
  // android value - local will be +1 second
#define DEFAULT_CLICKTODS 30

#define FLAG_SLAVE 1

void btle_initdata(int flag);
unsigned char btle_newdevice(int clientnode,int n0);
int btle_nextxhandle(int device);
unsigned char btle_getdevice(int clientnode);
int btle_extradata(int device,char *s,int len0);
int btle_callback(int clientnode,int operation,int cticn);
int btle_deviceok(int device,int pflag);
int btle_deviceokc(int device,int pflag);
int btle_incid(int device);
void btle_pushcmd(unsigned char *data,int paintflag);
int btle_cmdbatch(int device);
void btle_nixcmds(int device);
void btle_xcmd(int sn);
int btle_newcmds(int device,int flag);
void btle_sortstack(void);
int btle_sortdevice(int dev,int sn);
void btle_cleanstack(void);
void btle_globdata(void);
int btle_devhandok(int device,int handle,int op,int parentop,int pop2,int pop3);
void btle_devstack(int device);
int btle_settings(int device,int *params,int len,int loclen);
  
struct clientdata
  {
  int connected;
  int clientnode;
  int protocol;
  int nexthandle;
  int ackwait;
  int sentcount;
  int secure;
  int trycount;
  int pinhandle;
  unsigned char nextid;
  unsigned char eventid;
  char name[20];
  char address[20];
  unsigned char data[256];
  };
  
struct clientdata *devdat[256];
unsigned char btlestack[8192];

struct btleglobdata
  {
  int btlestn;
  int totackwait;  // number ack expected 
  int batchcount;  // per batch 
  int blockcount;  // number of batches to force paint  
  int clicktods;   // click time out
  int(*oneventcb)();
  int btleflags;
  int slave;
  int maxdevice;
  char password[16];
  char address[24];
  char name[256];
  };
 
struct btleglobdata btleg;

char *btle_errs[8] = { "None","Invalid opcode","Invalid handle","Run out of handles","Invalid operation on this item",
                       "Missed previous item","Invalid parameter","Master/Slave set up"};

char *btle_ops[32] = { "unknown","init","settings","paint","set_font","message/broadcast","text",
                  "button","check","select","text_input","newline","data","remove","restore","change_text",
                  "change_colour","change_font","change_check","clear","disconnect","ackreq","image","image_line",
                  "image_multiline","image_arc","image_rect","image_circle","image_oval","image_text","image_clear" };


int btle_server(int(*callback)(),char *name)
  {
  return(btle_server_ex(callback,name,0));
  }
  
int btle_server_ex(int(*callback)(),char *name,int hci)
  {
  int n,hcix; 
  static int initflag = 0;
      
  if(callback == NULL)
    {
    printf("Callback = null\n");
    return(0);
    }
  
  btle_globdata();  
  btleg.oneventcb = callback;
  
  btleg.btleflags = 0;
  
  hcix = hci & 0xFF;
  if(hcix != 0)
    printf("Using hci%d (not on-board adapter hci0)\n",hcix);
   
  if(init_btle(name,hcix) == 0) 
    return(0);     

  strcpy(btleg.name,name);
  strcpy(btleg.address,device_address(0));

  btle_initdata(initflag);
  initflag = 1;
  btleg.btlestn = 0;
  btleg.totackwait = 0;
  printf("Version %d  Protocol %d\n",BTLE_VERSION,BTLE_PROTOCOL);
  
   
  (*btleg.oneventcb)(SERVER_START,0,0,0,name);

  le_server(btle_callback,0);
  
  for(n = 1 ; n <= btleg.maxdevice && devdat[n] != NULL ; ++n)
    { 
    if(btle_deviceokc(n,0) != 0)
      {
      btle_nixcmds(n);
      disconnect_node(devdat[n]->clientnode);
      devdat[n]->connected &= 0x10;
      }
    }
  
  return(0);
  } 


int btle_callback(int clientnode,int operation,int cticn)
  {
  int n,dn,event,nread,xhandle,member,ndat,ver,opcode,retval,id,flag,pdev;
  unsigned int scode;
  unsigned char dat[32];
  unsigned char inst[20];
  unsigned char device; 
  char name[20],text[256];
  
  retval = BTLE_CONTINUE;
  device = 0;
  xhandle = 0;
  member = 0;
  text[0] = 0;
       
  if(operation == LE_CONNECT)
    {
    device = btle_newdevice(clientnode,0);
    if(device == 0)
      return(SERVER_CONTINUE);
  
      
    btle_nixcmds(device);  
    devdat[device]->connected |= 1;
    devdat[device]->nexthandle = 0;
    devdat[device]->ackwait = 0;
    devdat[device]->eventid = 0;
    devdat[device]->nextid = 1;
    devdat[device]->trycount = 0;
    if(btleg.password[0] == 0)
      devdat[device]->secure = 1;
    strcpy(devdat[device]->name,device_address(clientnode));
    strcpy(devdat[device]->address,device_address(clientnode));
    return(SERVER_CONTINUE);
    }
  else if(operation == LE_TIMER)
    {  // from local clientnode timerds interval 
    retval = (*btleg.oneventcb)(SERVER_TIMER,0,0,0,"");
    btle_newcmds(0,0);  // no device, TIMER
    btle_cmdbatch(0);   // no device, no ACK
    if(retval == BTLE_EXIT)  
      return(SERVER_EXIT);
    return(SERVER_CONTINUE);
    }
  else
    device = btle_getdevice(clientnode);
   
   
  if(device == 0 || device > 254 || devdat[device] == NULL || (devdat[device]->connected & 0x03) == 0)
    {
    printf("Device %d not found\n",device); 
    return(SERVER_CONTINUE);
    }  

  if(operation == LE_BTLETIMER)
    {   
    if(devdat[device]->ackwait != 0)
      {
      printf("Transmission error\n");
      devdat[device]->ackwait = 0;
      devdat[device]->eventid = 0;
      devdat[device]->sentcount = 0;
      }
    btleg.totackwait = 0;
    btle_cmdbatch(0);
    return(SERVER_CONTINUE);
    }    
   
  if(operation == LE_WRITE && cticn == CTICN_CLICK)
    {
    // read local characteristic that client has just written
    nread = read_ctic(localnode(),cticn,dat,sizeof(dat));
    if(nread != 20)
      printf("Transmission error\n");
       
    opcode = dat[0];
    
    if(opcode == CLICK_ACK)  // ACK
      {     
      btleg.totackwait = 0;
        
      if(devdat[device]->ackwait != 0)
        {
        if(devdat[device]->sentcount != dat[1])
          {
          printf("Transmission error\n");
          }
        devdat[device]->ackwait = 0;       
        devdat[device]->sentcount = 0;
        btle_devtimer(devdat[device]->clientnode,0);  // stop to
        devdat[device]->eventid = 0;
        }
      btle_cmdbatch(0); 
      }  // end ACK
    else if(opcode == CLICK_ERROR)
      {
      if(dat[2] != 0)
        {
        if(dat[1] <= INST_MAX && dat[2] <= 7)
          printf("*** ERROR btle_%s %s\n",btle_ops[dat[1]],btle_errs[dat[2]]);
        else
          printf("*** ERROR code %d %d\n",dat[1],dat[2]);
        }
      }     
    else if(opcode == CLICK_INIT)
      {
      pdev = dat[4];  // previous device known by Android 
      if(pdev != 0 && pdev != device && pdev <= btleg.maxdevice && devdat[pdev] != NULL &&
              (devdat[pdev]->connected & 0x03) == 0 && (devdat[pdev]->connected & 0x10) != 0 )
        {  // use pdev instead of device
        btle_newdevice(clientnode,pdev);  // re-init pdev
      
        devdat[pdev]->secure = devdat[device]->secure;
        strcpy(devdat[pdev]->name,devdat[device]->name);
        strcpy(devdat[pdev]->address,devdat[device]->address);
        devdat[device]->connected = 0;  // free
        devdat[device]->clientnode = 0;
        device = pdev;
        }
 
      n = 0;
      while(n < 15 && dat[n+5] != 0)
        {  // may be "" - leave name=address
        devdat[device]->name[n] = dat[n+5];
        ++n;
        }
      if(n > 0)
        devdat[device]->name[n] = 0;
           
      btle_nixcmds(device);
      
      devdat[device]->connected = 0x13;  // 00010011
      devdat[device]->protocol = dat[1];
      devdat[device]->ackwait = 0;
      devdat[device]->eventid = 0;
      devdat[device]->nextid = 1;
      devdat[device]->nexthandle = 0;
      devdat[device]->sentcount = 0;
                          
      printf("%s %s connected as device %d\n",devdat[device]->address,
                      devdat[device]->name,device);

      if(dat[1] != BTLE_PROTOCOL)
        {
        printf("Different protocols - update so both are same\n");
        printf("  This device=%d  Other device=%d\n",BTLE_PROTOCOL,dat[1]);
        }
              
           // reply with device 
      dat[0] = INST_INIT_REPLY;
      dat[1] = device;
      dat[2] = dat[2];
      dat[3] = dat[3];
      dat[4] = BTLE_PROTOCOL;
      dat[5] = (unsigned char)(btleg.btleflags & 0xFF);
      if(btleg.slave != 0)
        dat[5] |= FLAG_SLAVE;

      dat[6] = (unsigned char)(btleg.btleflags >> 8) & 0xFF;        
      dat[7] = (unsigned char)(btleg.btleflags >> 16) & 0xFF;             
      dat[8] = 2;   // btferret server
      for(n = 8 ; n < 20 ; ++n)
        dat[n] = 0;
          
      btleg.slave &= 1;  // allow INIT_REPLY and PAINT         
      btle_pushcmd(dat,0);
                 
      btleg.totackwait = 0;
      
      btle_newcmds(device,1);
      btle_cmdbatch(device);           
                 
      if(btleg.slave != 0)
        devdat[device]->secure = 1;
        
      if(devdat[device]->secure == 0)
        {
        btle_text(device,"Password");
        devdat[device]->pinhandle = btle_text_input(device,16);
        }
      else      
        {
        devdat[device]->pinhandle = 0;
        retval = (*btleg.oneventcb)(BTLE_CONNECT,device,0,0,"");
        }
      if(btle_newcmds(device,3) == 0)
         { // no cmds - force paint
         dat[0] = INST_PAINT;
         dat[1] = device;
         for(n = 2 ; n < 20 ; ++n)
           dat[n] = 0;
         btle_pushcmd(dat,1);
         btle_newcmds(device,3);
         }
      btle_cmdbatch(device);
      }
    else if(opcode == CLICK_BUTTON || opcode == CLICK_SELECT ||
                     opcode == CLICK_CHECK || opcode == CLICK_TEXT)
      {  // click - will go to onEvent       
      xhandle = dat[1];
      member = 0;
      text[0] = 0;
      
      if(opcode == CLICK_TEXT && xhandle == (devdat[device]->pinhandle & 0xFF) && devdat[device]->secure == 0)
        {
        if(dat[2] >= strlen(btleg.password))
          scode = 0;
        else 
          scode = 1;
        n = 0;
        while(scode == 0 && btleg.password[n] != 0 && n < 15)
          {
          if(dat[n+3] != btleg.password[n])
            scode = 1;
          ++n;
          } 
        if(scode == 0)
          {
          devdat[device]->secure = 1;
          devdat[device]->nexthandle = 0;
          devdat[device]->pinhandle = 0;
          btle_clear(device);
          retval = (*btleg.oneventcb)(BTLE_CONNECT,device,0,0,"");
          
          if(btle_newcmds(device,3) == 0)
            { // no cmds - force paint
            dat[0] = INST_PAINT;
            dat[1] = device;
            for(n = 2 ; n < 20 ; ++n)
              dat[n] = 0;
            btle_pushcmd(dat,1);
            btle_newcmds(device,3);
            }
     
          btle_cmdbatch(device);
          if(retval == BTLE_EXIT)  
            return(SERVER_EXIT);
          return(SERVER_CONTINUE);
          }
        else
          {
          if(devdat[device]->trycount < 3)
            ++devdat[device]->trycount;    
          else
            btle_disconnect(device);            
          }
        return(SERVER_CONTINUE);
        }
      
      if(devdat[device]->secure == 0)
        return(SERVER_CONTINUE);
        
      if(opcode == CLICK_BUTTON)
        event = BTLE_CLICK_BUTTON;
      else if(opcode == CLICK_CHECK)
        {
        event = BTLE_CLICK_CHECK;
        member = dat[2];
        }
      else if(opcode == CLICK_SELECT)
        {
        event = BTLE_CLICK_SELECT;
        member = dat[2];
        }
      else if(opcode == CLICK_TEXT)
        {
        if(xhandle == 0)
          event = BTLE_BROADCAST;
        else
          event = BTLE_CLICK_TEXT; 
        n = 0;
        dn = 0;
        while(n < dat[2] && n < 251)
          {
          if(n < 17)
            text[n] = dat[n+3];
          else
            {
            text[n] = devdat[device]->data[dn];
            ++dn;
            }
          ++n;
          }
        text[n] = 0;
        }
            
      retval = (*btleg.oneventcb)(event,device,xhandle | (opcode << 8) | (device << 16) ,member,text);
  
      if(btle_newcmds(device,3) == 0)
        { // no cmds - force paint
        dat[0] = INST_PAINT;
        dat[1] = device;
        for(n = 2 ; n < 20 ; ++n)
          dat[n] = 0;
        btle_pushcmd(dat,1);
        btle_newcmds(device,3);
        }
      
      btle_cmdbatch(device);
      }  // end clickable events    
    else if(opcode == CLICK_RESTART && devdat[device]->secure != 0)
      {
      devdat[device]->nexthandle = 0;
      btle_clear(device);
      retval = (*btleg.oneventcb)(BTLE_CONNECT,device,0,0,"");
      
      if(btle_newcmds(device,3) == 0)
         { // no cmds - force paint
         dat[0] = INST_PAINT;
         dat[1] = device;
         btle_pushcmd(dat,1);
         btle_newcmds(device,3);
         }
   
      
      btle_cmdbatch(device);
      }     
    else if(opcode == CLICK_DATA)
      {  // extra data to device store for later CLICK_TEXT
      dn = dat[1];   // block number 0-13
      if(dn < 14)
        {
        dn *= 18;      // data index
        for(n = 0 ; n < 18 ; ++n)
          {
          devdat[device]->data[dn] = dat[n+2];
          ++dn;
          }
        }
      }         
    }   // end LE_WRITE
  else if(operation == LE_DISCONNECT)
    {
    devdat[device]->connected &= 0x10;  // can re-connect as previous device 
    retval = (*btleg.oneventcb)(BTLE_DISCONNECT,device,xhandle,member,text);
    printf("%s has disconnected\n",devdat[device]->name);
    if(retval != BTLE_EXIT)
      {
      flag = 0;
      for(n = 1 ; n <= btleg.maxdevice ; ++n)
        {
        if(btle_connected(n) != 0)
          flag = 1;
        }
      if(flag == 0)  
        printf("Waiting for another connection (x=exit)\n");
      }         
    btle_nixcmds(device);
    btle_newcmds(device,0);  
    btle_cmdbatch(0);       
    }


  if(retval == BTLE_EXIT)  
    return(SERVER_EXIT);
  return(SERVER_CONTINUE);  
  }



void btle_globdata()
  {
  btleg.btlestn = 0;
  btleg.totackwait = 0;  // number ack expected 
  btleg.slave = 0;
  btleg.maxdevice = 0;
  btleg.btleflags = 0;
  btleg.batchcount = DEFAULT_BATCH;  // per batch 
  btleg.blockcount = DEFAULT_BLOCK;  // number of batches to force paint  
  btleg.clicktods = DEFAULT_CLICKTODS + 10;   // click time out
  btleg.oneventcb = NULL;
  btleg.password[0] = '\0';
  btleg.address[0] = '\0';
  btleg.name[0] = '\0';
  }

int btle_timer(int timerds)
  {
  btle_devtimer(0,timerds);
  return(1);  
  }
 
int btle_password(char *pword)
  {
  int n;
  n = 0;
  if(strlen(pword) > 15)
    {
    printf("ERROR - Password max 15 chars\n");
    return(0);
    }
  while(pword != NULL && n < 15 && pword[n] != 0)
    {
    btleg.password[n] = pword[n];
    ++n;
    }
  btleg.password[n] = 0;
  return(1);
  }

int btle_slave()
  {
  int n;
 
  for(n = 1 ; n <= btleg.maxdevice ; ++n)
    {
    if(devdat[n] != NULL && (devdat[n]->connected & 3) != 0)
      {
      printf("ERROR - btle_slave must be called before any connection\n");
      return(0);
      }
    }
  btleg.slave = 1;
  return(1);
  }

 
int btle_message(int device,char *mess)  
  {
  int n,len,xlen;
  unsigned char dat[20];


  if(btle_devhandok(device,0,INST_MESSAGE,0,0,0) == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
 
  xlen = strlen(mess);  // total length
  len = xlen;           // this notify length
  if(xlen > 16)
    {
    xlen = btle_extradata(device,mess,16);
    len = 16;
    }
    
  dat[0] = INST_MESSAGE;
  dat[1] = (unsigned char)device;
  dat[2] = 0;  // message flag
  dat[3] = xlen;
  
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = mess[n];
  
  btle_pushcmd(dat,0);
  return(1);
  }


int btle_message_all(char *mess)  
  {
  int n,len,device;
  unsigned char dat[20];

  // use any connected deivice 

  device = 0;
  for(n = 1 ; n <= btleg.maxdevice  && device == 0 ; ++n)
    {
    if(btle_connected(n) == 1)
      device = n;
    }
    
  if(device == 0)
    return(0);
      
  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
 
  len = strlen(mess);  // total length
  if(len > 16)
    {
    printf("Message_all too long - truncated to 16 chars\n");
    len = 16;
    }
   
       
  dat[0] = INST_MESSAGE;
  dat[1] = (unsigned char)device;
  dat[2] = 2;  // all flag
  dat[3] = len;
  
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = mess[n];
  
  btle_pushcmd(dat,0);
  return(1);
  }



int btle_broadcast(char *mess)  
  {
  int n,len,device;
  unsigned char dat[20];

  // use any connected deivice 

  device = 0;
  for(n = 1 ; n <= btleg.maxdevice  && device == 0 ; ++n)
    {
    if(btle_connected(n) == 1)
      device = n;
    }
    
  if(device == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
 
  len = strlen(mess);  // total length
  if(len > 16)
    {
    printf("Broadcast too long - truncated to 16 chars\n");
    len = 16;
    }
    
  dat[0] = INST_MESSAGE;
  dat[1] = (unsigned char)device;
  dat[2] = 1;  // broadcast flag
  dat[3] = len;
  
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = mess[n];
  
  btle_pushcmd(dat,0);
  return(1);
  }



int btle_text(int device,char *text)
  {
  int n,xhandle,len,xlen;
  unsigned char dat[20];
  

  if(btle_devhandok(device,0,INST_PROMPT,0,0,0) == 0)
    return(0);

  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);
      
  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;

  xlen = strlen(text);  // total length
  len = xlen;           // this notify length
  if(xlen > 16)
    {
    xlen = btle_extradata(device,text,16);
    len = 16;
    }

  dat[0] = INST_PROMPT;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
  dat[3] = xlen;
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = text[n];
   
  btle_pushcmd(dat,1);

  return(xhandle | (INST_PROMPT << 8) | (device << 16));
  }

int btle_button(int device,char *text)
  {
  int n,xhandle,len;
  unsigned char dat[20];
    
  if(btle_devhandok(device,0,INST_BUTTON,0,0,0) == 0)
    return(0);
    
  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);
      
  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;
  
  dat[0] = INST_BUTTON;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
  len = strlen(text);
  if(len > 17)
    {
    printf("Button text %s too long - truncated\n",text);
    len = 17;
    }
  for(n = 0 ; n < len ; ++n)
    dat[n+3] = text[n];

  btle_pushcmd(dat,1);  
 
  return(xhandle | (INST_BUTTON << 8) | (device << 16));
  }


int btle_check(int device,int state)
  {
  int n,xhandle,len;
  unsigned char dat[20];
    
    
  if(btle_devhandok(device,0,INST_CHECK,0,0,0) == 0)
    return(0);
    
  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);
      
  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;
  
  dat[0] = INST_CHECK;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
  dat[3] = state;
  
  btle_pushcmd(dat,1);
 
  return(xhandle | (INST_CHECK << 8) | (device << 16));
  }



int btle_select(int device,char *text)
  {
  int n,xhandle,len,xlen;
  unsigned char dat[20];
    
  if(btle_devhandok(device,0,INST_SELECT,0,0,0) == 0)
    return(0);
   
  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;

  xlen = strlen(text);  // total length
  len = xlen;           // this notify length
  if(xlen > 16)
    {
    xlen = btle_extradata(device,text,16);
    len = 16;
    }
  
  dat[0] = INST_SELECT;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
  dat[3] = xlen;
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = text[n];

  btle_pushcmd(dat,1);
 
  return(xhandle | (INST_SELECT << 8) | (device << 16));
  }


int btle_text_input(int device,int width)
  {
  int n,xhandle;
  unsigned char wid;
  unsigned char dat[20];
  
  
  if(btle_devhandok(device,0,INST_TEXT,0,0,0) == 0)
    return(0);

  
  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
  
  dat[0] = INST_TEXT;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
  if(width < 1)
    wid = 1;
  else if(width > 40)
    wid = 40;
  else
    wid = width;
  dat[3] = wid;
  
  btle_pushcmd(dat,1);

  return(xhandle | (INST_TEXT << 8) | (device << 16));
  }
  
int btle_image(int device,int width,int height,int numlines,int red,int green,int blue)
  {
  int n,xhandle;
  unsigned char dat[20];
    
  if(width <= 0 || height <= 0 || numlines <= 0)
    {
    printf("ERROR btle_image parameter <= 0\n");
    return(0);
    }  
        
  if(btle_devhandok(device,0,INST_IMAGE,0,0,0) == 0)
    return(0);
  
  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);
      
  for(n = 11 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)xhandle;
  dat[3] = (unsigned char)(width & 0xFF);
  dat[4] = (unsigned char)((width >> 8) & 0xFF);
  dat[5] = (unsigned char)(height & 0xFF);
  dat[6] = (unsigned char)((height >> 8) & 0xFF);
  dat[7] = (unsigned char)numlines;
  dat[8] = (unsigned char)red;
  dat[9] = (unsigned char)green;
  dat[10] = (unsigned char)blue;

    
  btle_pushcmd(dat,1);
  
  return(xhandle | (INST_IMAGE << 8) | (device << 16));
  }


int btle_image_line(int device,int xhandle,int x0,int y0,int x1,int y1,int width,int red,int green,int blue)
  {
  int n,dev,op;
  unsigned char dat[20]; 
  
  if(width <= 0)
    {
    printf("ERROR btle_image_line width <= 0\n");
    return(0);
    }  

  if(btle_devhandok(device,xhandle,INST_IMAGE_LINE,INST_IMAGE,0,0) == 0)
    return(0);
  
  for(n = 15 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE_LINE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)(x1 & 0xFF);
  dat[8] = (unsigned char)((x1 >> 8) & 0xFF);
  dat[9] = (unsigned char)(y1 & 0xFF);
  dat[10] = (unsigned char)((y1 >> 8) & 0xFF);
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)width;
  
  btle_pushcmd(dat,1);
  return(1); 
  }
  

int btle_image_multiline(int device,int xhandle,int *x,int *y,int start,int end,int width,int red,int green,int blue,int pstyle,int pwid)
  {
  int n,dn,tick,in,xn,dev,op,del;
  unsigned char dat[20]; 
  

  if(width <= 0)
    {
    printf("ERROR btle_image_multiline width <= 0\n");
    return(0);
    }  

  if(btle_devhandok(device,xhandle,INST_IMAGE_MULTILINE,INST_IMAGE,0,0) == 0)
    return(0);

  del = end-start-1;  // num points in DATA beyond 1st two
  if(del <= 0 || del > 1088)
    {
    printf("ERROR btle_image_multiline end-start too small or too big (max 1090 points)\n");
    return(0);
    }
  
  if(del > 0)
    {
    dn = start+2;  // first data point in extra data
    in = 0;        // data packet index 0-13
    xn = 20;       // force new data packet on 1st loop
    tick = 0;      // switch x/y lo/hi
    for(n = 0 ; n < del*4 ; ++n)
      {
      if(xn == 20)
        {  // send data and start new packet
        if(n > 0)
          {
          btle_pushcmd(dat,0);
          }
        dat[0] = INST_DATA;
        dat[1] = (unsigned char)device;
        dat[2] = in;  // xtra index
        ++in;
        xn = 3;
        }
      
      if(tick == 0)
        dat[xn] = (unsigned char)(x[dn] & 0xFF);
      else if(tick == 1)
        dat[xn] = (unsigned char)((x[dn] >> 8) & 0xFF);
      else if(tick == 2)
        dat[xn] = (unsigned char)(y[dn] & 0xFF);
      else
        {
        dat[xn] = (unsigned char)((y[dn] >> 8) & 0xFF);
        ++dn;
        }
      ++xn;
      
      tick = (tick + 1) & 3;         
      }
    btle_pushcmd(dat,0);
    }   
    
  dat[0] = INST_IMAGE_MULTILINE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x[start] & 0xFF);
  dat[4] = (unsigned char)((x[start] >> 8) & 0xFF);
  dat[5] = (unsigned char)(y[start] & 0xFF);
  dat[6] = (unsigned char)((y[start] >> 8) & 0xFF);
  dat[7] = (unsigned char)(x[start+1] & 0xFF);
  dat[8] = (unsigned char)((x[start+1] >> 8) & 0xFF);
  dat[9] = (unsigned char)(y[start+1] & 0xFF);
  dat[10] = (unsigned char)((y[start+1] >> 8) & 0xFF);
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)width;
  dat[15] = (unsigned char)(del & 0xFF);
  dat[16] = (unsigned char)((del >> 8) & 0xFF);
  dat[17] = (unsigned char)pstyle;  // pts flag
  dat[18] = (unsigned char)pwid;     // pts wid
  dat[19] = 0;

  btle_pushcmd(dat,1); 
  return(1);
  }


int btle_scale_data(float *x,float *y,int start,int end,float xmin,float xmax,float ymin,float ymax,
               int xb,int yb,int xt,int yt,int *px,int *py,int len)
  {
  int dn,pn,n0,xp[2],yp[2],dx,dy;
  int xs,ys,flag,cflag,width,height;
  double temp,xfac,yfac,xx,yy;
  
  
  width = xt - xb;
  if(width <= 0)
    {
    printf("ERROR btle_scale_data Top right to left of origin\n");
    return(0);
    }
  height = yb - yt;
  if(height <= 0)
    {
    printf("ERROR btle_scale_data Top right below origin\n");
    return(0);
    }
      
  temp = xmax-xmin;
  if(temp <= 0)
    {
    printf("ERROR btle_scale_data xmax <= xmin\n");
    return(0);
    }
  xfac = (double)width/temp;
  temp = ymax-ymin;
  if(temp <= 0)
    {
    printf("ERROR btle_scale_data ymax <= ymin\n");
    return(0);
    }
  yfac = (double)height/temp;
  
  pn = 0;
  flag = 0xF0;  // last = break - start new line
  xp[1] = 0;
  yp[1] = 0;
  
  for(dn = start ; dn <= end ; ++dn)
    {
    xp[0] = xp[1];  // old = last new
    yp[0] = yp[1];
    xx = (double)xb + (x[dn] - xmin)*xfac;
    xp[1] = (int)xx;
    if(xx-xp[1] >= 0.5)
      ++xp[1];
    yy = (double)yb - (y[dn] - ymin)*yfac;
    yp[1] = (int)yy;
    if(yy-yp[1] >= 0.5)
      ++yp[1];
     
   
    if(xp[1] < xb)
      flag |= 1;
    else if(xp[1] > xt)
      flag |= 2;
    if(yp[1] > yb)
      flag |= 4;
    else if(yp[1] < yt)
      flag |= 8;
      
    if(flag == 0 || flag == 0xF0)
      {  // last and new pt in range
         // or last was break and new in range (new line start) 
      if(pn < len)
        {
        px[pn] = xp[1];
        py[pn] = yp[1];
        ++pn;
        }
      else
        {
        printf("ERROR btle_scale_data px/py length too small\n");
        px[0] = LINE_BREAK;
        return(0);
        }
      }
    else if((flag & 0x0F) == 0 || (flag & 0xF0) == 0)
      {  // one in/one out of range - calc boundary intersection xs ys
      dx = xp[1]-xp[0];
      dy = yp[1]-yp[0];
      if((flag & 0xF0) != 0)
        {
        n0 = 1;  // last out of range - use new xp[1]
        cflag = flag >> 4; 
        }
      else  // new out of range - use last xp[0]
        {
        cflag = flag;
        n0 = 0;
        }
        
      cflag &= 0x0F; 
        
      if((cflag & 1) != 0)
        xs = xb;  // will cross xb axis
      else if((cflag & 2) != 0)
        xs = xt;
      if((cflag & 4) != 0)
        ys = yb;
      else if((cflag & 8) != 0)
        ys = yt;
        
      if((cflag & 12) != 0 && dy != 0)
        {  // cross top/bot X axis at xs 
        xx = (double)xp[n0] + (double)(ys - yp[n0])*(double)dx/(double)dy;            
        xs = (int)xx;
        if(xx-xs >= 0.5)
          ++xs;
        if(xs >= xb && xs <= xt)
          cflag = 0;  // found solution in range - stop ys soln
        }
        
      if((cflag & 3) != 0 && dx != 0)
        {  // cross left/right Y axis at ys
        yy = (double)yp[n0] + (double)(xs - xp[n0])*(double)dy/(double)dx;
        ys = (int)yy;
        if(yy-ys >= 0.5)
          ++ys;
        if(ys >= yt && ys <= yb)
          cflag = 0;   // found solution in range
        }
        
      if(cflag == 0)
        {
        if(pn >= len-1)
          {
          printf("ERROR btle_scale_data px/py length too small\n");
          px[0] = LINE_BREAK;
          return(0);
          }
        if(n0 == 0)
          { // new xp[1] out of range
          px[pn] = xs;   // end line at boundary
          py[pn] = ys;
          ++pn;
          px[pn] = LINE_BREAK; 
          py[pn] = 0;
          ++pn;
          flag = 0x0F;      // break flag
          }
        else 
          { // old xp[0] out of range
          px[pn] = xs;  // start new line at boundary
          py[pn] = ys;
          ++pn;
          px[pn] = xp[1];  
          py[pn] = yp[1];
          ++pn;
          }     
        }  
      }    
     // else both out of range - no plot
  
        
    flag = (flag << 4) & 0xF0;   
    }


  // strip trailing line breaks
  while(pn > 0 && px[pn-1] == LINE_BREAK)
    --pn;  

  if(pn == 0)
    {
    px[0] = LINE_BREAK;
    return(0);
    }
        
  return(pn-1);
  }



int btle_image_arc(int device,int xhandle,int x0,int y0,int x1,int y1,int radius,int route,int width,int red,int green,int blue)
  {
  int n,dev,op;
  unsigned char dat[20]; 
  

  if(width <= 0)
    {
    printf("ERROR btle_image_arc width <= 0\n");
    return(0);
    }  


  if(btle_devhandok(device,xhandle,INST_IMAGE_ARC,INST_IMAGE,0,0) == 0)
    return(0);
 
  
  dat[0] = INST_IMAGE_ARC;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)(x1 & 0xFF);
  dat[8] = (unsigned char)((x1 >> 8) & 0xFF);
  dat[9] = (unsigned char)(y1 & 0xFF);
  dat[10] = (unsigned char)((y1 >> 8) & 0xFF);
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)width;
  dat[15] = (unsigned char)(radius & 0xFF);
  dat[16] = (unsigned char)((radius >> 8) & 0xFF);
  dat[17] = (unsigned char)route;
  dat[18] = 0;
  dat[19] = 0;

 
  btle_pushcmd(dat,1);
  return(1); 
  }

int btle_image_rect(int device,int xhandle,int x0,int y0,int x1,int y1,int red,int green,int blue,int style,int wid)
  {
  int n,dev,op;
  unsigned char dat[20]; 
  
 
  if(btle_devhandok(device,xhandle,INST_IMAGE_RECT,INST_IMAGE,0,0) == 0)
    return(0);
  
  for(n = 16 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE_RECT;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)(x1 & 0xFF);
  dat[8] = (unsigned char)((x1 >> 8) & 0xFF);
  dat[9] = (unsigned char)(y1 & 0xFF);
  dat[10] = (unsigned char)((y1 >> 8) & 0xFF);
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)wid;
  dat[15] = (unsigned char)style;
 
  btle_pushcmd(dat,1);
  return(1); 
  }
  
  
int btle_image_circle(int device,int xhandle,int x0,int y0,int radius,int red,int green,int blue,int style,int wid)
  {
  int n,dev,op;
  unsigned char dat[20]; 

  if(btle_devhandok(device,xhandle,INST_IMAGE_CIRCLE,INST_IMAGE,0,0) == 0)
    return(0);
  
  for(n = 16 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE_CIRCLE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)(radius & 0xFF);
  dat[8] = (unsigned char)((radius >> 8) & 0xFF);
  dat[9] = 0;
  dat[10] = 0;
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)wid;
  dat[15] = (unsigned char)style;

  
  btle_pushcmd(dat,1);
  return(1); 
  }
  

int btle_image_oval(int device,int xhandle,int x0,int y0,int x1,int y1,int red,int green,int blue,int style,int wid)
  {
  int n,dev,op;
  unsigned char dat[20]; 
 
    
  if(btle_devhandok(device,xhandle,INST_IMAGE_OVAL,INST_IMAGE,0,0) == 0)
    return(0);
  
  for(n = 16 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE_OVAL;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)(x1 & 0xFF);
  dat[8] = (unsigned char)((x1 >> 8) & 0xFF);
  dat[9] = (unsigned char)(y1 & 0xFF);
  dat[10] = (unsigned char)((y1 >> 8) & 0xFF);
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  dat[14] = (unsigned char)wid;
  dat[15] = (unsigned char)style;
   
  btle_pushcmd(dat,1); 
  return(1);
  }


int btle_image_text(int device,int xhandle,char *text,int x0,int y0,int dirn,int font,int size,int red,int green,int blue)
  {
  int n,dev,op,len,xlen;
  unsigned char dat[20]; 
  
  
  if(btle_devhandok(device,xhandle,INST_IMAGE_TEXT,INST_IMAGE,0,0) == 0)
    return(0);

  xlen = strlen(text);  // total length
  len = xlen;           // this notify length
  if(xlen > 6)
    {
    xlen = btle_extradata(device,text,6);
    len = 6;
    }
    
  for(n = 0 ; n < len ; ++n)
    dat[14+n] = text[n]; 

  dat[0] = INST_IMAGE_TEXT;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)(x0 & 0xFF);
  dat[4] = (unsigned char)((x0 >> 8) & 0xFF);
  dat[5] = (unsigned char)(y0 & 0xFF);
  dat[6] = (unsigned char)((y0 >> 8) & 0xFF);
  dat[7] = (unsigned char)dirn;
  dat[8] = (unsigned char)font;
  dat[9] = (unsigned char)size;
  dat[10] = (unsigned char)xlen;
  dat[11] = (unsigned char)red;
  dat[12] = (unsigned char)green;
  dat[13] = (unsigned char)blue;
  
  btle_pushcmd(dat,1);
  return(1); 
  }
  
int btle_image_clear(int device,int xhandle)
  {
  int n,dev,op;
  unsigned char dat[20]; 

  if(btle_devhandok(device,xhandle,INST_IMAGE_CLEAR,INST_IMAGE,0,0) == 0)
    return(0);
   
  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_IMAGE_CLEAR;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
   
  btle_pushcmd(dat,1); 
  return(1);
  }
  
  
int btle_newline(int device)
  {
  int n,xhandle;
  unsigned char dat[20];

  if(btle_devhandok(device,0,INST_NEWLINE,0,0,0) == 0)
    return(0);

  xhandle = btle_nextxhandle(device);
  if(xhandle == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
  
  dat[0] = INST_NEWLINE;
  dat[1] = (unsigned char)device;
  dat[2] = xhandle;
 
  btle_pushcmd(dat,1); 

  return(xhandle | (INST_NEWLINE << 8) | (device << 16));
  }


int btle_font(int device,int font)
  {
  int n;
  unsigned char dat[20];

  if(btle_devhandok(device,0,INST_SET_FONT,0,0,0) == 0)
    return(0);

  if(font < 0 || font > FONT_MAX)
    {
    printf("Invalid font\n");
    return(0);
    }
  
  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_SET_FONT;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)font;
  
  btle_pushcmd(dat,0);
  return(1);
  }
  
  
int btle_spacings(int device,int hpad,int vpad,int hspace,int vspace)
  {
  int p[4];

  if(hpad < 0 || hpad > 20 || vpad < 0 || vpad > 20 ||
     hspace < 0 || hspace > 20 || vspace < 0 || vspace > 20)
    {
    printf("Spacings parameter out of range 0-20\n");
    return(0);
    }
  p[0] = hpad;
  p[1] = vpad;
  p[2] = hspace;
  p[3] = vspace;  
  return(btle_settings(device,p,4,0));
  }
  
int btle_message_buffer(int device,int bufsz)
  {
  int n,p[5];
  
  if(bufsz < 8 || bufsz > 250)
    {
    printf("Buffer size out of range (min 8)\n");
    return(0);
    }
  for(n = 0 ; n < 4 ; ++n)
    p[n] = NO_CHANGE;
  p[4] = bufsz;
    
  return(btle_settings(device,p,5,0));
  }
  
int btle_connect_settings(int device,int tos,int retry)
  {
  int n,p[7];
  
  if(tos < 1 || tos > 60 || retry < 0 || retry > 100)
    {
    printf("Connect settings out of range (tos=1-60 retry=0-100)\n");
    return(0);
    }
  
  for(n = 0 ; n < 5 ; ++n)
    p[n] = NO_CHANGE;
  p[5] = tos * 10;
  p[6] = retry;   
  return(btle_settings(device,p,7,0));
  }
  
/*********

Android data to dat[+2]
len = 0 to 18

0 = hpad
1 = vpad
2 = hspace
3 = vspace
4 = bufsz
5 = conntods
6 = conn retry

**********/  
  
int btle_settings(int device,int *p,int len,int loclen)
  {
  int n;
  unsigned char dat[20];
    
  
  if(btle_devhandok(device,0,INST_SETTINGS,0,0,0) == 0)
    return(0);
  
  if(len <= 0 || len > 18)
    return(1);
  
  for(n = 2 ; n < 20 ; ++n)
    dat[n] = NO_CHANGE;
    
  dat[0] = INST_SETTINGS;
  dat[1] = (unsigned char)device;
  for(n = 0 ; n < len ; ++n)
    dat[n+2] = (unsigned char)(p[n] & 0xFF);
  
  btle_pushcmd(dat,1);
  return(1);
  }


int btle_change_text(int device,int xhandle,char *text)
  {
  int n,len,xlen,dev,op;
  unsigned char dat[20];
    
  if(btle_devhandok(device,xhandle,INST_CHANGE_TEXT,INST_PROMPT,INST_BUTTON,INST_SELECT) == 0)
    return(0);
    
  for(n = 4 ; n < 20 ; ++n)
    dat[n] = 0;
    
  xlen = strlen(text);  // total length
  len = xlen;           // this notify length
  if(xlen > 16)
    {
    xlen = btle_extradata(device,text,16);
    len = 16;
    }

  dat[0] = INST_CHANGE_TEXT;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)xlen;
  
  for(n = 0 ; n < len ; ++n)
    dat[n+4] = text[n];
  
  btle_pushcmd(dat,1);
  return(1);
  }



int btle_change_colour(int device,int xhandle,int red,int green,int blue)
  {
  int n,op,dev;
  unsigned char dat[20];
    
  if(btle_devhandok(device,xhandle,INST_CHANGE_COLOUR,INST_PROMPT,INST_BUTTON,INST_IMAGE) == 0)
    return(0);

  for(n = 6 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_CHANGE_COLOUR;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)red;
  dat[4] = (unsigned char)green;
  dat[5] = (unsigned char)blue;
 
  btle_pushcmd(dat,1);
  return(1); 
  }

int btle_change_font(int device,int xhandle,int font)
  {
  int n,op,dev;
  unsigned char dat[20];
    
  if(font < 0 || font > FONT_MAX)
    {
    printf("Invalid font\n");
    return(0);
    }

  if(btle_devhandok(device,xhandle,INST_CHANGE_FONT,INST_PROMPT,INST_BUTTON,0) == 0)
    return(0);

  for(n = 4 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_CHANGE_FONT;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)font;
  
  btle_pushcmd(dat,1);
  return(1);
  }

int btle_change_check(int device,int xhandle,int state)
  {
  int n,op,dev;
  unsigned char dat[20];
 
  if(btle_devhandok(device,xhandle,INST_CHANGE_CHECK,INST_CHECK,0,0) == 0)
    return(0);

  for(n = 4 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_CHANGE_CHECK;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
  dat[3] = (unsigned char)state;
  
  btle_pushcmd(dat,1);
  return(1);
  }

int btle_remove(int device,int xhandle)
  {
  int n,dev;
  unsigned char dat[20];

  if(btle_devhandok(device,xhandle,INST_REMOVE,-1,0,0) == 0)
    return(0);

  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_REMOVE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
 
  btle_pushcmd(dat,1);
  return(1);
  }
  
int btle_restore(int device,int xhandle)
  {
  int n,dev;
  unsigned char dat[20];
  
  if(btle_devhandok(device,xhandle,INST_RESTORE,-1,0,0) == 0)
    return(0);

  for(n = 3 ; n < 20 ; ++n)
    dat[n] = 0;

  dat[0] = INST_RESTORE;
  dat[1] = (unsigned char)device;
  dat[2] = (unsigned char)(xhandle & 0xFF);
 
  btle_pushcmd(dat,1);
  return(1);
  }

int btle_connected(int device)
  {
  if(device < 1 || device > btleg.maxdevice || devdat[device] == NULL || (devdat[device]->connected & 3) == 0)
    return(0);
  return(1);  
  }

int btle_maxdevice()
  {
  return(btleg.maxdevice);
  }

char *btle_local_name()
  {
  return(btleg.name);
  }
char *btle_local_address()
  {
  return(btleg.address);
  }  

char *btle_name(int device)
  {
  if(btle_deviceok(device,0) == 0)
    return("");

  return(devdat[device]->name);
  }  

char *btle_address(int device)
  {
  if(btle_deviceok(device,0) == 0)
    return("");

  return(devdat[device]->address);
  }  

int btle_disconnect(int device)
  {
  int n,flag;
  
  if(btle_deviceokc(device,0) == 0)
    return(0);

  disconnect_node(devdat[device]->clientnode);

  devdat[device]->connected &= 0x10;  // can re-connect as previous device
  printf("%s disconnected\n",devdat[device]->name);
  flag = 0;
  for(n = 1 ; n <= btleg.maxdevice ; ++n)
    {
    if(btle_connected(n) != 0)
      flag = 1;
    }
     
  if(flag == 0)
    printf("Waiting for another connection (x=exit)\n");
  btle_nixcmds(device);
  btle_newcmds(device,0);  
  btle_cmdbatch(0);       
  return(1);
  }  

 
  
int btle_clear(int device)
  {
  int n;
  unsigned char dat[20];

  if(btle_devhandok(device,0,INST_CLEAR,0,0,0) == 0)
    return(0);

  for(n = 0 ; n < 20 ; ++n)
    dat[n] = 0;
  
  dat[0] = INST_CLEAR;
  dat[1] = (unsigned char)device;
  devdat[device]->nexthandle = 0;

  btle_pushcmd(dat,1);
  return(1);
  }

int btle_extradata(int device,char *s,int len0)
  {
  int n,k,len,rem,nx,sn,retlen,dlen;
  unsigned char dat[20];
  
  if(btle_deviceokc(device,0) == 0)
    return(0);

  // len0 in instruction - rest in extra data sends
   
  len = strlen(s);
  nx = (len-len0)/17;
  rem = (len-len0)%17;
  if(rem > 0)
   ++nx;
  if(nx > 14)
    {
    printf("Text %c%c%c%c... too long - truncated\n",s[0],s[1],s[2],s[3]);
    nx = 14;
    len = 238+len0;
    }
 
  dat[0] = INST_DATA;
  dat[1] = (unsigned char)device;
  retlen = len0; 
  len -= len0;  
  sn = len0;
  for(n = 0 ; n < nx ; ++n)
    {
    dat[2] = n;
    
    if(len > 17)
      dlen = 17;
    else
      dlen = len;

  
    for(k = 3 ; k < 20 ; ++k)
      dat[k] = 0;
      
    for(k = 0 ; k < dlen ; ++k)
      {
      dat[k+3] = s[sn];
      ++sn;
      }
              

    btle_pushcmd(dat,0);   
    len -= dlen;
    retlen += dlen;  
    }
  return(retlen);  
  }


int btle_devhandok(int device,int handle,int op,int parentop,int pop2,int pop3)
  {
  int hop,dev;
    
  if(btle_deviceokc(device,0) == 0)
    {
    printf("Invalid device %d in btle_%s\n",device,btle_ops[op]);
    return(0);
    }    
  
  if(parentop == 0)
    return(1);  // no check handle
    
  dev = (handle >> 16) & 0xFF;
  if(dev != device)
    {
    if(btle_deviceok(dev,0) == 0)
      printf("Invalid handle in btle_%s\n",btle_ops[op]);
    else
      printf("btle_%s error - Handle belongs to device %d\n",btle_ops[op],dev);
    return(0);
    }

  if((handle & 0xFF) == 0)
    {
    printf("Invalid handle in btle_%s\n",btle_ops[op]);
    return(0);
    }
    
  if(parentop == -1)
    return(1);  // no check parent op
    
  hop = (handle >> 8) & 0xFF; 
  if(!(hop == parentop || hop == pop2 || hop == pop3))
    {
    if(pop2 == 0 && pop3 == 0)
      printf("Not a btle_%s handle in btle_%s\n",btle_ops[parentop],btle_ops[op]);
    else
      printf("Cannot call btle_%s for item with specified handle\n",btle_ops[op]);
    return(0);
    }
    
  return(1);
  }


int btle_deviceok(int device,int pflag)
  {
  if(device < 1 || device > 254 || devdat[device] == NULL)
    {
    if(pflag != 0)
      printf("Invalid device %d\n",device);
    return(0);
    }
  return(1);
  }  
    
int btle_deviceokc(int device,int pflag)
  {
  if(btle_deviceok(device,pflag) == 0)
    return(0);
  if(devdat[device]->connected & 3 != 0)
    return(1);
  // printf("Device %d not connected\n",device);
  return(0);
  }    

    
unsigned char btle_newdevice(int clientnode,int n0)
  {
  int n,k;
  
  if(n0 != 0)
    n = n0;  // init existing 
  else  
    {
    n = btle_getdevice(clientnode);
    if(n == 0)
      { // not existing
      // look for alloc but never connected or unalloc
      n = 1;  
      while(devdat[n] != NULL && devdat[n]->connected != 0 && n <= btleg.maxdevice)
        ++n;
  
      if(n == 255)  // max device=254
        {  // look for disconnected 10 and re-use previously connected
        n = 1;
        while(devdat[n] != NULL && (devdat[n]->connected & 0x03) != 0 && n < 255)
          ++n;
        if(n == 255 || devdat[n] == NULL)
          {  
          printf("Too many devices\n");
          return(0);
          }
        devdat[n]->connected = 0;
        }
      }
    }
    
  if(devdat[n] == NULL)
    {
    devdat[n] = (struct clientdata*)malloc(sizeof(struct clientdata));
    if(devdat[n] == NULL)
       return(0);
    devdat[n]->connected = 0;
    if(n > btleg.maxdevice)
      btleg.maxdevice = n;
    }

  devdat[n]->connected &= 0x10;  // leave was connected bit
  devdat[n]->clientnode = clientnode;
  devdat[n]->protocol = 0;
  devdat[n]->nexthandle = 0;
  devdat[n]->ackwait = 0;
  devdat[n]->sentcount = 0;
  devdat[n]->secure = 0;
  devdat[n]->eventid = 0;
  devdat[n]->nextid = 1;
  devdat[n]->name[0] = 0;
  devdat[n]->address[0] = 0;
  for(k = 0 ; k < 256 ; ++k)
    devdat[n]->data[k] = 0;
  
  return(n);
  }

unsigned char btle_getdevice(int clientnode)
  {
  int n;
  
  for(n = 1 ; n <= btleg.maxdevice && devdat[n] != NULL ; ++n)
    {
    if(devdat[n]->clientnode == clientnode)
      return(n);
    }
  return(0);
  }

int btle_nextxhandle(int device)
  {
  ++devdat[device]->nexthandle;
  if(devdat[device]->nexthandle >= 256)
    {
    printf("Run out of handles\n");
    return(0);
    }
  return(devdat[device]->nexthandle);
  }  

  
void btle_initdata(int flag)
  {
  int n;

  if(flag != 0)
    return;
      
  for(n = 0 ; n < 256 ; ++n)
    devdat[n] = NULL;

    // devdat[0] not used
  devdat[0] = (struct clientdata*)malloc(sizeof(struct clientdata)); 
  if(devdat[0] != NULL)
    devdat[0]->connected = 0; 
  }

int *btle_handles()
  {
  return(calloc(256,sizeof(int)));
  }


int btle_cmdbatch(int prioritydev)
  {
  int n,k,sn,device,id,eid,count,flag,nextisack,getout,mflag;
  unsigned char dat[32];
  
  
  if(btleg.totackwait > 0 || btleg.btlestn == 0)
    {
    return(0);  // waiting for acks or empty stack
    }
    
  btle_cleanstack();
  btle_devstack(prioritydev);  // move device insts to bottom so sent first    
  // send max batchcount commands
  // if device eventid set - only send eventid cmds - skip others
  // if                not set - set to id on stack  

   
  count = 0;  
  n = 0;
  getout = 0;
  while(n < btleg.btlestn && getout == 0 && count < btleg.batchcount+2)
    {                               // check count for safety
    device = btlestack[n+1];  
    eid = devdat[device]->eventid;
    id = btlestack[n+20];
    flag = 1;
    if(eid == 0)   // start sending new id 
      {
      devdat[device]->eventid = id;
      devdat[device]->sentcount = 0;
      }      
    else if(eid != id || devdat[device]->ackwait != 0)
      flag = 0;  // no send
             
    if(flag != 0)
      {
      ++count;
      if(btlestack[n] == INST_MESSAGE && btlestack[n+2] == 2)
        mflag = 1;  // message_all 
      else 
        mflag = 0;  
   
      if(btlestack[n] != INST_ACKREQUEST && mflag == 0)
        ++devdat[device]->sentcount;
        
      if(mflag == 0)
        btle_notifynode(devdat[device]->clientnode);
   
      write_ctic(localnode(),CTICN_NOTIFY,btlestack+n,20);
      btle_notifynode(0);
             
     
      // is next an ACK for this device/id - if so, let it run, do not terminate via batchcount
      nextisack = 0;
        
      if(n+22 == btleg.btlestn || (btlestack[n+21] & 2) != 0 || (count >= btleg.batchcount && nextisack == 0))
        {
        if(count >= btleg.batchcount)
          getout = 1;  // getout must be on ACK request already on stack
                       // or forced by batchcount or forced by end of stack btlestn
        devdat[device]->ackwait = 1;  // stop more sends from this device until get ACK
        btleg.totackwait = 1;
    
        btlestack[n+21] |= 2;  // ACK request in case end of stack or batchcount
          
        for(k = 7 ; k < 20 ; ++k)
          dat[k] = 0;
    
        dat[0] = (unsigned char)(INST_ACKREQUEST);
        dat[1] = (unsigned char)device;
        dat[2] = (unsigned char)((btlestack[n+21] >> 3) & 1);   // unclick
        dat[3] = (unsigned char)((btlestack[n+21] >> 2) & 1);   // unlock to + paint
        dat[4] = (unsigned char)((btlestack[n+21] >> 1) & 1);   // ack request
        dat[5] = (unsigned char)(btlestack[n+21] & 1);          // paint
        dat[6] = (unsigned char)devdat[device]->sentcount;       
                
        btle_devtimer(devdat[device]->clientnode,btleg.clicktods);          
        btle_notifynode(devdat[device]->clientnode);
        write_ctic(localnode(),CTICN_NOTIFY,dat,20);
        btle_notifynode(0);
        }     
     
      btle_xcmd(n);
      }
    else
      n += 22;
    }  
    
  return(0);
  }  
  
  


void btle_pushcmd(unsigned char *data,int paintflag)
  {
  int n,dev;

  if(btleg.slave != 0)
    {
    if((btleg.slave & 2) != 0)
      return;
    if(data[0] != INST_INIT_REPLY && data[0] != INST_PAINT)
      return;  // dump BTLE_CONNECT cmds  
    if(data[0] == INST_PAINT)
      btleg.slave |= 2;
    }  
   
  if(btleg.btlestn >= 8180)
    {
    printf("Too many items\n");
    return;
    }

  dev = data[1];
  if(btle_deviceokc(dev,1) == 0)
    return;    
    
  for(n = 0 ; n < 20 ; ++n)
    btlestack[btleg.btlestn+n] = data[n];
    
  if(paintflag == 0)
    n = 0;
  else
    n = 1;

  btlestack[btleg.btlestn+20] = devdat[dev]->nextid;
  btlestack[btleg.btlestn+21] = n;   // paint flag  
  btleg.btlestn += 22;
  }


void btle_cleanstack()
  {
  int n;
  // clean up stack remove invalid and disconnected devices
  n = 0;
  while(n < btleg.btlestn)
    {
    if(btle_deviceokc(btlestack[n+1],0) == 0 || (devdat[btlestack[n+1]]->connected & 3) == 0)
      btle_xcmd(n);
    else           
      n += 22;
    }
  }


int btle_newcmds(int device,int flag)
  {
  int n,dn,count,devcount,id,paintflag;
  int lastn;
  unsigned char dat[20];
 
  btle_cleanstack();
  btle_sortstack();  // sort new entries  
  
  devcount = 0;
       
    // search stack for each device with its current nextid - must be new
  for(dn = 1 ; dn <= btleg.maxdevice && devdat[dn] != NULL ; ++dn)
    {
    id = devdat[dn]->nextid;
    paintflag = 0;
    count = 0;
    n = 0;
  
    while(n < btleg.btlestn)
      {  
      if(btlestack[n+1] == dn && btlestack[n+20] == id)
        {  // new entry for this device
        ++count;
        if(dn == device)
          ++devcount;
        if((btlestack[n+21] & 1) != 0)
          paintflag = 1;
    
        btlestack[n+21] |= paintflag;  // all subsequent in block   
        
        if((count % btleg.batchcount) == 0)
          {
          btlestack[n+21] |= 2;   // end of batch - ACK request  
          if((count % (btleg.batchcount*btleg.blockcount)) == 0)
            {  // force unlock/paint every blockcount batches
            btlestack[n+21] |= 4;   // end of block - add unlock
            paintflag = 0;
            }
          }
        lastn = n + 21;
        }
      n += 22;
      }
       
      
    if(count != 0)  // new nextid cmds on stack
      {           
      btlestack[lastn] |= 8 + 4 + 2 + paintflag;  // paint/ack/unlock/unclick
      
       // finished with this nextid
               
      if(devdat[dn]->nextid == 255)
        devdat[dn]->nextid = 1;
      else
       ++devdat[dn]->nextid;
       
      }
    }  // next device     

  return(devcount);
  }

void btle_nixcmds(int device)
  {
  int n;
  
  if(btleg.btlestn == 0)
    return;
  n = btleg.btlestn-22;  // last
  while(n >= 0)
    {
    if(btlestack[n+1] == device)
      btle_xcmd(n);
    n -= 22;
    }  
  }

void btle_xcmd(int sn)
  {
  int n;
  
  if(btleg.btlestn == 0 || sn >= btleg.btlestn)
    return;
    
  n = sn;
  while(n < btleg.btlestn-22)
    {
    btlestack[n] = btlestack[n+22];
    ++n; 
    }
  btleg.btlestn -= 22;
  }

void btle_devstack(int device)
  {  // move device block to bottom of stack
  int n,k,j,sn,n0,n1,sav,count;

  if(device == 0)
    return;
     
  count = 0;
  n = 0;   
  while(n < btleg.btlestn)
    {
    if(btlestack[n+1] == device)
      {
      if(count == 0)
        {
        n0 = n;
        n1 = n;
        }
      else
        n1 = n;
      ++count;
      }  
    n += 22;
    }  
  
  if(count > 0 && n0 > 0)
    {  // is device block above [0] shift n1-n0 to bottom
    for(sn = 0 ; sn < count ; ++sn)
      {  // shift n1 to bottom
      for(k = 0 ; k < 22 ; ++k)
        {
        sav = btlestack[n1+k];
        for(j = n1 ; j > 0 ; j -= 22)
          btlestack[j+k] = btlestack[j+k-22];
        btlestack[k] = sav;
        }
      }
    }
  }  
  

void btle_sortstack()
  {
  int sn,sn0,n,device,getout,getoutx;
  
  // consolidate new entries
  
  sn0 = 0;
      
  // find first new entry
 
  do
    {
    n = sn0; // first possible new unsorted entry
    getout = 0;
    while(n < btleg.btlestn && getout == 0)
      {
      device = btlestack[n+1];
      if(btlestack[n+1] == device && btlestack[n+20] == devdat[device]->nextid)
        {
        sn = n;  // new entry for this device
        getout = 1;
        }
      n += 22;
      }
    if(getout != 0)
      sn0 = btle_sortdevice(device,sn);
    }
  while(getout != 0);
  
  }
  
  
/***** SORT DEVICE
from btlestack[sn]
consolidate all later dev entries
*****************/

int btle_sortdevice(int dev,int sn)
  {
  int n,n0,n1,sn0,j,k,sav,getout;
  
  // sn is known dev
  sn0 = sn + 22;
  getout = 0;
  do
    {
    n = sn0; // first possible non-dev
    n0 = 0;  // first non-dev
    n1 = 0;  // following dev
    while(n < btleg.btlestn && (n0 == 0 || n1 == 0))
      {
      if(n0 == 0)
        {
        if(btlestack[n+1] != dev)
          n0 = n;
        }
      else
       {
       if(btlestack[n+1] == dev)
          n1 = n;
       }
      n += 22;
      }
    if(n0 == 0 || n1 == 0)
      getout = 1;
    else
      {  // swap n1 to n0, shift n0 to (n1-1) up
      for(k = 0 ; k < 22 ; ++k)
        {
        sav = btlestack[n1+k];
        for(j = n1 ; j >= n0+22 ; j -= 22)
          btlestack[j+k] = btlestack[j+k-22];
        btlestack[n0+k] = sav;
        }
      sn0 = n0 + 22;  // first possible non-dev
      } 
    }  
  while(getout == 0);
  return(sn0);
  }
