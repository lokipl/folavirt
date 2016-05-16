#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.disks.iscsi.Configuration import Configuration
from folavirt.disks.iscsi.Tgt import Tgt

class IscsiConsole():
    def __init__(self):
        if Params().getArg(0) == "iscsi":
            if Params().getArg(1) == "options":
                if Params().getArg(2) == "iqnbasename":
                    # Ustawienia iqn
                    self.iscsiOptionIqnbasename()
                    sys.exit(0)
                if Params().getArg(2) == "iqndate":
                    # Ustawienia daty w iqn
                    self.iscsiOptionIqndate()
                    sys.exit(0)
                if Params().getArg(2) == "iqnhostname":
                    # Ustawienia nazwy hosta w iqn
                    self.iscsiOptionIqnhostname()
                    sys.exit(0)
            if Params().getArg(1) == "dump":
                # Wyrzuca na konsole konfigurację TGT
                self.iscsiDump()
                sys.exit(0)
            if Params().getArg(1) == "write":
                # Zapisuje konfigurację
                self.iscsiWrite()
                sys.exit(0)
            if Params().getArg(1) == "reload":
                # Przełądowanie deamona
                self.reload()
                sys.exit(0)
        
            # Wyświetlanie helpa
            self.printhelp()
            sys.exit(0)

    @staticmethod
    def printhelp(ljust1 = 27, ljust2 = 15):
        """
        Wyświetla pomoc
        """
        print("\n " + u"Zarządzanie konfiguracją iSCSI")
        print("  " + Colors.setbold("iscsi dump".ljust(ljust1)) + u"generuje konfiguracjaę iscsi i wypisuje na standardowym wyjściu")
        print("  " + Colors.setbold("iscsi options iqnbasename".ljust(ljust1)) + u"nazwa zasobu maszyn bazowych")
        print("  " + Colors.setbold("iscsi options iqndate".ljust(ljust1)) + u"data widoczna w IQN")
        print("  " + Colors.setbold("iscsi options iqnhostname".ljust(ljust1)) + u"nazwa hosta w IQN") 
        print("  " + Colors.setbold("iscsi reload".ljust(ljust1)) + u"przeładowywuje daemona iscsi")
        print("  " + Colors.setbold("iscsi write".ljust(ljust1)) + u"zapisuje konfiguracjaę iscsi do pliku konfiguracyjnego")  
        
    def iscsiDump(self):
        """
        Wyrzuca na standardowe wyjście konfigurację tgt
        
        @param void
        @return void
        """
        print Tgt().getFreshConfig()
        
    def iscsiWrite(self):
        """
        Zapisuje konfigurację tgt
        
        @param void
        @return void
        """
        Tgt().writeConfig()
    
    def iscsiOptionIqnbasename(self):
        """
        Ustawia podstawowy ciąg iqn
        
        @param void
        @return void
        """
        if Params().argLen() == 3:
            print Configuration().getIqnbasename()
        if Params().argLen() == 4:
            Configuration().setIqnbasename(Params().getArg(3))
            
    def iscsiOptionIqndate(self):
        """
        Ustawia datę w iqn
        
        @param void
        @return void
        """
        if Params().argLen() == 3:
            print Configuration().getIqndate()
        if Params().argLen() == 4:
            Configuration().setIqndate(Params().getArg(3))

    def iscsiOptionIqnhostname(self):
        """
        Ustawia nazwę hosta w iqn
        
        @param void
        @return void
        """
        if Params().argLen() == 3:
            print Configuration().getIqnhostname()
        if Params().argLen() == 4:
            Configuration().setIqnhostname(Params().getArg(3))
    
    def reload(self):
        """
        Przeładowywuje konfigurację
        """
        Tgt().reload()