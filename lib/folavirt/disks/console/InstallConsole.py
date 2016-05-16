#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import commands

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.disks.Configure import Configure

class InstallConsole():
    def __init__(self):
        if Params().getArg(0) == "vg":
            if Params().getArg(1) == "attach":
                # Dodawanie nowej grupy wolumenowej
                self.installAttachVg()
                sys.exit(0)
                        
            if Params().getArg(1) == "detach":
                # Usuwanie grupy wolumenowej z systemu
                self.installDettachVg()
                sys.exit(0)
                        
            if Params().getArg(1) == "list":
                # Lista wszystkich woluminów logicznych
                self.installListVg()
                sys.exit(0)
                        
            if Params().getArg(1) == "details":
                # Szczegóły VG
                self.installDetails()
                sys.exit(0)
            
            self.printhelp()
            sys.exit(0)
                
    @staticmethod
    def printhelp(ljust1 = 37, ljust2 = 15):
        """
        Pomoc dotycząca poleceń instalujących system
        
        @param void
        @return void
        """
        print("\n " + "Instalacja grup woluminowych")
        print("  " + Colors.setbold("vg attach $VG [--force]".ljust(ljust1)) + u"dodaje grupę woluminową do folavirt [z pominięciem sprawdzenia czy istnieje]")
        print("  " + Colors.setbold("vg detach $VG".ljust(ljust1)) + u"usuwa grupę woluminową z folavirt")
        print("  " + Colors.setbold("vg details $VG".ljust(ljust1)) + u"szczegóły grupy woluminowej")
        print("  " + Colors.setbold("vg list".ljust(ljust1)) + u"wyświetla listę grup woluminowych zarządzanych przez foladisk")
    
    def installAttachVg(self):
        """
        Dodaje do zarządzania grupę woluminową
        """
        # Pobiera listę skonfigurowanych wolimnów ligicznych
        vglist = Configure().getVolumeGroupList()
        if Params().getArg(2) in vglist:
            print(Colors.setred(" * ") + u"Taka grupa woluminowa już istnieje.")
            sys.exit(1)
            
        if Params().getArg(2) == "":
            print(Colors.setred(" * ") + u"Nie podano nazwy grupy woluminowej")
            sys.exit(1)
        
        if not Params().isParameter("force"):
            (status, output) = commands.getstatusoutput("vgdisplay " + Params().getArg(2))
            if status != 0:
                print(Colors.setred(" * ") + u"Nie ma takiej grupy woluminowej w systemie")
                sys.exit(1)
            
        # Dodawanie grupy woluminów logicznych
        Configure().addVolumeGroup(Params().getArg(2))
        print(Colors.setgreen(" * ") + u"grupa woluminowa " + Params().getArg(2) + u" przyłączona")
        sys.exit(0)
        
    def installDettachVg(self):
        """
        Usuwa wolumin logiczny z zarządzania
        
        @param void
        @return void
        """
        if (Params().argLen() == 3):
            # Sprawdza czy taka grupa istenieje
            vglist = Configure().getVolumeGroupList()
            if not Params().getArg(2) in vglist:
                print(Colors.setred(" * ") + u"Nie ma takiej grupy woluminowej")
                sys.exit(1)
            
            # Usuwanie grupy wolimnów
            Configure().deleteVolumeGroup(Params().getArg(2))
            print(Colors.setgreen(" * ") + u"Usunięto z zarządzania grupę woluminową " + Params().getArg(2))
            sys.exit(0)
        else:
            sys.exit(-1)
        
    def installListVg(self):
        """
        Wypisuje listę woluminów logicznych
        
        @param void
        @return void
        """
        if Params().argLen() == 2:
            # Pobiera listę skonfigurowanych wolimnów ligicznych
            vglist = Configure().getVolumeGroupList()
            
            i = 1
            for vg in vglist:
                print(Colors.setbold(str(i)) + " " + vg)
                i += 1
    
    def installDetails(self):
        """
        Wyświetlanie szczegółów woluminu logicznego
        
        @param void
        @return void
        """
        if Params().argLen() == 3:
            # Wykonywanie polecenia powłoki
            (status, output) = commands.getstatusoutput("vgdisplay " + Params().getArg(2))
            if (status != 0):
                print(Colors.setred(" * ") + u"Błąd!")
            else:
                print output