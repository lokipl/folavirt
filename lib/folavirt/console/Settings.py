#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import signal
import codecs
from ConfigParser import ConfigParser

from folavirt.console.Params import Params
from folavirt.console.Colors import Colors

class Settings():
    def setAsScript(self):
        """
        Ustawia wykonywanie skryptu
        """
        # Poprawka kodowania
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        
        parser = ConfigParser()
        parser.read("../etc/folavirt.ini")
        
        # Sprawdza czy dodano parametr silent
        if Params().isParameter("quiet") or (parser.getint('console','quiet') == 1):
            if not Params().isParameter('noquiet'):
                self.setSilent()

        if Params().isParameter("nocolor") or (parser.getint('console', 'color') == 0):
            if not Params().isParameter("color"):
                Colors().disable()
    
    def setPidFile(self, path):
        """
        Ustawia plik gdzie będzie zapisywany pid procesu
        """
        f = open(path, 'w+')
        f.write(str(os.getpid()))
        f.close()
        
    def setLogFile(self, logfile):
        """
        Ustawia plik przychytywania stdout
        """
        f = codecs.open(logfile, 'a', 'utf8', 'replace')
        sys.stdout = f
        
    def setAsDeamon(self, logfile = False):
        """
        Ustawia środowisko po daemona
        Wycisza stdout
        """
        # Wyciszanie stdout
        if logfile:
            self.setLogFile(logfile)
        Colors().disable()
        self.daemonize()
            
    def daemonize(self):
        """
        Daemonizuje proces
        
        @see http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
        """
        workdir = os.getcwd()
        umask = 0
        
        # Forkowanie pierwszego procesu
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
            
        os.chdir(workdir)
        os.umask(umask)
        os.setsid()
        
        # Forkowanie drugiego procesu
        pid2 = os.fork()
        if pid2 > 0:
            sys.exit(0)
            
        os.chdir(workdir)
        os.umask(umask)
        
        os.dup2(0, 1)
        os.dup2(0, 2)
                
        sys.stdout.flush()
        sys.stderr.flush()
        
    def _start(self, pid):
        try:
            if pid == None:
                raise Exception('fresh start')
            os.kill(int(pid), 0)
            print(Colors.setred(" * ") + Params().getScriptName() + u" jest uruchomiony")
            sys.exit(1)
        except OSError:
            print(Colors.setgreen(" * ") + Params().getScriptName() + u" uruchomiony")
            return 1
        except Exception:
            print(Colors.setgreen(" * ") + Params().getScriptName() + u" uruchomiony")
            return 1
    
    def _stop(self, pid, restart = False):
        if pid == None:
            print(Colors.setred(" * ") + Params().getScriptName() + u" jest zatrzymany")
            if not restart:
                sys.exit(1)
        try:
            os.kill(int(pid), signal.SIGKILL)
            print(Colors.setgreen(" * ") + Params().getScriptName() + u" zatrzymany")
            if not restart:
                sys.exit(0)
        except OSError:
            print(Colors.setred(" * ") + Params().getScriptName() + u" jest zatrzymany")
            if not restart:
                sys.exit(2)
        except TypeError:
            if not restart:
                sys.exit(2)
    
    def deamonManage(self, pidfile):
        """
        Obsługuje polecenia zarządzające daemonem. Dodaje obsługę poleceń, start, stop, status
        
        @param Nazwa pliku z numerem procesu
        """
        if Params().isParameter("quiet"):
            self.setSilent()
        
        if Params().isParameter("nocolor"):
            Colors().disable()
        
        # Szukanie pid
        try:
            f = open(pidfile)
            pid = f.readline()
        except IOError:
            pid = None
        
        # Uruchomienie daemona
        if Params().getArg(0) == "start":
            out = self._start(pid)
            if out == 1:
                return
        
        # Zatrzymanie procesu
        if Params().getArg(0) == "stop":
            self._stop(pid)
        
        if Params().getArg(0) == "restart":
            self._stop(pid, True)
            time.sleep(1)
            out = self._start(pid)
            if out == 1:
                return
        
        # Status
        if Params().getArg(0) == "status":
            try:
                if pid != None:
                    os.kill(int(pid), 0)
                else:
                    raise Exception("zatrzymany")
                print(Colors().setgreen(" * ") + Params().getScriptName() + u" jest uruchomiony")
            except:
                print(Colors().setred(" * ") + Params().getScriptName() + u" jest zatrzymany")   
            sys.exit(0)
        
        print(Params().getScriptName() + " start|stop|restart|status")
        sys.exit(0)       
            
    def setSilent(self):
        """
        Ustawia stdout na /dev/null
        """
        devnull = codecs.open('/dev/null', 'w', 'utf8', 'replace')
        sys.stdout = devnull
        
    def getUsageHelp(self, ljust = 27):
        print(u"UŻYCIE")
        print(" " + Params().getScriptName() + u" [opcje] [komenda]")
        
    def getDefaultOptionsHelp(self, ljust = 27):
        """
        Wypisuje pomoc dot. ogólnych parametrów 
        """
        #print(u"UŻYCIE:")
        #print("  " + Params().getScriptName() + u" [opcje] [komenda]")
        print(u"\nOPCJE:")
        print("  " + Colors().setbold("--[no]quiet".ljust(ljust)) + "Ukrywa wszystko z ekranu")
        print("  " + Colors().setbold("--[no]color".ljust(ljust)) + "Usuwa kolory")