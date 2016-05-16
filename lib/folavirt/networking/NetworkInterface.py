#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ctypes
import ctypes.util
import avahi

from ConfigParser import ConfigParser

class NetworkInterface():
    def __init__(self):
        parser = ConfigParser()
        parser.read('../etc/folavirt.ini')
        
        self.name = parser.get('folavirt', 'interface')
    
    def getIndex(self):
        libc = ctypes.CDLL(ctypes.util.find_library('c'))
        idx = libc.if_nametoindex(self.name)
        if not idx:
            return avahi.IF_UNSPEC
        return idx
        