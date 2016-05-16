#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import base64
import string
import random

from folavirt.remote.RemoteObject import RemoteObject
from folavirt.networking.Query import Query
from folavirt.console.Colors import Colors
from folavirt.virt.Domain import Statuses

def getDomains():
    """
    Zwraca wszystkie domeny
    
    @param void
    @return []
    """
    from folavirt.remote.Agent import getAgents
    
    domains = []
    # Pobieranie listy agentów
    agents = getAgents()
    for agent in agents:
        # Dodawanie do listy domen
        domains += agent.getVmList()

    return domains

class Domain(RemoteObject):
    """
    Obiekt wirtualnej maszyny
    """
    def __init__(self, name = -1):
        if name != -1:
            self.name = name
    
    name = ""
    state = None
    host = None
    
    def getName(self):
        """
        Zwraca nazwę wirtualnej maszyny
        
        @param void
        @return nazwa
        """
        return self.name
    
    def getHost(self):
        return self.host
    
    def getAgent(self):
        """
        Zwraca agenta
        
        @return folavirt.remote.Agent
        """
        return self.host
    
    def searchHost(self):
        self.searchAgent()
    
    def searchAgent(self):
        """
        Szuka hosta na którym działa domena
        
        @param void
        @return Host
        """
        from folavirt.remote.Agent import getAgents
        
        agents = getAgents()
         
        for agent in agents:
            response = agent.ping()
            if not response:
                continue
            if response == "nolibvirt":
                continue
            
            domains = agent.getVmList()
            for domain in domains:
                if domain.getName() == self.name:
                    self.host = agent
                    self.address = self.host.address
                    self.port = self.host.port
                    agent.close()
                    return self.host
            agent.close()
        
        raise Exception("Nie można znaleźć agenta z maszyna wirtualna lub maszyna " + self.name + " nieistnieje.")
    
    def setAgentByName(self, name):
        """
        Ustawia nazwę agenta na podstawie nazwy
        """     
        from folavirt.remote.Agent import getAgents
           
        for agent in getAgents():            
            if agent.getHostName() == name:
                for domain in agent.getVmList():
                    if domain.getName() == self.name:                    
                        self.host = agent
                        self.address = self.host.address
                        self.port = self.host.port
                
                        return agent
                raise Exception(u"Nie ma takiej maszyny wirtualnej w agencie")
        
        raise Exception(u"Nie znaleziono agenta")
    
    def start(self):
        """
        Uruchamia domenę
        
        @param void
        @return void
        """
        q = Query()
        q.setCommand("start")
        q.setData(self.getName())
        
        return self.execute(q)
    
    def destroy(self):
        """
        Zatrzymuje domenę
        
        @param void
        @return void
        """
        q = Query()
        q.setCommand("destroy")
        q.setData(self.getName())
        
        return self.execute(q)
    
    def suspend(self):
        q = Query()
        q.setCommand("suspend")
        q.setData(self.getName())
        
        return self.execute(q)
    
    def resume(self):
        """
        Wznawianie działania maszyny
        
        @param void
        @return void
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("resume")
        q.setData(self.getName())
        
        # Zwracanie wyniku zapytania
        return self.execute(q)
    
    def reset(self):
        """
        Resetowanie maszyny
        
        @param void
        @return void
        """
        # Tworzneie zapytania
        q = Query()
        q.setCommand("reset")
        q.setData(self.getName())
        
        # Zwracanie wyniku zapytania
        return self.execute(q)
    
    def getState(self):
        """
        Pobieranie statusu
        
        @param void
        @return Status
        """
        if self.address == "":
            return Statuses.DOMAIN_DONTEXIST
        
        if self.state == None:
            # Tworzenie obiektu zapytania
            q = Query()
            q.setCommand('getstate')
            q.setData(self.getName())
            
            # Wysyłanie zapytania
            r = self.execute(q)
            
            # Ustawianie statusu w zmiennej obiektu
            self.state = r.getData()
            
        return self.state
    
    def getTemporaryGraphicPassword(self):
        """
        Zwraca tymczasowe hasło
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("gettemporarypasswd")
        q.setData(self.name)
        
        r = self.execute(q)
        
        passwd = r.getData()
        
        return passwd
    
    def getGraphicConsoleOptions(self):
        """
        Zwraca parametry konsoli graficznej
        
        @param void
        @return list
        """
        # Tworzenie obiektu zapytania
        q = Query()
        q.setCommand('graphicconsoleoptions')
        q.setData(self.getName())
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        # Zwracanie odpowiedzi
        return r
    
    def setGraphicConsoleListen(self, listen):
        """
        Ustawia adres nasłuchiwania konsoli VNC
        
        @param adres
        @return void
        """
        # Tworzenie obiektu zapytania
        q = Query()
        q.setCommand('setgraphicconsoleaddress')
        q.setData({'domain':self.getName(), 'address':listen})

        # Wykonywanie zapytania
        r = self.execute(q)
        
        # Zwracanie odpowiedzi
        return r
    
    def setGraphicConsolePasswd(self, passwd):
        """
        Ustawia hasło konsoli VNC
        
        @param hasło
        @return void
        """
        # Tworzenie obiektu zapytania
        q = Query()
        q.setCommand('setgraphicconsolepasswd')
        q.setData({'domain':self.getName(), 'passwd':passwd})
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        # Zwracanie odpowiedzi
        return r
    
    def setGraphicConsoleTemporaryPasswd(self, passwd):
        """
        Ustawia tymczasowego hasło konsoli VNC
        
        @param hasło
        @return void
        """
        # Tworzenie obiektu zapytania
        q = Query()
        q.setCommand('settemporarygraphicconsolepasswd')
        q.setData({'domain':self.getName(), 'passwd':passwd})
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        # Zwracanie odpowiedzi
        return r
    
    def setGraphicConsoleRandomPasswd(self):
        """
        Ustawia losowe hasło
        
        @param void
        @return Ustawione hasło
        """
        passwd = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
        # Ustawia hasło
        self.setGraphicConsoleTemporaryPasswd(passwd)
        
        return passwd
    
    def removeTemporaryPasswdFromDatabase(self):
        """
        Usuwa tymczasowe hasło z bazy danych
        """
        q = Query("removetemporarypasswd", self.name)
        return self.execute(q)
    
    def addOwnership(self, user):
        """
        Dodaje prawo do maszyny użytkownikowi
        
        @param Użytkownik
        @return void
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand("ownership-add")
        q.setData([user, self.getName()])
                
        # Wykonywanie zapytania
        r = self.execute(q)
        
        return r
    
    def clearOwnership(self):
        """
        Zabiera wszelkie uprawnienia do tej domeny
        
        @param void
        @return void
        """
        # Tworzenie zapytania
        q = Query()
        q.setCommand('ownership-cleandomain')
        q.setData(self.getName())
                
        r = self.execute(q)
        
        return r
    
    def undefine(self):
        """
        Usuwa definicję domeny
        
        @param void
        @return void
        """
        # Tworzenie obiektu zapytania
        q = Query()
        q.setCommand("undefinebyname")
        q.setData(self.getName())
        
        # Wykonywanie zapytania
        r = self.execute(q)
        
        # Zwracanie odpowiedzi
        return r
    
    def getXML(self):
        """
        Zwraca definicję maszyny wirtualnej
        """
        # Tworzenie zapytania
        q = Query("getxml", self.getName())
        
        r = self.execute(q)
        
        return base64.b64decode(r.getData())
    
    def getStateForConsole(self, ljust = 12):
        if self.getState() == Statuses.DOMAIN_NOSTATE:
            return "brak".ljust(ljust)
        
        if self.getState() == Statuses.DOMAIN_SHUTDOWN:
            return Colors.setred(u"wyłączanie".ljust(ljust))
        
        if self.getState() == Statuses.DOMAIN_SHUTOFF:
            return Colors.setred(u"wyłączona".ljust(ljust))
        
        if self.getState() == Statuses.DOMAIN_RUNNING:
            return Colors.setgreen(u"działa".ljust(ljust))
        
        if self.getState() == Statuses.DOMAIN_PAUSED:
            return Colors.setyellow(u"wstrzymana".ljust(ljust))
        
        if self.getState() == Statuses.DOMAIN_PMSUSPENDED:
            return Colors.setyellow(u"wstrzymana".ljust(ljust))
        
        return u"błąd"
    
    def __repr__(self):
        return repr((self.name))