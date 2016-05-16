#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import commands

from folavirt.networking.Response import Response
from folavirt.disks.iscsi.ImportIscsiPool import ImportIscsiPool

class IscsiResponses():
    def __init__(self, q):
        self.q = q
        self.uri = 'qemu:///system'
        
    def getResponse(self):
        # Odświeżenie zasobów iscsi
        if self.q.getCommand() == "iscsi-add":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("iscsi-add")
             
            # Ścieżka początkowa aplikacji
            output = commands.getoutput(os.path.abspath(os.getcwd() + '/../sbin/folaiscsidiscover'))
             
            # Przekazywanie wyniku do obiektu przetwarzającego wynik
            ImportIscsiPool(json.loads(output))
             
            # Zwrócenie odpowiedzi
            return r
        
        if self.q.getCommand() == "iscsi-sync":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("iscsi-sync")
             
            # Ścieżka początkowa aplikacji
            output = commands.getoutput(os.path.abspath(os.getcwd() + '/../sbin/folaiscsidiscover'))
             
            # Przekazywanie wyniku do obiektu przetwarzającego wynik
            importpools = ImportIscsiPool(json.loads(output), True)
            r.setData({'added':importpools.added, 'removed':importpools.removed})
            
            # Zwrócenie odpowiedzi
            return r
        
        return None