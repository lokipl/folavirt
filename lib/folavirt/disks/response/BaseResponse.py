#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.networking.Response import Response
from folavirt.disks.iscsi.Partitions import Partitions
from folavirt.disks.iscsi.Configuration import Configuration

class BaseResponse():
    def __init__(self, q):
        self.conf = Configuration()
        self.q = q
        
    def getResponse(self):
        # Lista baz
        if self.q.getCommand() == "getbasevolumes":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('getbasevolumes')
            r.setData([x.getName() for x in Partitions().getBaseList()])
            
            return r
        
        # Nazwa zasobu iSCSI z pulami bazowymi
        if self.q.getCommand() == "getbaseiqn":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("getbaseiqn")
            r.setData("iqn." + self.conf.getIqndate() + "." + self.conf.getIqnhostname() + ":" + self.conf.getIqnbasename())
            
            return r
        
        return None