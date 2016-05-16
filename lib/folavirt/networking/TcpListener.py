#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import threading

from folavirt.networking.TcpListenerThreaded import TcpListenerThreaded

class TcpListener():
    host = "0.0.0.0"
    port = 7002
    
    listener = 0
    listenerthread = 0
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        pass
    
    def setListen(self, classname):
        self.listener = TcpListenerThreaded((self.host, self.port), classname)
        
        self.listenerthread = threading.Thread(target=self.listener.serve_forever)
        self.listenerthread.start()
        
        pass