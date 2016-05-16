#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import dbus
import avahi
import socket

from folavirt.networking.NetworkInterface import NetworkInterface

"""
Klasa służy do rozgłąszania czegoś poprzez Avahi
"""
class AvahiBroadcaster():
    def __init__(self, name, avahiname, avahiport):
        self._service_name = name
        self.avahiname = avahiname
        self.avahiport = avahiport
        
        self.bus = dbus.SystemBus()
        
        raw_server = self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        self.server = dbus.Interface(raw_server, avahi.DBUS_INTERFACE_SERVER)
        
        self.group = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
    

    """
    Publikuj
    """ 
    def publish(self):
        self.group.AddService(
                              NetworkInterface().getIndex(), 
                              avahi.PROTO_INET, 
                              0, 
                              self._service_name, 
                              self.avahiname,
                              '',
                              '',
                              self.avahiport,
                              ''
                        )
        self.group.Commit()
            
    def unpublish(self):
        self.group.Reset()