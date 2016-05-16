#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.remote.Agent import getAgents
from folavirt.remote.Domain import Domain
from folavirt.virt.Domain import Statuses

class BasicConsole():
    """
    Podstawowe polecenia operujące na maszynach wirtualncych
    """
    def __init__(self):
        if Params().getArg(0) == "list":
            self.list()
            sys.exit(0)
        
        if Params().getArg(0) == "start":
            self.start()
            sys.exit(0)
        
        if Params().getArg(0) == "destroy":
            self.destroy()
            sys.exit(0)
        
        if Params().getArg(0) == "suspend":
            self.suspend()
            sys.exit(0)
        
        if Params().getArg(0) == "resume":
            self.resume()
            sys.exit(0)
        
        if Params().getArg(0) == "reset":
            self.reset()
            sys.exit(0)
        
        if Params().getArg(0) == "console":
            self.console()
            sys.exit(0)
        
        if Params().getArg(0) == "details":
            self.details()
            sys.exit(0)
            
        if Params().getArg(0) == "virsh":
            self.virsh()
            sys.exit(0)
        
    def list(self):
        """
        Wyświetla listę wszystkich maszyn wirtualncych
        """
        agents = getAgents()
        
        # Lista maszyn
        domains = []
        
        for agent in agents:
            if Params().getArg(1) != "":
                if agent.getHostName() != Params().getArg(1):
                    continue
                    
            if agent.ping():
                domains += agent.getVmList()
                agent.close()
            else:
                print(Colors.setred(" * ") + agent.getHostName() + u" nie odpowiada")
        
        if len(domains)> 0:
            print(Colors.setbold(u"Nazwa".ljust(30) + u"Agent".ljust(20) + u"Stan"))
        
            # Sortowanie po nazwach
            domains = sorted(domains, key=lambda domain:domain.name.lower())
               
            # Wypisywanie maszyn
            for domain in domains:
                if Params().isParameter("on"):
                    if domain.getState() != Statuses.DOMAIN_RUNNING:
                        continue
                if Params().isParameter("off"):
                    if domain.getState() != Statuses.DOMAIN_SHUTOFF:
                        continue
                    
                print(domain.getName().ljust(30) + domain.getHost().getHostName().ljust(20) + domain.getStateForConsole(15))

    
    @staticmethod
    def printhelp(ljust = 37, ljust2 = 15):
        """
        Pomoc
        
        @static
        @param void
        @return void
        """
        print(" " + u"Podstawowe operacje na maszynach wirtualnych")
        print("  " + Colors.setbold("create base $VM $T $B [$D] [--xml]".ljust(ljust)) + u"tworzy maszynę wirtualną z woluminu bazowego [tylko generuje XML]")
        print("  " + Colors.setbold("create snapshot $T $B $S [$D]".ljust(ljust)) + u"tworzy maszynę wirtualną będącą snapshotem z woluminu bazowego")
        print("  " + Colors.setbold("destroy $VM[@$A]".ljust(ljust)) + u"niszczy maszynę wirtualną")
        print("  " + Colors.setbold("details $VM[@$A]".ljust(ljust)) + u"wypisuje wszystko na temat maszyny wirtualnej")
        print("  " + Colors.setbold("dumpxml $VM[@$A]".ljust(ljust)) + u"wypisuje na standardowe wyjście definicję maszyny")
        print("  " + Colors.setbold("list [--on|-off] [$A]".ljust(ljust)) + u"tworzy listę zdefiniowanych maszyn wirtualnych")
        print("  " + "".ljust(ljust) + u"[aktywne (running)|nieaktywne (shut off)] [tylko z jednego agenta]")
        print("  " + Colors.setbold("migratexml $VM $A [--force]".ljust(ljust)) + u"przenosi definicję maszyny do innego agenta [bez pytania potwierdzenie przy niszczeniu maszyny]")
        print("  " + Colors.setbold("reset $VM[@$A]".ljust(ljust)) + u"resetuje maszynę wirtualną")
        print("  " + Colors.setbold("resume $VM[@$A]".ljust(ljust)) + u"wznawia maszynę wirtualną")
        print("  " + Colors.setbold("start $VM[@$A]".ljust(ljust)) + u"uruchamia maszynę wirtualną")
        print("  " + Colors.setbold("suspend $VM[@$A]".ljust(ljust)) + u"wstrzymuje maszynę wirtualną")
        print("  " + Colors.setbold("undefine $VM[@$A] [--force]".ljust(ljust)) + u"usuwa maszynę wirtualną [bez pytania o potwierdzenie]")
        print("  " + Colors.setbold("undefine-snapshot $VM [--force]".ljust(ljust)) + u"usuwa maszynę wirtualną typu snapshot [bez pytania o potwierdzenie]")
        print("  " + Colors.setbold("virsh $A $V".ljust(ljust)) + u"wykonuje polecenie virsh na agencie")
        
    @staticmethod
    def printhelpconsole(ljust = 37, ljust2 = 15):
        print("\n " + u"Ustawienia konsoli maszyny wirtualnej")
        print("  " + Colors.setbold("console $VM set passwd $P".ljust(ljust)) + u"ustawianie stałego hasła dostępu do konsoli graficznej")
        print("  " + Colors.setbold("console $VM set tmppasswd [--del] $P ".ljust(ljust)) + u"ustawianie tymczasowego hasła dostępu do konsoli graficznej [usuwa hasło i kończy]")
        print("  " + Colors.setbold("console $VM set randompasswd".ljust(ljust)) + u"ustawianie tymczasowego hasło do konsoli graficznej losowo")
        print("  " + Colors.setbold("console $VM set listen [local|any]".ljust(ljust)) + u"ustawianie adresu nasłuchiwania dla konsoli graficznej")

    @staticmethod
    def _getDomain():
        """
        Zwraca domenę
        
        @param void
        @return folavirt.remove.Domain
        """
        if Params().argLen() < 2:
            print(Colors.setred(" * ") + u"Musisz podać nazwę maszyny wirtualnej")
            sys.exit(1)           
            
        domain = Domain()
        
        splitted = Params().getArg(1).split("@")
        if len(splitted) > 1:
            agent = splitted[1]
            domain.name = splitted[0]
            try:
                domain.setAgentByName(agent)
            except Exception as e:
                print(Colors.setred(" * ") + u"Błąd! "),
                print(str(e).decode('utf-8'))
                sys.exit(1)
        else:   
            domain.name = Params().getArg(1)

            try:
                domain.searchAgent()
            except Exception as e:
                print(Colors.setred(" * ") + u"Błąd! " + str(e).decode('utf-8'))
                sys.exit(1)
        
        return domain
            
    def start(self):
        """
        Uruchamia domenę
        
        @param void
        @return void
        """
        domain = self._getDomain()
            
        # Uruchomienie domeny
        r = domain.start()
        if r.getErrorCode() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas uruchamiania maszyny wirtualnej " + domain.getName())
            if r.getData() == -1:
                print(Colors.setred(" * ") + u"Maszyna wirtualna jest już uruchomiona")
                sys.exit(0)
            print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
        else:
            print(Colors.setgreen(" * ") + u"Uruchomiono maszynę wirtualną " + domain.getName() + " na " + domain.getHost().getHostName())
    
    def destroy(self):
        """
        Zatrzymuje domenę
        
        @param void
        @return void
        """
        # Pobiera domenę
        domain = self._getDomain()
        
        # Zatrzymuje domenę
        r = domain.destroy()
        
        if r.getErrorCode() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas wyłączania maszyny wirtualnej " + domain.getName())
            print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
        else:
            print(Colors.setgreen(" * ") + u"Wyłączono maszynę wirtualną " + domain.getName() + " na " + domain.getHost().getHostName())
    
    def suspend(self):
        """
        Wstrzymywanie domeny
        
        @param void
        @return void
        """
        # Pobiera domenę
        domain = self._getDomain()
        
        # Wstrzymywanie domeny
        r = domain.suspend()
        
        if r.getErrorCode() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas wstrzymywania maszynę wirtualną " + domain.getName())
            print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
        else:
            print(Colors.setgreen(" * ") + u"Wstrzymano maszynę wirtualną " + domain.getName() + " na " + domain.getHost().getHostName())
    
            
    def resume(self):
        """
        Wznawia działanie domeny
        
        @param void
        @return void
        """
        # Pobiera domenę
        domain = self._getDomain()
        
        # Wznawianie domeny
        r = domain.resume()
        
        if r.getErrorCode() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas wznawiania maszyny wirtualnej " + domain.getName())
            print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
        else:
            print(Colors.setgreen(" * ") + u"Wznowiono maszynę wirtualną " + domain.getName() + " na " + domain.getHost().getHostName())
            
    def reset(self):
        """
        Resetowanie domeny
        
        @param void
        @return void
        """
        # Pobiera domenę
        domain = self._getDomain()
        
        # Resetuje domenę
        r = domain.reset()
        
        if r.getErrorCode() != 0:
            print(Colors.setred(" * ") + u"Błąd podczas resetowania maszyny wirtualnej " + domain.getName())
            print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
        else:
            print(Colors.setgreen(" * ") + u"Zresetowano maszynę wirtualną " + domain.getName() + " na " + domain.getHost().getHostName())
    
    def details(self):
        """
        Wyświetla informacje nt. maszyny wirtualnej
        
        @param void
        @return void
        """
        # Pobiera domenę
        domain = self._getDomain()
        
        print(Colors.setbold("Nazwa".ljust(20)) + domain.getName())
        print(Colors.setbold("Agent".ljust(20)) + domain.getAgent().getHostName())
        print(Colors.setbold("Stan".ljust(20)) + domain.getStateForConsole())
        
        graphicoptions = domain.getGraphicConsoleOptions().getData()
        print(Colors.setbold("Typ konsoli".ljust(20)) + graphicoptions['type'])
        print(Colors.setbold("Adres".ljust(20)) + domain.getAgent().getAddress())
        print(Colors.setbold("Port".ljust(20)) + graphicoptions['port'])
        print(Colors.setbold(u"Nasłuchuje na".ljust(20)) + graphicoptions['listen'])
        passwd = domain.getTemporaryGraphicPassword()
        if passwd == False:
            passwd = Colors.setred("brak")
        print(Colors.setbold(u"Tymczasowe hasło".ljust(19)) + " " +passwd)
    
    def console(self):
        """
        Wypisuje dane dot. konsoli graficznej domeny
        
        @param void
        @return void
        """
        if Params().argLen() == 1:
            self.printhelpconsole()
            sys.exit(0)
        
        domain = self._getDomain()
        
        # Tylko wyświetlenie parametrów
        if Params().argLen() == 2:            
            # Pobiera dane
            r = domain.getGraphicConsoleOptions()
            
            if r.getErrorCode() != 0:
                print(Colors.setred(" * ") + u"Błąd podczas pobierania parametrów domeny " + domain.getName())
                print(Colors.setred(" * ") + u"Błąd: " + str(r.getData()))
            else:
                print(Colors.setbold(u"Typ konsoli".ljust(20)) + r.getData()['type'])
                print(Colors.setbold(u"Adres".ljust(20)) + domain.getHost().getAddress())
                print(Colors.setbold(u"Port".ljust(20)) + r.getData()['port'])
                print(Colors.setbold(u"Nasłuchuje na".ljust(20)) + str(r.getData()['listen']))
                passwd = domain.getTemporaryGraphicPassword()
                if passwd == False:
                    passwd = Colors.setred("brak")
                print(Colors.setbold(u"Tymczasowe hasło".ljust(19)) + " " +passwd)
                
        # Zmiana ustawień
        if Params().getArg(2) == "set":
            if domain.getState() != Statuses.DOMAIN_SHUTOFF:
                print(Colors.setred(" * ") + u"Nie można zmieniać ustawień na niewyłączonej maszynie wirtualnej!")
                sys.exit(1)
            
            # Zmiana adresu nasłuchiwania
            if Params().getArg(3) == "listen":
                # Pobranie adresu z parametru
                address = Params().getArg(4)
                
                if address == "":
                    address = "0.0.0.0"
                if address == "any":
                    address = "0.0.0.0"
                if address == "local":    
                    address = "127.0.0.1"
                
                # Ustawienie adresu nasłuchiwania
                r = domain.setGraphicConsoleListen(address)
                
                print(Colors.setgreen(" * ") + u"Ustawiono adres nasłuchiwania na " + address)
                sys.exit(0)
                
            # Zmiana hasła
            if Params().getArg(3) == "passwd":
                # Pobranie hasła z parametru
                passwd = Params().getArg(4)
                
                # Ustawianie hasła
                r = domain.setGraphicConsolePasswd(passwd)
                
                # Usuwanie tymczasowego hasła
                domain.removeTemporaryPasswdFromDatabase()
                
                print(Colors.setgreen(" * ") + u"Ustawiono hasło do VNC")
                sys.exit(0)
                
            # Zmiana hasła na tymczasowe
            if Params().getArg(3) == "tmppasswd":
                # Czy usuwać tymczasowe hasło
                if Params().isParameter("del"):
                    domain.removeTemporaryPasswdFromDatabase()
                    sys.exit(0)
                
                # Pobranie hasła z parametru
                passwd = Params().getArg(4)
                
                # Ustawianie hasła
                r = domain.setGraphicConsoleTemporaryPasswd(passwd)
                
                print(Colors.setgreen(" * ") + u"Ustawiono tymczasowe hasło VNC")
                sys.exit(0)
                
            # Ustawia losowe tymczasowe hasło
            if Params().getArg(3) == "randompasswd":
                passwd = domain.setGraphicConsoleRandomPasswd()
                
                print(Colors.setgreen(" * ") + u"Ustawiono tymczasowe hasło VNC na " + Colors.setbold(passwd))
                sys.exit(0)
            
            self.printhelpconsole()
    
    def virsh(self):
        if Params().getArg(1) == "":
            print(Colors.setred(" * ") + u"Nie podano agenta")
            sys.exit(1)
            
        if Params().getArg(2) == "":
            print(Colors.setred(" * ") + u"Nie podano polecenia do wykonania")
            sys.exit(0)
        
        for agent in getAgents():
            if agent.getHostName() == Params().getArg(1):
                print(agent.virsh(Params().getAllArgsFrom(2)))
                
                sys.exit(0)
                
        print(Colors.setred(" * ") + u"Nie ma takiego agenta")
        sys.exit(1)