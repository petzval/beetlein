#!/usr/bin/python3
# Library for BeetleIN server
# Full documentation at https://github.com/petzval/beetlein
# Import to your code as follows
# Minimum code mycode.py =
#
#    #!/usr/bin/python3
#    from btle import *
#
#    def onEvent(event,device,handle,member,text):
#      return(BTLE_CONTINUE)
#
#    btle_server(onEvent,"Name")
#
#
# RUN via:
#    python3 mycode.py
#
# The dbus/bluez parts of this code have been
# adapted from the sample files available here:
# https://www.bluetooth.com/bluetooth-resources/bluetooth-for-linux/ 

import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib
import sys
from gi.repository import GLib

# constants also needed by user code

BTLE_CONNECT = 0
BTLE_CLICK_BUTTON = 1
BTLE_CLICK_SELECT = 2
BTLE_CLICK_TEXT = 3
SERVER_TIMER = 4
BTLE_DISCONNECT = 5
SERVER_START = 6
BTLE_CLICK_CHECK = 7
BTLE_BROADCAST = 8

BTLE_CONTINUE = 0
BTLE_EXIT     = 1


FONT_DEFAULT = 0
FONT_THIN    = 1
FONT_LIGHT   = 2
FONT_MEDIUM  = 3
FONT_THICK   = 4
FONT_CONDENSED = 5
FONT_FIXED   = 6
FONT_SERIF   = 7
FONT_SERIF_FIXED = 8
FONT_CASUAL  = 9
FONT_DANCING = 10
FONT_GOTHIC  = 11
FONT_MAX = 11

STYLE_FILL = 0
STYLE_STROKE = 1
DIRN_HORIZ = 0
DIRN_VERT = 1

DEFAULT_VALUE = 255
NO_CHANGE = 254

CLOCK_SHORT = 0
CLOCK_LONG = 1
ANTICLOCK_SHORT = 2
ANTICLOCK_LONG  = 3

LINE_BREAK = -32768
POINTS_OFF = 0
POINTS_SQUARE = 1
POINTS_CIRCLE = 2
POINTS_CROSS = 3
POINTS_TRIANGLE = 4
POINTS_ONLY = 128

UNCHECKED = 0
CHECKED = 1

# end constants needed by user code

btle_errs = ["None","Invalid opcode","Invalid handle","Run out of handles",
             "Invalid operation on this item","Missed previous item",
             "Invalid parameter","Master/Slave set up"]

btle_ops = ["unknown","init","settings","paint","set_font","message/broadcast",
            "text","button","check","select","text_input","newline","data",
            "remove","restore","change_text","change_colour","change_font",
            "change_check","clear","disconnect","ackreq","image","image_line",
            "image_multiline","image_arc","image_rect","image_circle",
            "image_oval","image_text","image_clear"]

# emd constants


# only global needed by this btle.py
# will be global variables class
btleg = None

# global variables for btleg
class globaldata:
  def __init__(self):
    self.oneventcb = None
    self.mainloop = None
    self.adv = None 
    self.chrnotify = None
    self.devdat = []    
    self.name = "BTLE"
    self.address = ""
    self.flags = 0
    self.instruct = [0 for n in range(20)]
    self.timerds = 0
    self.hci = 0
    self.timerid = 0
    self.BTLE_PROTOCOL = 1
    self.BTLE_VERSION = 1
    self.stack = [0 for n in range(8192)]
    self.stn = 0
    self.totackwait = 0
    self.slave = 0
    self.maxdevice = 0
    self.password = None
    self.DEFAULT_BATCH = 8
    self.DEFAULT_BLOCK = 16
    self.DEFAULT_CLICKTODS = 30
    self.batchcount = self.DEFAULT_BATCH
    self.blockcount = self.DEFAULT_BLOCK
    self.clicktoms = (self.DEFAULT_CLICKTODS * 100) + 1000

    # notify opcodes outgoing

    self.INST_INIT_REPLY = 1
    self.INST_SETTINGS   = 2
    self.INST_PAINT      = 3
    self.INST_SET_FONT   = 4
    self.INST_MESSAGE    = 5
    self.INST_PROMPT     = 6
    self.INST_BUTTON     = 7
    self.INST_CHECK      = 8
    self.INST_SELECT     = 9
    self.INST_TEXT       = 10
    self.INST_NEWLINE    = 11 
    self.INST_DATA       = 12
    self.INST_REMOVE     = 13
    self.INST_RESTORE    = 14
    self.INST_CHANGE_TEXT   = 15
    self.INST_CHANGE_COLOUR = 16
    self.INST_CHANGE_FONT   = 17
    self.INST_CHANGE_CHECK  = 18
    self.INST_CLEAR         = 19
    self.INST_DISCONNECT    = 20
    self.INST_ACKREQUEST    = 21
    self.INST_IMAGE         = 22
    self.INST_IMAGE_LINE    = 23
    self.INST_IMAGE_MULTILINE = 24
    self.INST_IMAGE_ARC     = 25
    self.INST_IMAGE_RECT    = 26
    self.INST_IMAGE_CIRCLE  = 27
    self.INST_IMAGE_OVAL    = 28
    self.INST_IMAGE_TEXT    = 29
    self.INST_IMAGE_CLEAR   = 30
    self.INST_MAX = 30
        
    # click opcodes incoming

    self.CLICK_ACK = 0
    self.CLICK_ERROR = 3
    self.CLICK_INIT   = 1
    self.CLICK_BUTTON = 7
    self.CLICK_CHECK  = 8
    self.CLICK_SELECT = 9
    self.CLICK_TEXT   = 10
    self.CLICK_DATA   = 12
    self.CLICK_DISCONNECT = 20
    self.CLICK_RESTART = 2
    
           
    self.FLAG_SLAVE = 1

# device data      
  
class clientdata:
  def __init__(self): 
    self.connected = 0
    self.nexthandle = 0
    self.protocol = 0
    self.ackwait = 0
    self.sentcount = 0
    self.secure = False
    self.trycount = 0
    self.pinhandle = 0
    self.nextid = 1
    self.eventid = 0
    self.cmdtimid = None
    self.cmdtimflag = False
    self.path = ""
    self.name = ""
    self.address = ""
    self.data = [0 for n in range(256)]
    
  
# exceptions

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class NotAuthorizedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotAuthorized'

class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'

# end exceptions



class Service(dbus.service.Object):
  #  org.bluez.GattService1 interface implementation

  def __init__(self, bus, path_base, index, uuid, primary):
    self.path = path_base + "/service" + str(index)
    self.bus = bus
    self.uuid = uuid
    self.primary = primary
    self.characteristics = []
    dbus.service.Object.__init__(self, bus, self.path)

  def get_properties(self):
    return {"org.bluez.GattService1": {
              'UUID': self.uuid,
              'Primary': self.primary,
              'Characteristics': dbus.Array(
              self.get_characteristic_paths(),
              signature='o')}}

  def get_path(self):
    return dbus.ObjectPath(self.path)

  def add_characteristic(self, characteristic):
    self.characteristics.append(characteristic)

  def get_characteristic_paths(self):
    result = []
    for chrc in self.characteristics:
      result.append(chrc.get_path())
    return result

  def get_characteristics(self):
    return self.characteristics

  @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature='s',
                         out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != "org.bluez.GattService1":
      raise InvalidArgsException()
    return self.get_properties()["org.bluez.GattService1"]


class Characteristic(dbus.service.Object):
  #  org.bluez.GattCharacteristic1 interface implementation

  def __init__(self, bus, index, uuid, flags, service):
    self.path = service.path + '/char' + str(index)
    # creating Characteristic with path=self.path
    self.bus = bus
    self.uuid = uuid
    self.service = service
    self.flags = flags
    self.descriptors = []
    dbus.service.Object.__init__(self, bus, self.path)

  def get_properties(self):
    return {"org.bluez.GattCharacteristic1": {
              'Service': self.service.get_path(),
              'UUID': self.uuid,
              'Flags': self.flags,
              'Descriptors': dbus.Array(
              self.get_descriptor_paths(),
              signature='o')}}

  def get_path(self):
    return dbus.ObjectPath(self.path)

  def add_descriptor(self, descriptor):
    self.descriptors.append(descriptor)

  def get_descriptor_paths(self):
    result = []
    for desc in self.descriptors:
      result.append(desc.get_path())
    return result

  def get_descriptors(self):
    return self.descriptors

  @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature='s',
                         out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != "org.bluez.GattCharacteristic1":
      raise InvalidArgsException()

    return self.get_properties()["org.bluez.GattCharacteristic1"]

  @dbus.service.method("org.bluez.GattCharacteristic1",
                        in_signature='a{sv}',
                        out_signature='ay')
  def ReadValue(self, options):
    print('Remote device has read non-btle characteristic')
    raise NotSupportedException()

  @dbus.service.method("org.bluez.GattCharacteristic1",in_signature='aya{sv}')
  def WriteValue(self, value, options):
    print('Remote device has written non-btle characteristic')
    raise NotSupportedException()

  @dbus.service.method("org.bluez.GattCharacteristic1")
  def StartNotify(self):
    print('Default StartNotify called, returning error')
    raise NotSupportedException()

  @dbus.service.method("org.bluez.GattCharacteristic1")
  def StopNotify(self):
    print('Default StopNotify called, returning error')
    raise NotSupportedException()

  @dbus.service.signal("org.freedesktop.DBus.Properties",
                         signature='sa{sv}as')
  def PropertiesChanged(self, interface, changed, invalidated):
    pass


class Descriptor(dbus.service.Object):
  #   org.bluez.GattDescriptor1 interface implementation
  def __init__(self, bus, index, uuid, flags, characteristic):
    self.path = characteristic.path + '/desc' + str(index)
    self.bus = bus
    self.uuid = uuid
    self.flags = flags
    self.chrc = characteristic
    dbus.service.Object.__init__(self, bus, self.path)

  def get_properties(self):
    return {"org.bluez.GattDescriptor1": {
              'Characteristic': self.chrc.get_path(),
              'UUID': self.uuid,
              'Flags': self.flags,}}

  def get_path(self):
    return dbus.ObjectPath(self.path)

  @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature='s',
                         out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != "org.bluez.GattDescriptor1":
      raise InvalidArgsException()

    return self.get_properties()["org.bluez.GattDescriptor1"]

  @dbus.service.method("org.bluez.GattDescriptor1",
                        in_signature='a{sv}',
                        out_signature='ay')
  def ReadValue(self, options):
    print('Default ReadValue called, returning error')
    raise NotSupportedException()

  @dbus.service.method("org.bluez.GattDescriptor1",in_signature='aya{sv}')
  def WriteValue(self, value, options):
    print('Default WriteValue called, returning error')
    raise NotSupportedException()



class Advertisement(dbus.service.Object):
      
  PATH_BASE = '/org/bluez/ldsg/advertisement'

  def __init__(self, bus, index, advertising_type):
    global btleg
    
    self.path = self.PATH_BASE + str(index)
    self.bus = bus
    self.ad_type = advertising_type
    self.service_uuids = None
    self.manufacturer_data = None
    self.solicit_uuids = None
    self.service_data = None
    self.local_name = btleg.name[0:18]
    self.minint = 300
    self.maxint = 600
    self.include_tx_power = False
    self.data = None
    self.discoverable = True
    dbus.service.Object.__init__(self, bus, self.path)

  def get_properties(self):
    properties = dict()
    properties['Type'] = self.ad_type

    if self.local_name is not None:
      properties['LocalName'] = dbus.String(self.local_name)
    if self.discoverable is not None and self.discoverable == True:
      properties['Discoverable'] = dbus.Boolean(self.discoverable)

    properties['MinInterval'] = dbus.Int32(self.minint)
    properties['MaxInterval'] = dbus.Int32(self.maxint)
    
    return {"org.bluez.LEAdvertisingManager1": properties}

  def get_path(self):
    return dbus.ObjectPath(self.path)

  @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature='s',
                         out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != "org.bluez.LEAdvertisement1":
      raise InvalidArgsException()
    return self.get_properties()["org.bluez.LEAdvertisingManager1"]

  @dbus.service.method("org.bluez.LEAdvertisingManager1",
                         in_signature='',
                         out_signature='')
  def Release(self):
    print('%s: Released' % self.path)


class Application(dbus.service.Object):
  #  org.bluez.GattApplication1 interface implementation
  
  def __init__(self, bus):
    # Adding Beetle Service to the Application
    self.path = '/'
    self.services = []
    dbus.service.Object.__init__(self, bus, self.path)
    self.add_service(BeetleService(bus, '/org/bluez/ldsg', 0))

  def get_path(self):  
    return dbus.ObjectPath(self.path)

  def add_service(self, service):
    self.services.append(service)

  @dbus.service.method('org.freedesktop.DBus.ObjectManager',
                           out_signature='a{oa{sa{sv}}}')
  def GetManagedObjects(self):
    global btleg
                
    response = {}
           
    for service in self.services:
      # GetManagedObjects: service=service.get_path()
      response[service.get_path()] = service.get_properties()
      chrcs = service.get_characteristics()
      for chrc in chrcs:
        response[chrc.get_path()] = chrc.get_properties()
        if(chrc.get_properties()['org.bluez.GattCharacteristic1']['UUID'] ==
                                  '11223344-5566-7788-99aa-bbccddeeff00'):
          # GOT notify characteristic
          btleg.chrnotify = chrc
                             
        descs = chrc.get_descriptors()
        for desc in descs:
          response[desc.get_path()] = desc.get_properties()

    return response


class BeetleService(Service):

  def __init__(self, bus, path_base, index):
    # Initialising Beetle Service object
    Service.__init__(self, bus, path_base, index,
               "11223344-5566-7788-99aa-bbccddeeffff", True)
    # Adding Notify/Click to the service
    self.add_characteristic(NotifyCharacteristic(bus, 0, self))
    self.add_characteristic(ClickCharacteristic(bus, 1, self))


class NotifyCharacteristic(Characteristic):
  notifying = False
  
  def __init__(self, bus, index, service):
        
    Characteristic.__init__(
                self, bus, index,
                "11223344-5566-7788-99aa-bbccddeeff00",
                ['read','notify'],
                service)
  
  def notify_instruction(self):
    global btleg

    for n in range(20):
      btleg.instruct[n] = btleg.instruct[n] & 0xFF
   
    value = dbus.Array([dbus.Byte(elem) for elem in btleg.instruct],'y')
  
    self.PropertiesChanged("org.bluez.GattCharacteristic1",
                              {'Value': value}, [])
    return self.notifying
    
     # make it visible over DBus
  def StartNotify(self):
    # starting notifications
    self.notifying = True

  def StopNotify(self):
    # stopping notifications
    self.notifying = False


class ClickCharacteristic(Characteristic):
       
  def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                "11223344-5566-7788-99aa-bbccddeeff01",
                ['write-without-response'],
                service)

  def WriteValue(self, value, options):
    global btleg
         
    retval = BTLE_CONTINUE      
    # GOT click pscket from Android
    if ("device" in options):
      device = btle_getdevice(options['device'])   # 'device' = path
    if device == 0:
      print("Got packet from unknown device")
      return
    
    text = ""
    member = 0
    dat = [int(elem) for elem in value]
  
    opcode = dat[0]
    
    if opcode == btleg.CLICK_ACK:
      btleg.totackwait = 0
      if btleg.devdat[device].ackwait != 0:
        if(btleg.devdat[device].sentcount != dat[1]):
          print("Transmission error")
        btleg.devdat[device].ackwait = 0
        btleg.devdat[device].sentcount = 0
        btleg.devdat[device].eventid = 0
        btle_devtimer(device,0)  # stop cmd timer
      btle_cmdbatch(0)    
    elif opcode == btleg.CLICK_ERROR:
      if(dat[2] != 0):
        if(dat[1] <= btleg.INST_MAX and dat[2] <= 7):
          print("*** ERROR btle_" + btle_ops[dat[1]] + 
                          " " + btle_errs[dat[2]])
        else:
          print("*** ERROR code " + str(dat[1]) + " errn " + str(dat[2]))
           
    elif opcode == btleg.CLICK_INIT:
      # GOT init packet 
      # dat[5]-[19] = name
      pdev = dat[4]
      if (pdev != 0 and pdev != device and  pdev <= btleg.maxdevice and
             (btleg.devdat[pdev].connected & 3) == 0  and  (btleg.devdat[pdev].connected & 0x10) != 0):
        # use previous device number
        # Swap  device  to  pdev
        btle_newdevice(btleg.devdat[device].path,pdev)
            
        btleg.devdat[pdev].secure = btleg.devdat[device].secure
        btleg.devdat[pdev].name = btleg.devdat[device].name
        btleg.devdat[pdev].address = btleg.devdat[device].address
        
        btleg.devdat[device].connected = 0
        btleg.devdat[device].path = ""
        device = pdev
      
      s = ""
      n = 0
      while(n < 15 and dat[n + 5] != 0):
        s = s + chr(dat[n + 5])
        n = n + 1
      if(n > 0):
        btleg.devdat[device].name = s 

      btleg.devdat[device].connected = 0x13     
      btle_nixcmds(device)

      btleg.devdat[device].protocol = dat[1]
      btleg.devdat[device].ackwait = 0
      btleg.devdat[device].sentcount = 0
      btleg.devdat[device].eventid = 0
      btleg.devdat[device].nextid = 1 
      btleg.devdat[device].cmdtimid = None
      btleg.devdat[device].cmdtimflag = False
      btleg.devdat[device].nexthandle = 0 
       
      print(btleg.devdat[device].name + " has connected as device " + str(device))  

      if dat[1] != btleg.BTLE_PROTOCOL:
        print("Different protocols - update so both are same")
        print("  This device=" + str(btleg.BTLE_PROTOCOL) + "  Other device=" + str(dat[1]))
                  
      btleg.instruct[0] = btleg.INST_INIT_REPLY
      btleg.instruct[1] = device
      btleg.instruct[2] = dat[2]
      btleg.instruct[3] = dat[3]
      btleg.instruct[4] = btleg.BTLE_PROTOCOL
      btleg.instruct[5] = btleg.flags & 255
      if(btleg.slave != 0):
        btleg.instruct[5] = btleg.instruct[5] | btleg.FLAG_SLAVE
        
      btleg.instruct[6] = (btleg.flags >> 8) & 255
      btleg.instruct[7] = (btleg.flags >> 16) & 255
      btleg.instruct[8] = 1   # Python server
      for n in range(9,20):
        btleg.instruct[n] = 0

      btleg.slave = btleg.slave & 1    
      btle_pushcmd(0) 
      btleg.totackwait = 0
      btle_newcmds(device,1)
      btle_cmdbatch(device)

      if btleg.slave != 0:
        btleg.devdat[device].secure = True
            
      if(btleg.devdat[device].secure == False):
        btle_text(device,"Password")
        btleg.devdat[device].pinhandle = btle_text_input(device,12)
      else:  
        btleg.devdat[device].pinhandle = 0
        retval = btleg.oneventcb(BTLE_CONNECT,device,0,0,"")
        
      if(btle_newcmds(device,3) == 0):
        btleg.instruct[0] = btleg.INST_PAINT
        btleg.instruct[1] = device
        for n in range(2,20):
          btleg.instruct[n] = 0
        btle_pushcmd(1)
        btle_newcmds(device,3)  
      btle_cmdbatch(device)
    
             
    elif(opcode == btleg.CLICK_BUTTON or opcode == btleg.CLICK_SELECT or 
         opcode == btleg.CLICK_TEXT or opcode == btleg.CLICK_CHECK):
      # click - will go to onEvent
      xhandle = dat[1]
      member = 0
      
      if(opcode == btleg.CLICK_TEXT and
               xhandle == (btleg.devdat[device].pinhandle & 0xFF) and
               btleg.devdat[device].secure == False):
        scode = 0
        if btleg.password != None and len(btleg.password) != 0:           
          if(dat[2] >= len(btleg.password)):
            n = 0
            while(n < 15 and n < len(btleg.password)):
              if ord(btleg.password[n]) != dat[n + 3]:
                scode = 1
              n = n + 1
          else:
            scode = 1
            
        if scode == 0:
          btleg.devdat[device].secure = True
          btleg.devdat[device].pinhandle = 0
          btleg.devdat[device].nexthandle = 0
          btle_clear(device)
          retval = btleg.oneventcb(BTLE_CONNECT,device,0,0,"")  
          
          if(btle_newcmds(device,3) == 0):
            btleg.instruct[0] = btleg.INST_PAINT
            btleg.instruct[1] = device
            for n in range(2,20):
              btleg.instruct[n] = 0
            btle_pushcmd(1)
            btle_newcmds(device,3)  
          
          btle_cmdbatch(device)

          if retval == BTLE_EXIT:
            # programmed exit
            if btleg.devdat[device].cmdtimflag == True:
              GLib.source_remove(btleg.devdat[device].cmdtimid)
              btleg.devdat[device].cmdtimflag = False
            btleg.mainloop.quit()
          return            
        else:
          if btleg.devdat[device].trycount < 2:
            btleg.devdat[device].trycount = btleg.devdat[device].trycount + 1
          else:
            btle_disconnect(device)
        return      
     
      if btleg.devdat[device].secure == False:
        return
      
      if(opcode == btleg.CLICK_BUTTON):
        event = BTLE_CLICK_BUTTON
      elif(opcode == btleg.CLICK_SELECT):
        event = BTLE_CLICK_SELECT
        member = dat[2]
      elif(opcode == btleg.CLICK_CHECK):
        event = BTLE_CLICK_CHECK
        member = dat[2]
      elif(opcode == btleg.CLICK_TEXT):
        if xhandle == 0:
          event = BTLE_BROADCAST
        else:
          event = BTLE_CLICK_TEXT 
        n = 0
        dn = 0
        while(n < dat[2] and n < 251):
          if(n < 17):
            text = text + chr(dat[n + 3])
          else:
            text = text + chr(btleg.devdat[device].data[dn])
            dn = dn + 1
          n = n + 1
             
      retval = btleg.oneventcb(event,device,
          xhandle | ((opcode & 0x7F) << 8) | (device << 16),member,text)
        
      if(btle_newcmds(device,3) == 0):
        btleg.instruct[0] = btleg.INST_PAINT
        btleg.instruct[1] = device
        for n in range(2,20):
          btleg.instruct[n] = 0
        btle_pushcmd(1)
        btle_newcmds(device,3)  
     
      btle_cmdbatch(device)
      # end clickable events  
    elif opcode == btleg.CLICK_RESTART:
      btleg.devdat[device].nexthandle = 0
      btle_clear(device)   
      retval = btleg.oneventcb(BTLE_CONNECT,device,0,0,"")
      
      if(btle_newcmds(device,3) == 0):
        btleg.instruct[0] = btleg.INST_PAINT
        btleg.instruct[1] = device
        for n in range(2,20):
          btleg.instruct[n] = 0
        btle_pushcmd(1)
        btle_newcmds(device,3)  
      
      btle_cmdbatch(device)
    elif(opcode == btleg.CLICK_DATA):
      # extra data to device store for later CLICK_TEXT
      dn = dat[1]  # block number 0-13
      if(dn < 14):
        dn = dn * 18   # data index
        for n in range(18):
          btleg.devdat[device].data[dn] = dat[n + 2]
          dn = dn + 1
      
    if retval == BTLE_EXIT:
      # programmed exit
      if(device != 0 and btleg.devdat[device].cmdtimflag == True):
        GLib.source_remove(btleg.devdat[device].cmdtimid)
        btleg.devdat[device].cmdtimflag = False
      btleg.mainloop.quit()            
   
    
    # end CLICK


def btle_timer(timerds):
  global btleg

  # start server timer
  # C devtimer(0,ds)
  if btleg.timerid != 0: 
    GLib.source_remove(btleg.timerid)
    btleg.timerid = 0
      
  tds = int(timerds)
  if(tds > 0):
    btleg.timerds = tds
  else:
    btleg.timerds = 0
    
  if btleg.timerds > 0:  
    btleg.timerid = GLib.timeout_add(btleg.timerds * 100,btle_timertick)
  return

def btle_timertick():
  global btleg
  
  # started by btle_timer(ds)
  # C operation == LE_TIMER 
  retval = btleg.oneventcb(SERVER_TIMER,0,0,0,"")
  if retval == BTLE_EXIT:
    btleg.mainloop.quit()
  btle_newcmds(0,0)
  btle_cmdbatch(0)
  if btleg.timerds > 0:  
    btleg.timerid = GLib.timeout_add(btleg.timerds * 100,btle_timertick)
  else:
    btleg.timerid = 0
  return

def btle_timeout(device):
  global btleg
  
  # started by devtimer(device,flag)
  # C operation == LE_BTLETIMER started by devtimer(node,ds)
  if (device < 1 or device > btleg.maxdevice):
    return
    
  if btleg.devdat[device].ackwait != 0:
    print("Transmission error")
      
    btleg.devdat[device].ackwait = 0
    btleg.devdat[device].sentcount = 0
    btleg.devdat[device].eventid = 0

  btleg.totackwait = 0
  btle_cmdbatch(0)
  return 
  
def btle_devtimer(device,flag):
  global btleg
  
  # C devtimer(node,ds) 
  if flag == 0:
    if btleg.devdat[device].cmdtimflag == True:
      GLib.source_remove(btleg.devdat[device].cmdtimid)
      btleg.devdat[device].cmdtimflag = False   
  else:
    if btleg.devdat[device].cmdtimflag == False:
      btleg.devdat[device].cmdtimid = GLib.timeout_add(btleg.clicktoms,
                btle_timeout,device)
      btleg.devdat[device].cmdtimflag = True
  return



def register_ad_cb():
    # Advertisement registered OK
    return
    
def register_ad_error_cb(error):
    print('Error: Failed to register advertisement: ' + str(error))
    btleg.mainloop.quit()

def register_app_cb():
    # GATT application registered
    return
    
def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    btleg.mainloop.quit()

def set_connected_status(path,conflag,conadd,coname):
  global btleg
  
  if conflag == 1:
    device = btle_newdevice(path,0)
    # New/exist device
  else:
    device = btle_getdevice(path)
    # Existing device 
  if device == 0:
    # Device not found 
    return
    
  if btleg.devdat[device].name == "":
    if coname != "":
      btleg.devdat[device].name = coname
      # Set name = coname
  if btleg.devdat[device].address == "":
    if conadd != "":
      btleg.devdat[device].address = conadd
      # Set address = conadd
    
  if conflag == 0:
    return
    
  if conflag == 1:
    # connected
    # C operation == LE_CONNECT
    btleg.devdat[device].connected = btleg.devdat[device].connected | 1
    btleg.devdat[device].nexthandle = 0
    btleg.devdat[device].ackwait = 0
    btleg.devdat[device].sentcount = 0
    btleg.devdat[device].eventid = 0
    btleg.devdat[device].nextid = 1
    btleg.devdat[device].cmdtimid = None
    btleg.devdat[device].cmdtimflag = False
    btleg.devdat[device].trycount = 0
    btleg.devdat[device].pinhandle = 0
 
    if btleg.password == None or len(btleg.password) == 0:
      btleg.devdat[device].secure = True
    else:
      btleg.devdat[device].secure = False
  elif conflag == 2:    # same as C operation = LE_DISCONNECT
    print(btleg.devdat[device].name + " has disconnected")
    btleg.devdat[device].connected = btleg.devdat[device].connected & 0x10
    if(btleg.devdat[device].cmdtimflag == True):
      GLib.source_remove(btleg.devdat[device].cmdtimid)
      btleg.devdat[device].cmdtimflag = False
 
    retval = btleg.oneventcb(BTLE_DISCONNECT,device,0,0,"")

    if retval == BTLE_EXIT:
      # programmed exit
      btleg.mainloop.quit()            
    else:
      flag = 0
      for n in range(1,btleg.maxdevice+1):
        if(btle_connected(n) != 0):
          flag = 1
      if(flag == 0):  
        print("Waiting for another connection (Ctl-C=exit)")           
   
      btle_nixcmds(device)
      btle_newcmds(device,0)  
      btle_cmdbatch(0)       
     
    
def properties_changed(interface, changed, invalidated, path):
    
  if (interface == "org.bluez.Device1"):
    if ("Connected" in changed):
      # Connected
      if changed['Connected'] == True:
        conflag = 1
      else:
        conflag = 2
    else:
      conflag = 0
    if("Address" in changed):
      conadd = changed['Address']
    else:
      conadd = ""
  
    if("Name" in changed):
      coname = changed['Name']
    else:
      coname = ""
          
    # Connect state = conflag
    set_connected_status(path,conflag,conadd,coname)

def interfaces_added(path, interfaces):
  global btleg
  
  if "org.bluez.Device1" in interfaces:
    properties = interfaces["org.bluez.Device1"]
     
    if ("Connected" in properties):
      # connected
      
      if properties['Connected'] == True:
        conflag = 1
      else:
        conflag = 2
      if("Address" in properties):
        conadd = properties['Address']
      else:
        conadd = ""
      if("Name" in properties):
        coname = properties['Name']
      else:
        coname = ""
          
      # Connect state = conflag
      set_connected_status(path,conflag,conadd,coname)
      
  return   


def btle_password(pword):
  global btleg
  
  if(len(pword) > 15):
    print("ERROR - Password max 15 chars")
    return(0)
  else:
    btleg.password = pword
  return(1)

def btle_slave():
  
  for n in range(1,btleg.maxdevice+1):
    if (btleg.devdat[n].connected & 3) != 0:
      print("ERROR - btle_slave must be called before any connection")
      return(0)
  
  btleg.slave = 1
  return(1)


def btle_message(device,mess):  
  global btleg
  
  dev = btle_b(device)

  if btle_devhandok(dev,0,btleg.INST_MESSAGE,0,0,0) == 0:
    return(0)
   
  for n in range(20):
    btleg.instruct[n] = 0
 
  xlen = len(mess)  # total length
  tlen = xlen       # this notify length
  if(xlen > 16):
    xlen = btle_extradata(dev,mess,16)
    tlen = 16
        
  btleg.instruct[0] = btleg.INST_MESSAGE
  btleg.instruct[1] = dev
  btleg.instruct[2] = 0  # message flag  
  btleg.instruct[3] = xlen
   
  for n in range(tlen):
    btleg.instruct[n + 4] = ord(mess[n])
  
  btle_pushcmd(0)
  return(1)
  


def btle_message_all(mess):  
  global btleg
    
  device = 0
  for n in range(1,btleg.maxdevice+1):
    if(device == 0 and btle_connected(n) == 1):
      device = n
        
  if(device == 0):
    return(0)
  
  dev = btle_b(device)

  if btle_devhandok(dev,0,btleg.INST_MESSAGE,0,0,0) == 0:
    return(0)
   
  for n in range(20):
    btleg.instruct[n] = 0
 
  xlen = len(mess)  # total length
  if(xlen > 16):
    print("Message_all too long - truncated")
    xlen = 16
    
    
  btleg.instruct[0] = btleg.INST_MESSAGE
  btleg.instruct[1] = dev
  btleg.instruct[2] = 2  # all flag
  btleg.instruct[3] = xlen
   
  for n in range(xlen):
    btleg.instruct[n + 4] = ord(mess[n])
  
  btle_pushcmd(0)
  return(1)


def btle_broadcast(mess):  
  global btleg
  
  device = 0
  for n in range(1,btleg.maxdevice+1):
    if(device == 0 and btle_connected(n) == 1):
      device = n
        
  if(device == 0):
    return(0)

  dev = btle_b(device)

  for n in range(20):
    btleg.instruct[n] = 0
 
  xlen = len(mess)  # total length
  if(xlen > 16):
    print("Broadcast too long - truncated")
    xlen = 16
    
    
  btleg.instruct[0] = btleg.INST_MESSAGE
  btleg.instruct[1] = dev
  btleg.instruct[2] = 1  # broadcast flag
  btleg.instruct[3] = xlen
   
  for n in range(xlen):
    btleg.instruct[n + 4] = ord(mess[n])
  
  btle_pushcmd(0)
  return(1)
  

def btle_text(device,text):
  global btleg

  dev = btle_b(device)

  if btle_devhandok(dev,0,btleg.INST_PROMPT,0,0,0) == 0:
    return(0)

  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)
      
  for n in range(20):
    btleg.instruct[n] = 0

  xlen = len(text)  # total length
  tlen = xlen       # this notify length
  if(xlen > 16):
    xlen = btle_extradata(dev,text,16)
    tlen = 16
    

  btleg.instruct[0] = btleg.INST_PROMPT
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  btleg.instruct[3] = xlen
  for n in range(tlen):
    btleg.instruct[n + 4] = ord(text[n])

    
  btle_pushcmd(1)
   
  return(xhandle | (btleg.INST_PROMPT << 8) | (dev << 16))
  
  

def btle_button(device,text):
  global btleg
      

  dev = btle_b(device)
  
  if btle_devhandok(dev,0,btleg.INST_BUTTON,0,0,0) == 0:
    return(0)

  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)
      
  for n in range(3,20):
    btleg.instruct[n] = 0
  
  btleg.instruct[0] = btleg.INST_BUTTON
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  tlen = len(text)
  if(tlen > 17):
    print("Button label too long - truncated")
    tlen = 17
 
  for n in range(tlen):
    btleg.instruct[n + 3] = ord(text[n])
   
  btle_pushcmd(1)

  return(xhandle | (btleg.INST_BUTTON << 8) | (dev << 16))



def btle_check(device,state):
  global btleg
      
  dev = btle_b(device)
    
  if btle_devhandok(dev,0,btleg.INST_CHECK,0,0,0) == 0:
    return(0)
    
  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)
      
  for n in range(4,20):
    btleg.instruct[n] = 0
  
  
  btleg.instruct[0] = btleg.INST_CHECK
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  btleg.instruct[3] = btle_b(state)
  
  btle_pushcmd(1)

  return(xhandle | (btleg.INST_CHECK << 8) | (dev << 16))
  
  

def btle_select(device,text):
  global btleg
    
  dev = btle_b(device)

  if btle_devhandok(dev,0,btleg.INST_SELECT,0,0,0) == 0:
    return(0)

  
  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)

  for n in range(20):
    btleg.instruct[n] = 0

  xlen = len(text)  # total length
  tlen = xlen       # this notify length
  if(xlen > 16):
    xlen = btle_extradata(device,text,16)
    tlen = 16
  
  btleg.instruct[0] = btleg.INST_SELECT
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  btleg.instruct[3] = xlen
  for n in range(tlen):
    btleg.instruct[n + 4] = ord(text[n])
   
   
  btle_pushcmd(1)
 
  return(xhandle | (btleg.INST_SELECT << 8) | (dev << 16))
 


def btle_text_input(device,width):
  global btleg
    
  dev = btle_b(device)

  if btle_devhandok(dev,0,btleg.INST_TEXT,0,0,0) == 0:
    return(0)

   
  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)

  for n in range(20):
    btleg.instruct[n] = 0
  
  btleg.instruct[0] = btleg.INST_TEXT
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  wid = btle_b(width)
  if(wid < 1):
    wid = 1
  elif(wid > 40):
    wid = 40
  btleg.instruct[3] = wid 
 
  btle_pushcmd(1)

  return(xhandle | (btleg.INST_TEXT << 8) | (dev << 16))


def btle_image(device,width,height,numlines,red,green,blue):
  global btleg
   
   
  if(width <= 0 or height <= 0 or numlines <= 0):
    print("ERROR btle_image parameter <= 0")
    return(0)
    
  dev = btle_b(device)
    
  if btle_devhandok(dev,0,btleg.INST_IMAGE,0,0,0) == 0:
    return(0)
 
  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)

  for n in range(11,20):
    btleg.instruct[n] = 0
          
  btleg.instruct[0] = btleg.INST_IMAGE
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  btleg.instruct[3] = btle_wl(width)
  btleg.instruct[4] = btle_wh(width)
  btleg.instruct[5] = btle_wl(height)
  btleg.instruct[6] = btle_wh(height)
  btleg.instruct[7] = btle_b(numlines)
  btleg.instruct[8] = btle_b(red)
  btleg.instruct[9] = btle_b(green)
  btleg.instruct[10] = btle_b(blue)
    
  btle_pushcmd(1)
         
  return(xhandle | (btleg.INST_IMAGE << 8) | (dev << 16))
  

def btle_image_line(device,xhandle,x0,y0,x1,y1,width,red,green,blue):
  global btleg
    
  if width <= 0:
    print("ERROR btle_image_line width <= 0")
    return(0)  
    
      
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_IMAGE_LINE,btleg.INST_IMAGE,0,0) == 0:
    return


  for n in range(15,20):
    btleg.instruct[n] = 0


  btleg.instruct[0] = btleg.INST_IMAGE_LINE
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_wl(x1)
  btleg.instruct[8] = btle_wh(x1)
  btleg.instruct[9] = btle_wl(y1)
  btleg.instruct[10] = btle_wh(y1)
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(width)

  btle_pushcmd(1) 
  return(1)
  

def btle_image_multiline(device,xhandle,x,y,start,end,
                         width,red,green,blue,pstyle,pwid):
  global btleg
      
  if width <= 0:
    print("ERROR btle_image_multiline width <= 0")
    return(0)  


  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_IMAGE_MULTILINE,
                                btleg.INST_IMAGE,0,0) == 0:
    return(0)

  deln = end - start - 1
  if(deln <= 0 or deln > 1088):
    print("Multiline start-end too small or too big (max 1090 points)")
    return(0)
       
  if(deln > 0):
    dn = start + 2  # first data point in extra data
    pn = 0        # data packet index 0-13
    xn = 20       # force new data packet on 1st loop
    tick = 0      # switch x/y lo/hi
    for n in range(deln * 4):
      if(xn == 20):
        # send data and start new packet
        if(n > 0):
          btle_pushcmd(0)
        btleg.instruct[0] = btleg.INST_DATA
        btleg.instruct[1] = btle_b(device)
        btleg.instruct[2] = btle_b(pn)    # xtra index
        pn = pn + 1
        xn = 3
     
      if(tick == 0):
        btleg.instruct[xn] = btle_wl(x[dn])
      elif(tick == 1):
        btleg.instruct[xn] = btle_wh(x[dn])
      elif(tick == 2):
        btleg.instruct[xn] = btle_wl(y[dn])
      else:
        btleg.instruct[xn] = btle_wh(y[dn])
        dn = dn + 1
      xn = xn + 1
      
      tick = (tick + 1) & 3         
    btle_pushcmd(0)
  
  btleg.instruct[0] = btleg.INST_IMAGE_MULTILINE
  btleg.instruct[1] = btle_b(device)
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x[start])
  btleg.instruct[4] = btle_wh(x[start])
  btleg.instruct[5] = btle_wl(y[start])
  btleg.instruct[6] = btle_wh(y[start])
  btleg.instruct[7] = btle_wl(x[start + 1])
  btleg.instruct[8] = btle_wh(x[start + 1])
  btleg.instruct[9] = btle_wl(y[start + 1])
  btleg.instruct[10] = btle_wh(y[start + 1])
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(width)
  btleg.instruct[15] = btle_wl(deln)
  btleg.instruct[16] = btle_wh(deln)
  btleg.instruct[17] = btle_b(pstyle)   # pts flag
  btleg.instruct[18] = btle_b(pwid)     # pts wid
  btleg.instruct[19] = 0
    
  btle_pushcmd(1) 
  return(1)



def btle_scale_data(x,y,start,end,xmin,xmax,ymin,ymax,
                      originx,originy,toprx,topry,px,py):

  if len(px) != 0 or len(py) != 0:
    print("btle_scale_data px/py lists must be empty")
    return(0)
    
  xb = btle_i(originx)
  yb = btle_i(originy)
  xt = btle_i(toprx)
  yt = btle_i(topry) 
 
  width = xt - xb
  if(width <= 0):
    print("ERROR btle_scale_data Top right to left of origin")
    return(0)
    
  height = yb - yt
  if(height <= 0):
    print("ERROR btle_scale_data Top right below origin")
    return(0)
 
  temp = xmax - xmin
  if(temp <= 0):
    print("ERROR btle_scale_data xmax <= xmin")
    return(0)
    
  xfac = width / temp  # float calc
  temp = ymax - ymin
  if(temp <= 0):
    print("ERROR btle_scale_data ymax <= ymin")
    return(0)
    
  yfac = height / temp  # float calc
  
  pn = 0
  flag = 0xF0  # last = break - start new line
  xp = [0 for n in range(2)]
  yp = [0 for n in range(2)] 
   
  for dn in range(start,end + 1):
    xp[0] = xp[1]  # old = last new
    yp[0] = yp[1] 
    xx = xb + (x[dn] - xmin) * xfac
    xp[1] = int(round(xx))
    yy = yb - (y[dn] - ymin) * yfac
    yp[1] = int(round(yy))
      
  
    if(xp[1] < xb):
      flag = flag | 1
    elif(xp[1] > xt):
      flag = flag | 2
    if(yp[1] > yb):
      flag = flag | 4
    elif(yp[1] < yt):
      flag = flag | 8
    
          
    if(flag == 0 or flag == 0xF0):
      # last and new pt in range
      # or last was break and new in range (new line start) 
      px.append(xp[1])
      py.append(yp[1])
      pn = pn + 1
    elif((flag & 0x0F) == 0 or (flag & 0xF0) == 0):
      # one in/one out of range - calc boundary intersection xs ys
      dx = xp[1] - xp[0]
      dy = yp[1] - yp[0]
      if((flag & 0xF0) != 0):
        n0 = 1  # last out of range - use new xp[1]
        cflag = flag >> 4 
      else:     # new out of range - use last xp[0]
        cflag = flag
        n0 = 0
        
      cflag = cflag & 0x0F 
        
      if((cflag & 1) != 0):
        xs = xb  # will cross xb axis
      elif((cflag & 2) != 0):
        xs = xt
      if((cflag & 4) != 0):
        ys = yb
      elif((cflag & 8) != 0):
        ys = yt
        
      if((cflag & 12) != 0 and dy != 0):
        # cross top/bot X axis at xs 
        xx = xp[n0] + (ys - yp[n0]) * dx / dy            
        xs = int(round(xx))
        if(xs >= xb and xs <= xt):
          cflag = 0  # found solution in range - stop ys soln
       
        
      if((cflag & 3) != 0 and dx != 0):
        # cross left/right Y axis at ys
        yy = yp[n0] + (xs - xp[n0]) * dy / dx
        ys = int(round(yy))
        if(ys >= yt and ys <= yb):
          cflag = 0  # found solution in range
        
        
      if(cflag == 0):
        if(n0 == 0):
          # new xp[1] out of range
          px.append(xs)   # end line at boundary
          py.append(ys)
          pn = pn + 1
          px.append(LINE_BREAK) 
          py.append(0)
          pn = pn + 1
          flag = 0x0F  # break flag
        else: 
          # old xp[0] out of range
          px.append(xs)   # start new line at boundary
          py.append(ys)
          pn = pn + 1
          px.append(xp[1])  
          py.append(yp[1])
          pn = pn + 1
    
      # else both out of range - no plot
  
        
    flag = (flag << 4) & 0xF0  


  # strip trailing line breaks
  while(pn > 0 and px[pn - 1] == LINE_BREAK):
    pn = pn - 1  

  if(pn == 0):
    if len(px) == 0:
      px.append(LINE_BREAK)
      py.append(0)
    else:  
      px[0] = LINE_BREAK
      py[0] = 0
    return(0)
        
  return(pn - 1)


def btle_image_arc(device,xhandle,x0,y0,x1,y1,
                   radius,route,width,red,green,blue):
  global btleg
      
  if width <= 0:
    print("ERROR btle_image_arc width <= 0")
    return(0)  
      
      
  dev = btle_b(device)
  xh = int(xhandle)
      
  if btle_devhandok(dev,xh,btleg.INST_IMAGE_ARC,btleg.INST_IMAGE,0,0) == 0:
    return(0)
      
  btleg.instruct[0] = btleg.INST_IMAGE_ARC
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_wl(x1)
  btleg.instruct[8] = btle_wh(x1)
  btleg.instruct[9] = btle_wl(y1)
  btleg.instruct[10] = btle_wh(y1)
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(width)
  btleg.instruct[15] = btle_wl(radius)
  btleg.instruct[16] = btle_wh(radius)
  btleg.instruct[17] = btle_b(route)
  btleg.instruct[18] = 0
  btleg.instruct[19] = 0
 
  btle_pushcmd(1)
  return(1)
   
  

def btle_image_rect(device,xhandle,x0,y0,x1,y1,red,green,blue,style,wid):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)
  
  if btle_devhandok(dev,xh,btleg.INST_IMAGE_RECT,btleg.INST_IMAGE,0,0) == 0:
    return(0)
  
  for n in range(16,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_IMAGE_RECT
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_wl(x1)
  btleg.instruct[8] = btle_wh(x1)
  btleg.instruct[9] = btle_wl(y1)
  btleg.instruct[10] = btle_wh(y1)
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(wid)
  btleg.instruct[15] = btle_b(style)

  btle_pushcmd(1)
  return(1)
  
  
  
def btle_image_circle(device,xhandle,x0,y0,radius,red,green,blue,style,wid):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)
  
  if btle_devhandok(dev,xh,btleg.INST_IMAGE_CIRCLE,btleg.INST_IMAGE,0,0) == 0:
    return(0) 

  for n in range(16,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_IMAGE_CIRCLE
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_wl(radius)
  btleg.instruct[8] = btle_wh(radius)
  btleg.instruct[9] = 0
  btleg.instruct[10] = 0
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(wid)
  btleg.instruct[15] = btle_b(style)

  btle_pushcmd(1)
  return(1) 
  
  

def btle_image_oval(device,xhandle,x0,y0,x1,y1,red,green,blue,style,wid):
  global btleg
      

  dev = btle_b(device)
  xh = int(xhandle)
  
  if btle_devhandok(dev,xh,btleg.INST_IMAGE_OVAL,btleg.INST_IMAGE,0,0) == 0:
    return(0)
 
  for n in range(16,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_IMAGE_OVAL
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_wl(x1)
  btleg.instruct[8] = btle_wh(x1)
  btleg.instruct[9] = btle_wl(y1)
  btleg.instruct[10] = btle_wh(y1)
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue)
  btleg.instruct[14] = btle_b(wid)
  btleg.instruct[15] = btle_b(style)
  
  btle_pushcmd(1)
  return(1) 
  

def btle_image_text(device,xhandle,text,x0,y0,dirn,font,size,red,green,blue):
  global btleg

  dev = btle_b(device)
  xh = int(xhandle)
 
  if btle_devhandok(dev,xh,btleg.INST_IMAGE_TEXT,btleg.INST_IMAGE,0,0) == 0:
    return(0)

  xlen = len(text)  # total length
  tlen = xlen       # this notify length
  if(xlen > 6):
    xlen = btle_extradata(device,text,6)
    tlen = 6  
  
  btleg.instruct[0] = btleg.INST_IMAGE_TEXT
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  btleg.instruct[3] = btle_wl(x0)
  btleg.instruct[4] = btle_wh(x0)
  btleg.instruct[5] = btle_wl(y0)
  btleg.instruct[6] = btle_wh(y0)
  btleg.instruct[7] = btle_b(dirn)
  btleg.instruct[8] = btle_b(font)
  btleg.instruct[9] = btle_b(size)
  btleg.instruct[10] = btle_b(xlen)
  btleg.instruct[11] = btle_b(red)
  btleg.instruct[12] = btle_b(green)
  btleg.instruct[13] = btle_b(blue) 
 
  for n in range(tlen):
    btleg.instruct[14 + n] = ord(text[n]) 

  btle_pushcmd(1)
  return(1) 
  
  
def btle_image_clear(device,xhandle):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_IMAGE_CLEAR,btleg.INST_IMAGE,0,0) == 0:
    return(0)      

  for n in range(3,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_IMAGE_CLEAR
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(xh & 0xFF)
  
  btle_pushcmd(1) 
  return(1)

  
def btle_newline(device):
  global btleg
  
  dev = btle_b(device)
  
  if btle_devhandok(dev,0,btleg.INST_NEWLINE,0,0,0) == 0:
    return(0)
  
  xhandle = btle_nextxhandle(dev)
  if(xhandle == 0):
    return(0)

  for n in range(20):
    btleg.instruct[n] = 0
  
  btleg.instruct[0] = btleg.INST_NEWLINE
  btleg.instruct[1] = dev
  btleg.instruct[2] = xhandle
  
  btle_pushcmd(1)

  return(xhandle | (btleg.INST_NEWLINE << 8) | (device << 16))


  
def btle_font(device,font):
  global btleg
  
  if(font < 0 or font > FONT_MAX):
    print("Invalid font")
    return(0)

  dev = btle_b(device)
 
  if btle_devhandok(dev,0,btleg.INST_SET_FONT,0,0,0) == 0:
    return(0)
 
  for n in range(20):
    btleg.instruct[n] = 0
    
  btleg.instruct[0] = btleg.INST_SET_FONT
  btleg.instruct[1] = dev
  btleg.instruct[2] = btle_b(font)
  
  btle_pushcmd(0)
  return(1)  

def btle_spacings(device,hpad,vpad,hspace,vspace):
 
  if(hpad < 0 or hpad > 20 or vpad < 0 or vpad > 20 or
     hspace < 0 or hspace > 20 or vspace < 0 or vspace > 20):
    print("Spacings parameter out of range 0-20")
    return(0)
    
  p = [0 for n in range(4)]
  p[0] = int(hpad)
  p[1] = int(vpad)
  p[2] = int(hspace)
  p[3] = int(vspace)  
  ret = btle_settings(device,p,4,0)
  return(ret)
  
def btle_message_buffer(device,bufsz):

  if(bufsz < 8 or bufsz > 250):
    print("Buffer size out of range (min 8)")
    return(0)
    
  p = [NO_CHANGE for n in range(5)]
  
  p[4] = int(bufsz)
    
  ret = btle_settings(device,p,5,0)
  return(ret)
  
def btle_connect_settings(device,tos,retry):
    
  if(tos < 1 or tos > 60 or retry < 0 or retry > 100):
    print("Connect settings out of range (tos=1-60 retry=0-100)")
    return(0)
    
  p = [NO_CHANGE for n in range(7)]
  
  p[5] = int(tos*10)
  p[6] = int(retry)
    
  ret = btle_settings(device,p,7,0)
  return(ret)
  


# Android data to dat[+2]
# len = 0 to 18

# 0 = hpad
# 1 = vpad
# 2 = hspace
# 3 = vspace
# 4 = bufsz
# 5 = connect to ds
# 6 = connect retry

 
  
def btle_settings(device,p,xlen,loclen):
  global btleg

  dev = btle_b(device)
  
  if btle_devhandok(dev,0,btleg.INST_SETTINGS,0,0,0) == 0:
    return(0)
  
  if(xlen <= 0 or xlen > 18):
    return(1)
  
  for n in range(2,20):
    btleg.instruct[n] = NO_CHANGE

  btleg.instruct[0] = btleg.INST_SETTINGS
  btleg.instruct[1] = dev
  for n in range(xlen):
    btleg.instruct[n+2] = btle_b(p[n])

  btle_pushcmd(1)
  return(1)
   
  

def btle_change_text(device,xhandle,text):
  global btleg
      
    
  dev = btle_b(device)
  xh = int(xhandle)
  
  if btle_devhandok(dev,xh,btleg.INST_CHANGE_TEXT,
         btleg.INST_PROMPT,btleg.INST_BUTTON,btleg.INST_SELECT) == 0:
    return(0)  
 
  for n in range(4,20):
    btleg.instruct[n] = 0
    
  xlen = len(text)  # total length
  tlen = xlen       # this notify length
  if(xlen > 16):
    xlen = btle_extradata(device,text,16)
    tlen = 16
  

  btleg.instruct[0] = btleg.INST_CHANGE_TEXT
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh
  btleg.instruct[3] = xlen

  for n in range(tlen):
    btleg.instruct[n + 4] = ord(text[n])
  
  
  btle_pushcmd(1)
  return(1)
    
  
def btle_change_colour(device,xhandle,red,green,blue):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_CHANGE_COLOUR,
                          btleg.INST_PROMPT,btleg.INST_BUTTON,btleg.INST_IMAGE) == 0:
    return(0)

  for n in range(6,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_CHANGE_COLOUR
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh
  btleg.instruct[3] = btle_b(red)
  btleg.instruct[4] = btle_b(green)
  btleg.instruct[5] = btle_b(blue)
 
  btle_pushcmd(1)
  return(1)
  
def btle_change_font(device,xhandle,font):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_CHANGE_FONT,
                   btleg.INST_PROMPT,btleg.INST_BUTTON,0) == 0:
    return(0)

  if(font < 0 or font > FONT_MAX):
    print("Invalid font")
    return(0)

   
  for n in range(4,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_CHANGE_FONT
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh
  btleg.instruct[3] = btle_b(font)
   
  btle_pushcmd(1)
  return(1)
 

def btle_change_check(device,xhandle,state):
  global btleg
      
  dev = btle_b(device)
  xh = int(xhandle)
  
  if btle_devhandok(dev,xh,btleg.INST_CHANGE_CHECK,btleg.INST_CHECK,0,0) == 0:
    return(0)
     
  for n in range(4,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_CHANGE_CHECK
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh
  btleg.instruct[3] = btle_b(state)
   
  btle_pushcmd(1)
  return(1)
  

def btle_remove(device,xhandle):
  global btleg
  
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_REMOVE,-1,0,0) == 0:
    return(0)

   
  for n in range(3,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_REMOVE
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh & 0xFF
  btle_pushcmd(1)
  return(1)
  
  
def btle_restore(device,xhandle):
  global btleg
  
  
  dev = btle_b(device)
  xh = int(xhandle)

  if btle_devhandok(dev,xh,btleg.INST_RESTORE,-1,0,0) == 0:
    return(0)
   
  for n in range(3,20):
    btleg.instruct[n] = 0

  btleg.instruct[0] = btleg.INST_RESTORE
  btleg.instruct[1] = dev
  btleg.instruct[2] = xh & 0xFF
 
  btle_pushcmd(1)
  return(1)
  
def btle_connected(device):
  if btle_deviceokc(device,0):
    return 1
  return 0  
    
def btle_maxdevice():
  global btleg
  return(btleg.maxdevice)
      
def btle_local_name():
  global btleg
  return(btleg.name)
  
def btle_local_address():
  global btleg
  return(btleg.address)    
      
def btle_name(device):
  global btleg
  
  if btle_deviceok(device,0):
    return btleg.devdat[device].name      
  return ""
  
def btle_address(device):
  global btleg
  
  if btle_deviceok(device,0):
    return btleg.devdat[device].address      
  return ""
       
  
def btle_disconnect(device):
  global btleg
  
  if btle_deviceokc(device,0) == False:
    return(0)
 
  bus = dbus.SystemBus()
  proxy = bus.get_object("org.bluez",btleg.devdat[device].path)
  interface = dbus.Interface(proxy,"org.bluez.Device1")
  interface.Disconnect()
  btleg.devdat[device].connected = btleg.devdat[device].connected & 0x10
      # can re-connect as previous device

  return(1)
  
def btle_clear(device):
  global btleg


  dev = btle_b(device)
  
  if btle_devhandok(dev,0,btleg.INST_CLEAR,0,0,0) == 0:
    return(0)
  
  
  for n in range(2,20):
    btleg.instruct[n] = 0
  
  btleg.instruct[0] = btleg.INST_CLEAR
  btleg.instruct[1] = dev
  btleg.devdat[dev].nexthandle = 0   

  btle_pushcmd(1)
  return(1)  
  
def btle_handles():
  new = [0 for n in range(256)]
  return new
  

def btle_extradata(device,s,len0):
  global btleg
  
  if btle_deviceokc(device,0) == False:
    return(0)

    
  tlen = len(s)
  nx = (tlen - len0) // 17
  rem = (tlen - len0) % 17
  if(rem > 0):
   nx = nx + 1
  if(nx > 14):
    print("Text " + s[0:6] + "... too long - truncated")
    nx = 14
    tlen = 238 + len0
 

  btleg.instruct[0] = btleg.INST_DATA
  btleg.instruct[1] = device
  retlen = len0 
  tlen = tlen - len0  
  sn = len0
  for n in range(nx):
    
    btleg.instruct[2] = n
    
    if(tlen > 17):
      dlen = 17
    else:
      dlen = tlen

    for k in range(3,20):
      btleg.instruct[k] = 0
  
    for k in range(dlen):
      btleg.instruct[k + 3] = ord(s[sn])
      sn = sn + 1
               
    btle_pushcmd(0)

    tlen = tlen - dlen
    retlen = retlen + dlen
    
  return(retlen)  


def btle_newcmds(device,flag):
  global btleg
  
  
  btle_cleanstack()    
  btle_sortstack()
  
  devcount = 0     
  # search stack for each device with its current nextid - must be new
  dn = 1
  while(dn < 255 and dn < len(btleg.devdat)):
    id = btleg.devdat[dn].nextid
    paintflag = 0
    count = 0
    n = 0
    
    while(n < btleg.stn):  
      if(btleg.stack[n + 1] == dn and btleg.stack[n + 20] == id):
        # new entry for this device
        count = count + 1
        if dn == device:
          devcount = devcount + 1
        if((btleg.stack[n + 21] & 1) != 0):
          paintflag = 1
        
        btleg.stack[n + 21] = btleg.stack[n + 21] | paintflag
          # all subsequent in block   
        
        if((count % btleg.batchcount) == 0):
          btleg.stack[n + 21] = btleg.stack[n + 21] | 2
              # end of batch - ACK request  
          if((count % (btleg.batchcount * btleg.blockcount)) == 0):
            # force unlock/paint every blockcount batches
            btleg.stack[n + 21] = btleg.stack[n + 21] | 4 
               # end of block - add unlock
            paintflag = 0
              
        lastn = n + 21
      n = n + 22
      # stack entry loop
       
      
    if(count != 0):  # new nextid cmds on stack
        
      btleg.stack[lastn] = btleg.stack[lastn] | (8 + 4 + 2 + paintflag)
        # paint/ack/unlock/unclick
      
      # finished with this nextid
               
      if(btleg.devdat[dn].nextid == 255):
        btleg.devdat[dn].nextid = 1
      else:
       btleg.devdat[dn].nextid = btleg.devdat[dn].nextid + 1   
             
    dn = dn + 1
    # next device loop
          
  return(devcount)            

 

def btle_cleanstack():
  global btleg
  # clean up stack remove invalid and disconnected devices
  n = 0
  while(n < btleg.stn):
    if(btle_deviceokc(btleg.stack[n + 1],0) == False or 
            (btleg.devdat[btleg.stack[n + 1]].connected & 3) == 0):
      btle_xcmd(n)
    else:           
      n = n + 22
  return

def btle_cmdbatch(prioritydev):
  global btleg
 
     
  if(btleg.totackwait > 0 or btleg.stn == 0):
    return  # waiting for acks or empty stack


  btle_cleanstack()
  btle_devstack(prioritydev)
  
  
  count = 0  
  n = 0
  getout = 0
  while(n < btleg.stn and getout == 0 and count < btleg.batchcount + 2):
    # check count for safety
    device = btleg.stack[n + 1]  
    eid = btleg.devdat[device].eventid
    id = btleg.stack[n + 20]
    flag = 1
    if(eid == 0):   # start sending new id 
      btleg.devdat[device].eventid = id
      btleg.devdat[device].sentcount = 0      
    elif(eid != id or btleg.devdat[device].ackwait != 0):
      flag = 0   # no send
    
    if(flag != 0):
      count = count + 1

      for k in range(20):
        btleg.instruct[k] = btleg.stack[k + n] & 0xFF

      if(btleg.instruct[0] == btleg.INST_MESSAGE and btleg.instruct[2] == 2):
        mflag = 1
      else:
        mflag = 0

      if(btleg.instruct[0] != btleg.INST_ACKREQUEST and mflag == 0): 
        btleg.devdat[device].sentcount = btleg.devdat[device].sentcount + 1

      
      btleg.chrnotify.notify_instruction()
 
      # is next an ACK for this device/id 
      # if so, let it run, do not terminate via batchcount
      nextisack = 0        
        
      if(n + 22 == btleg.stn or (btleg.stack[n + 21] & 2) != 0 or
                  (count >= btleg.batchcount and nextisack == 0)):
        if(count >= btleg.batchcount):
          getout = 1  # getout must be on ACK request already on stack
             # or forced by batchcount or forced by end of stack btlestn
        btleg.devdat[device].ackwait = 1
              # stop more sends from this device until get ACK
        btleg.totackwait = 1  
        btleg.stack[n + 21] = btleg.stack[n + 21] | 2 
           # ACK request in case end of stack or batchcount
          
        for k in range(7,20):
          btleg.instruct[k] = 0
    
        btleg.instruct[0] = btleg.INST_ACKREQUEST
        
        btleg.instruct[1] = device
        btleg.instruct[2] = ((btleg.stack[n + 21] >> 3) & 1) & 0xFF 
           # unclick
        btleg.instruct[3] = ((btleg.stack[n + 21] >> 2) & 1) & 0xFF
           # unlock to + paint
        btleg.instruct[4] = ((btleg.stack[n + 21] >> 1) & 1) & 0xFF
           # ack request
        btleg.instruct[5] = (btleg.stack[n + 21] & 1) & 0xFF
           # paint
        btleg.instruct[6] = btleg.devdat[device].sentcount
             
 
        btle_devtimer(device,1)
        btleg.chrnotify.notify_instruction()
     
          
      btle_xcmd(n)
      # emd flag != 0 
    else:
      n = n + 22
    # next stack entry loop   
 
  return
    
  

def btle_pushcmd(paintflag):
  global btleg
    
  if btleg.slave != 0:
    if((btleg.slave & 2) != 0):
      return
    if(btleg.instruct[0] != btleg.INST_INIT_REPLY and
                  btleg.instruct[0] != btleg.INST_PAINT):
      return  
    if(btleg.instruct[0] == btleg.INST_PAINT):
      btleg.slave = btleg.slave | 2
      
    
  if(btleg.stn >= 8180):
    print("Too many items")
    return
          
  device = btleg.instruct[1]
  if(btle_deviceokc(device,0) == False):
    return
               
  for n in range(20):
    btleg.stack[btleg.stn + n] = btleg.instruct[n]
  
  if paintflag == 0:
    n = 0
  else:
    n = 1
    
  btleg.stack[btleg.stn + 20] = btleg.devdat[device].nextid
  btleg.stack[btleg.stn + 21] = n
  btleg.stn = btleg.stn + 22
  return
    


def btle_nixcmds(device):
  global btleg
   
  if(btleg.stn == 0):
    return
  n = btleg.stn - 22
  while(n >= 0):
    if(btleg.stack[n + 1] == device):
      btle_xcmd(n)    
    n = n - 22
  return    


def btle_xcmd(sn):
  global btleg
    
  if(btleg.stn == 0 or sn >= btleg.stn):
    return

  n = sn
  while n < btleg.stn - 22:
    btleg.stack[n] = btleg.stack[n + 22]
    n = n + 1
    
  btleg.stn = btleg.stn - 22      
  return


def btle_sortstack():
  global btleg
  
  # consolidate new entries
  
  sn0 = 0
     
  # find first new entry
  getout = 1
  while getout != 0:
    n = sn0    # first possible new unsorted entry
    getout = 0
    while(n < btleg.stn and getout == 0):
      device = btleg.stack[n + 1]
      if(btleg.stack[n + 1] == device and
                 btleg.stack[n + 20] == btleg.devdat[device].nextid):
        sn = n  # new entry for this device
        getout = 1     
      n = n + 22
     
    if(getout != 0):
      sn0 = btle_sortdevice(device,sn)
          
  return 
 



def btle_sortdevice(dev,sn):
  global btleg 
 
  sn0 = sn + 22
  getout = 0
  while getout == 0:
    n = sn0
    n0 = 0  # first non-dev
    n1 = 0  # following dev
    while(n < btleg.stn and (n0 == 0 or n1 == 0)):
      if(n0 == 0):
        if(btleg.stack[n + 1] != dev):
          n0 = n
      else:
        if(btleg.stack[n + 1] == dev):
          n1 = n 
      n = n + 22
      
    if(n0 == 0 or n1 == 0):
      getout = 1
    else:
      #  swap n1 to n0, shift n0 to (n1-1) up
      for k in range(22):
        sav = btleg.stack[n1 + k]
        for j in range(n1,n0,-22):
          btleg.stack[j + k] = btleg.stack[j + k - 22]
        btleg.stack[n0 + k] = sav        
      sn0 = n0 + 22
      
  return(sn0)    
 


def btle_devstack(device):
  # move priority device block to bottom of stack

  if(device == 0):
    return
     
  count = 0
  n = 0   
  while(n < btleg.stn):
    if(btleg.stack[n + 1] == device):
      if(count == 0):
        n0 = n
        n1 = n
      else:
        n1 = n
      count = count + 1
    n = n + 22
  
  if(count > 0 and n0 > 0):
    # is device block above [0] shift n1-n0 to bottom
    for sn in range(count):
      # shift n1 to bottom
      for k in range(22):
        sav = btleg.stack[n1 + k]
        j = n1
        while(j > 0):
          btleg.stack[j + k] = btleg.stack[j + k - 22]
          j = j - 22
        btleg.stack[k] = sav
  return  



# convert float or int to byte
def btle_b(x):
  if x < 0 or x > 255:
    print("Parameter out of range 0-255")
    return(0)
  if isinstance(x,float):
    nx = int(round(x))
  else:
    nx = x
  return(nx)
  
# hi byte of word or float
def btle_wh(x):
  if x < -32768 or x > 32767:
    print("Parameter out of range +/-32767")
    return(0)
  if isinstance(x,float):
    nx = int(round(x))
  else:
    nx = x
  return((nx >> 8) & 0xFF)
  
# lo byte of word or float
def btle_wl(x):
  if isinstance(x,float):
    nx = int(round(x))
  else:
    nx = x
  return(nx & 0xFF)

# convert float to int
def btle_i(x):
  if isinstance(x,float):
    nx = int(round(x))
  else:
    nx = x
  return(nx)




def btle_devhandok(device,handle,op,parentop,pop2,pop3):
   
  dev = btle_b(device)
  if btle_deviceokc(dev,0) == False:
    print("Invalid device " + str(device) + " in btle_" + btle_ops[op])
    return(0)
   
  if parentop == 0:
    return(1) 
  
  xh = int(handle)
  devh = (xh >> 16) & 0xFF
  if(devh != dev):
    if btle_deviceok(devh,0) == False:
      print("Invalid handle in btle_" + btle_ops[op])
    else:
      print("btle_" + btle_ops[op] +
            " error - Handle belongs to device " + str(devh))
    return(0)

  if((xh & 0xFF) == 0):
    print("Invalid handle in btle_" + btle_ops[op])
    return(0)

  if parentop == -1:
    return(1)
       
  hop = (xh >> 8) & 0xFF 
  if(hop != parentop and hop != pop2 and hop != pop3):
    if(pop2 == 0 and pop3 == 0):
      print("Not a btle_" + btle_ops[parentop] +
                  " handle in btle_" + btle_ops[op])
    else:
      print("Cannot call btle_" + btle_ops[op] +
                  " for item with specified handle")
    return(0)
    

  return(1)
  


def btle_deviceok(device,pflag):
  global btleg
  
  if(device < 1 or device > 254 or device > btleg.maxdevice):
    if pflag != 0:  
      print("Invalid device " + str(device))
    return False
  return True
    
def btle_deviceokc(device,pflag):
  global btleg
 
  if btle_deviceok(device,pflag) == False:
    return False
       
  if (btleg.devdat[device].connected & 3) != 0:  
    return True
  #  not connected
  return False


def btle_newdevice(path,n0):
  global btleg

  if n0 != 0:
    dn = n0
  else:   
    dn = btle_getdevice(path)
    if dn == 0:   
      dn = 1
      while(dn <= btleg.maxdevice and btleg.devdat[dn].connected != 0): 
        dn = dn + 1
      if dn == 255:
        dn = 1
        while(dn <= btleg.maxdevice and (btleg.devdat[dn].connected & 3) != 0): 
          dn = dn + 1
          
        if dn == 255:
          print("Too many connected devices")
          return(0)
        btleg.devdat[dn].connected = 0  
        
 
  if dn > btleg.maxdevice:
    btleg.maxdevice = dn
    btleg.devdat.append(clientdata())

  btleg.devdat[dn].path = path
  btleg.devdat[dn].connected = btleg.devdat[dn].connected & 0x10
  btleg.devdat[dn].protocol = 0
  btleg.devdat[dn].nexthandle = 0
  btleg.devdat[dn].ackwait = 0
  btleg.devdat[dn].sentcount = 0
  btleg.devdat[dn].secure = False
  btleg.devdat[dn].trycount = 0
  btleg.devdat[dn].pinhandle = 0
  btleg.devdat[dn].eventid = 0
  btleg.devdat[dn].nextid = 1
  btleg.devdat[dn].cmdtimid = None
  btleg.devdat[dn].cmdtimflag = False
  btleg.devdat[dn].name = ""
  btleg.devdat[dn].address = ""
  for k in range(256):
    btleg.devdat[dn].data[k] = 0
  return(dn)


def btle_getdevice(path):
  global btleg
  
  for n in range(1,btleg.maxdevice+1):
    if btleg.devdat[n].path == path:
      return(n)
  return(0)

def btle_nextxhandle(device):
  global btleg
  
  btleg.devdat[device].nexthandle = btleg.devdat[device].nexthandle + 1
  if btleg.devdat[device].nexthandle >= 256:
    print("Run out of handles")
    return(0)
  
  return(btleg.devdat[device].nexthandle)

  



def btle_server(callback,name):
  return(btle_server_ex(callback,name,0))
  
def btle_server_ex(callback,name,hci):
  global btleg
  
  # need python 3.5 or higher
  assert sys.version_info >= (3,5)
  
  btleg = globaldata()

  hcix = hci & 0xFF
  if hcix != 0:
    print("Using hci" + hcix + " (not on-board hci0)") 
  
  btleg.hci = hcix
  if callback == None:
    print("No callback")
    return(0)
    
  btleg.oneventcb = callback
  btleg.name = name
  
  btleg.flags = 0
    
  btleg.devdat.append(clientdata())  # device 0 not used 

  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
  bus = dbus.SystemBus()
  btleg.mainloop = GLib.MainLoop()
  # we're assuming the adapter supports advertising
  adapter_path = "/org/bluez/hci" + str(hcix)
    
  adv_mgr_interface = dbus.Interface(bus.get_object("org.bluez",adapter_path),
                     "org.bluez.LEAdvertisingManager1")

  service_manager = dbus.Interface(
        bus.get_object("org.bluez", adapter_path),
        "org.bluez.GattManager1")
  
  bus.add_signal_receiver(properties_changed,
        dbus_interface="org.freedesktop.DBus.Properties",
        signal_name="PropertiesChanged",
        path_keyword="path")

  bus.add_signal_receiver(interfaces_added,
        dbus_interface='org.freedesktop.DBus.ObjectManager',
        signal_name="InterfacesAdded")

  # we're only registering one advertisement object
  # so index (arg2) is hard coded as 0
  adv_mgr_interface = dbus.Interface(bus.get_object("org.bluez",adapter_path),
                   "org.bluez.LEAdvertisingManager1")
  btleg.adv = Advertisement(bus, 0, 'peripheral')

    
  # start advertising
  # Register advertisement
  advertising = True
  adv_mgr_interface.RegisterAdvertisement(btleg.adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)

  app = Application(bus)
 
  # Register GATT application
  service_manager.RegisterApplication(app.get_path(), {},
                                reply_handler=register_app_cb,
                                error_handler=register_app_error_cb)
 
  if btleg.timerds > 0:
    btleg.timerid = GLib.timeout_add(btleg.timerds * 100,btle_timertick)
  
  obj = bus.get_object("org.bluez","/org/bluez/hci0") 
  interface = dbus.Interface(obj,"org.freedesktop.DBus.Properties")
  try:
    btleg.address = interface.Get("org.bluez.Adapter1","Address")
  except:
    btleg.address = "Unknown address" 
      
  print("Version " + str(btleg.BTLE_VERSION) + "  Protocol " + str(btleg.BTLE_PROTOCOL))
  print("Waiting for BeetleIN Android apps to connect (Ctl-C stops)")
  print("Advertising as " + btleg.address + " " + btleg.name)  

  btleg.oneventcb(SERVER_START,1,0,0,name)

  try:
    btleg.mainloop.run()
  except KeyboardInterrupt:
    advertising = False
    adv_mgr_interface.UnregisterAdvertisement(btleg.adv.get_path())
    print("\nUnprogrammed exit")
          
  if advertising == True:
    adv_mgr_interface.UnregisterAdvertisement(btleg.adv.get_path())
    print("Programmed exit")

  for n in range(1,btleg.maxdevice + 1):
    if btle_connected(n) == 1:
      btle_disconnect(n)

  return(1)
