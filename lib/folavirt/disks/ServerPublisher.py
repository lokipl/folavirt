#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
from ConfigParser import ConfigParser

from folavirt.networking.AvahiBroadcaster import AvahiBroadcaster
from folavirt.disks.iscsi.Configuration import Configuration
from folavirt.disks.iscsi.Partitions import Partitions

class ServerPublisher():
    def __init__(self, serviceport):
        parser = ConfigParser()
        parser.readfp(open("../etc/folavirt.ini"))
        
        # Port z serwerem iSCSI
        self.port = int(parser.get("tgt", "port"))
        # Port usługi
        self.serviceport = serviceport
        # Konfiguracja iSCSI zapisana w bazie danych
        self.conf = Configuration()
        
        self.broadcasters = []
        
        self.init()
    
    def init(self):
        """
        Rozgłaszanie informacji o zarządcy dyskami
        
        @param void
        @return void
        """
        broadcaster = AvahiBroadcaster('Folavirt iSCSI on '+socket.gethostname(),'_folavirt_iscsi._tcp', self.serviceport)
        broadcaster.publish()
     
    def publishDisks(self):
        """
        Rozgłaszanie dysków poprzez Avahi
        
        @param void
        @return void
        """
        # Generowanie ciągu iqn
        iqn = "iqn." + self.conf.getIqndate() + "." + self.conf.getIqnhostname() + ""
        
        # Rozgłaszanie puli z dyskami bazowymi
        broadcaster = AvahiBroadcaster(iqn + ":" + self.conf.getIqnbasename() ,'_folavirt_baseiqn._tcp', self.port)
        broadcaster.publish()
        self.broadcasters.append(broadcaster)
        
        # Rozgłaszanie każdej z puli dysków bazowych
        for base in Partitions().getBaseList():
            broadcaster = AvahiBroadcaster(iqn + ":snapshots_" + base.getName(), '_folavirt_snapshotsiqn._tcp', self.port)
            broadcaster.publish()
            self.broadcasters.append(broadcaster)
    
    def republish(self):
        """
        Na nowo publikuje dyski
        
        @param void
        @return void
        """
        for broadcaster in self.broadcasters:
            broadcaster.unpublish()
            del broadcaster
        
        self.broadcasters = []
        self.publishDisks()
        
        
