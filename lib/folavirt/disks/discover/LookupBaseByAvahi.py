#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import dbus
import avahi
import gobject
from dbus.mainloop.glib import DBusGMainLoop, threads_init

from threading import Thread
from folavirt.networking.NetworkInterface import NetworkInterface

class LookupBaseByAvahi():
    base = []
    
    def __init__(self):
        loop = DBusGMainLoop()
        
        self.bus = dbus.SystemBus(mainloop=loop)
        
        raw_server = self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        self.server = dbus.Interface(raw_server, avahi.DBUS_INTERFACE_SERVER)
        
        self.browser = dbus.Interface(
                    self.bus.get_object(
                            avahi.DBUS_NAME, 
                            self.server.ServiceBrowserNew(
                                    NetworkInterface().getIndex(),
                                    avahi.PROTO_UNSPEC,
                                    '_folavirt_baseiqn._tcp',
                                    'local',
                                    dbus.UInt32(0)
                            )
                    ),
                    avahi.DBUS_INTERFACE_SERVICE_BROWSER
                )
        
        dbus.mainloop.glib.threads_init()
        self.browser.connect_to_signal('ItemNew', self.handler)
        gobject.threads_init()
        self.main_loop = gobject.MainLoop()
        t = Thread(target=self.main_loop.run)
        t.daemon = True
        t.start()
        
    def handler(self, interface, protocol, name, stype, domain, flags):
        self.server.ResolveService(
                interface, 
                protocol, 
                name, 
                stype, 
                domain, 
                avahi.PROTO_INET, 
                dbus.UInt32(0), 
                reply_handler=self.service_resolved, 
                error_handler=self.print_error
            )
    
    def service_resolved(self, interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags):
        self.base.append({'iqn' : name, 'address' : address})
    
    def getBase(self):
        return self.base

    def print_error(self, err):
        print "Avahi discover error:", str(err)
 
    def kill(self):
        self.main_loop.quit()