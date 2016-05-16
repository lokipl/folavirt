#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
from ConfigParser import ConfigParser

from folavirt.console.Params import Params
from folavirt.console.Colors import Colors
from folavirt.remote.DiskManager import getDms,DiskManager
from folavirt.disks.ServerDiscover import ServerDiscover
from folavirt.permissions.Network import Network

class DiskConsole():
    def __init__(self):
        if Params().getArg(0) == "disk":
            if Params().getArg(1) == "discover":
                # Skanowanie w poszukiwaniu zarządców dyskami
                self.discover()
                sys.exit(0)
            if Params().getArg(1) == "list":
                # Wyświetla listę zarządców dysków
                self.dmlist()
                sys.exit(0)
                
            if Params().getArg(1) == "lv":
                # Lista maszyn bazowych
                if Params().getArg(2) == "list":
                    self.baselvlist()
                    sys.exit(0)
                    
            self.printhelp()
            sys.exit(0)
                
    @staticmethod
    def printhelp(ljust1 = 37, ljust2 = 15):
        """
        Wyświetla pomoc
        
        @param void
        @return void
        """
        print("\n " + u"Obsługa zarządców dyskami")
        print("  " + Colors.setbold("disk discover [--dry-run]".ljust(ljust1)) + u"poszukiwanie maszyn z uruchomioną usługą foladiskd [bez aktualizuji etc/disks]")
        print("  " + Colors.setbold("disk list".ljust(ljust1)) + u"wyświetla listę zarządców dyskami")
        print("  " + Colors.setbold("disk lv list".ljust(ljust1)) + u"lista woluminów bazowych")
    
    def dmlist(self):
        """
        Wyświetla listę dm
        """
        if not os.path.exists('../etc/disks'):
            print(Colors.setred(" * ") + u"Brak konfiguracji zarządców dysków. Wykonaj najpierw " + Colors.setbold(u"disk discover"))
            sys.exit(0)
        
        dms = getDms()
        
        if len(dms) == 0:
            print(Colors.setred(" * ") + u"Brak konfiguracji zarządców dysków. Wykonaj najpierw " + Colors.setbold(u"disk discover"))
            sys.exit(0)
            
        print(Colors.setbold("Nazwa".ljust(25) + "Adres".ljust(20) + "Port".ljust(10) + "Status"))
        
        for dm in dms:
            if dm.ping():
                status = Colors.setgreen(u"działa")
            else:
                status = Colors.setred(u"nie działa")
            
            print(dm.getName().ljust(25) + dm.getAddress().ljust(20) + str(dm.getPort()).ljust(10) + status)
      
    def discover(self):
        """
        Szuka po Avahi foladisk
        """
        #print(Colors.setyellow(" * ") + u"Skanowanie w poszukiwaniu zarządców dyskami")
        # Rozpoczęcie skanowania
        sd = ServerDiscover()
        
        parser = ConfigParser()
        parser.read('../etc/folavirt.ini')
        
        try:
            seconds = parser.getint("console", "avahi_timeout")
        except:
            seconds = 3        
        
        time.sleep(seconds)
        
        # Parsowanie wyniku
        disks = {}
        for definition in sd.getDisks():
            disks.update({definition['host']: definition})
        
        # Plik z konfiguracją
        if not Params().isParameter("dry-run"):
            f = open("../etc/disks", "w+")
            f.write("# Wygenerowano " + str(datetime.datetime.now()) + "\n")
        
        print(Colors.setbold("Nazwa".ljust(25) + "Adres".ljust(20) + "Port".ljust(11) + "Status"))
        for disk in disks:
            # Sprawdzanie czy jest to host należący do sieci
            if Network().contains(disks[disk]['address']):
                # Zapis konfiguracji
                if not Params().isParameter("dry-run"):
                    f.write(disks[disk]['host'] + "\t"+disks[disk]['address'] + "\t"+str(disks[disk]['port']) + "\n")
                
                # Tworzenie obiektu zarządcy dysków
                dm = DiskManager()
                dm.address = disks[disk]['address']
                dm.port = disks[disk]['port']
                dm.name = disks[disk]['host']
                
                # Ping
                if dm.ping():
                    status = Colors.setgreen(u"działa")
                else:
                    status = Colors.setred(u"nie działa")
                
                print(dm.getName().ljust(25) + dm.getAddress().ljust(20) + str(dm.getPort()).ljust(11) + status)
            
        sd.kill()
        
    def baselvlist(self):
        """
        Lista maszyn bazowych
        """
        # Pobieranie listy zarządców dysków
        dms = getDms()
        
        basevolumes = []
        
        for dm in dms:
            if dm.ping():
                for name in dm.getBaseVolumes():
                    basevolumes.append({"address":dm.getName(), "name": name})
            else:
                print(Colors.setred(" * ") + dm.getName() + u" nie odpowiada")

        # Tabelka, gdy znaleziono wiecej niż 1 wolumin
        if len(basevolumes) >= 1:
            print(Colors.setbold("Adres".ljust(15) + "Nazwa"))
            for volume in basevolumes:
                print(volume["address"].ljust(15) + volume["name"])
