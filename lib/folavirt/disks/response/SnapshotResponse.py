#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from folavirt.networking.Response import Response
from folavirt.disks.iscsi.Snapshot import Snapshot
from folavirt.disks.iscsi.Snapshots import Snapshots
from folavirt.disks.iscsi.Partitions import Partitions
from folavirt.disks.iscsi.Tgt import Tgt

class SnapshotResponse():
    def __init__(self, q):
        self.q = q
        
    def getResponse(self):
        # Tworzenie snapshotów
        if self.q.getCommand() == "createsnapshot":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("createsnapshot")
            
            # Pobieranie opcji
            options = self.q.getData()
            
            # Szukanie bazy
            base = Partitions().getBaseByName(options['base'])

            # Tworzenie snapshota
            status = Snapshots().createFromBase(base, options['size'])
            if not status:
                r.setErrorCode(1) 
            
            # Uaktualnianie konfiguracji tgt
            Tgt().writeConfig()
            
            return r
        
        # Usuwanie snapshotów
        if self.q.getCommand() == "removebasesnapshot":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("removebasesnapshot")
            
            # Tworzy obiekt bazy
            base = Partitions().getBaseByName(self.q.getData())
            
            # Usuwanie wszystkich snapshotów z bazy woluminu
            removed = 0
            for snapshot in base.getSnapshots():
                snapshot.remove()
                removed+=1
                
            # Dodawanie ilości usuniętych snapshotów
            r.setData(removed)
                
            return r
        
        
        # Usuwanie konkretnych snapshotów
        if self.q.getCommand() == "removeparticualsnapshot":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("removeparticualsnapshot")
            
            print "Test"
            # Szukanie vg na którym jest baza
            vg = ""
            for base in Partitions().getBaseList():
                if base.getName() == self.q.getData()['baselv']:
                    vg = base.getVolumeGroup()
                    break
            
            snapshot = Snapshot(vg, self.q.getData()['baselv'])
            snapshot.setDeviceByLun(self.q.getData()['lun'])
            
            snapshot.remove()
            
            return r
            
        return None