#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.disks.iscsi.Snapshots import Snapshots

class Base():
    def __init__(self, vg = None, name = None):
        self.vg = vg
        self.name = name
    
    def getVolumeGroup(self):
        """
        Zwraca nazwę grupy woluminowej do której należy baza
        
        @param void
        @return Grupa woluminowa
        """
        return self.vg
    
    def setVolumeGroup(self, vg):
        """
        Ustawia grupę woluminową
        
        @param Grupa woluminowa
        @return void
        """
        self.vg = vg
        
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
    
    def getDevice(self):
        """
        Zwraca urządzenie blokowe dysku bazowego
        
        @param void
        @return Urządzenie blokowe
        """
        return "/dev/" + self.getVolumeGroup() + "/" + self.getName()
    
    def getSnapshots(self):
        """
        Zwracanie snapshotów
        
        @param void
        @return void
        """
        snapshots = Snapshots().getList()
        result = []
        for snapshot in snapshots:
            if snapshot.getBase().getName() == self.getName() and snapshot.getBase().getVolumeGroup() == self.getVolumeGroup():
                result.append(snapshot)
                
        return result
    
    def getLastSnapshotNumber(self):
        return len(self.getSnapshots())
