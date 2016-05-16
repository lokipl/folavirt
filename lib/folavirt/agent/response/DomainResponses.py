#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import base64

from folavirt.networking.Response import Response
from folavirt.virt.Domain import Domain
from folavirt.permissions.GraphicPasswords import GraphicPasswords

class DomainResponses():
    def __init__(self, q):
        self.q = q
        self.uri = 'qemu:///system'
        
    def getResponse(self):
        # Uruchomienie domeny
        if self.q.getCommand() == "start":
            # Odpowiedź
            r = Response()
            r.setCommand("start")
            
            print "start"
            try:
                # Obiekt domeny
                domain = Domain(self.uri, self.q.getData())
                # Uruchomienie domeny
                out = domain.create()
                
                # Powiodło się
                r.setData(out)
                if out != 0:
                    r.setErrorCode(1)
                    
                return r
            except:
                # Nie powiodło się
                r.setData("fail")
                return r

            return r
        
        # Wyłączenie domeny
        if self.q.getCommand() == "destroy":
            # Odpowiedź
            r = Response()
            r.setCommand("destroy")
            
            # Obiekt domeny
            domain = Domain(self.uri, self.q.getData())
            # Zatrzymywanie domeny
            out = domain.destroy()
            
            if out == 0:
                # Poprawnie zatrzymano domenę
                r.setData('OK')
                return r
                
            if out == -1:
                r.setData('Domain is down')
                r.setErrorCode(1)
                return r
            
            r.setData('fail')
            r.setErrorCode(out)
            return r
        
        # Resetowanie domeny
        if self.q.getCommand() == "reset":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("reset")
            
            domain = Domain(self.uri, self.q.getData())
            out = domain.reset()
            if out == 0:
                r.setData("ok")
                return r
            
            r.setData('fail')
            r.setErrorCode(out)
            return r
        
        # Wstrzymywanie domeny
        if self.q.getCommand() == "suspend":
            r = Response()
            r.setCommand("suspend")
            
            domain = Domain(self.uri, self.q.getData())
            out = domain.suspend()        
            if out == 0:
                r.setData('OK')
                return r
            
            r.setData('fail')
            return r
        
        # Zapytanie o status domeny
        if self.q.getCommand() == 'getstate':
            # Tworzenie obiektu odpowiedzi
            r = Response()
            r.setCommand('getstate')
             
            # Tworzenie obiektu rzeczywistej domeny
            domain = Domain(self.uri, self.q.getData())
             
            # Pobieranie statusu i ustawianie go jako parametr odpowiedzi
            r.setData(domain.getState())
             
            return r
        
        # Wznawianie działania maszyny wirtualnej
        if self.q.getCommand() == "resume":
            # Tworzenie obiektu odpowiedzi
            r = Response()
            r.setCommand("resume")
            
            # Domena
            domain = Domain(self.uri, self.q.getData())
            out = domain.resume()
            if out == 0:
                r.setData('OK')
                return r
            
            r.setData('fail')
            return r
        
        # Opcje konsoli graficznej
        if self.q.getCommand() == "graphicconsoleoptions":
            # Tworzenie obiektu odpowiedzi
            r = Response()
            r.setCommand("graphicconsoleoptions")
            
            # Domena
            domain = Domain(self.uri, self.q.getData())
            r.setData(domain.getGraphicConsoleOptions())
        
            return r
        
        # Zwraca definicję XML maszyny
        if self.q.getCommand() == "getxml":
            # Tworzenie odpowiedzi
            r = Response("getxml")
            
            # Domena
            domain = Domain(self.uri, self.q.getData())
            r.setData(base64.b64encode(domain.dumpXML()))
            
            return r
        
        # Ustawia adres na jakim ma słuchać konsola graficzna
        if self.q.getCommand() == "setgraphicconsoleaddress":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('setgraphicconsoleaddress')
            
            # Domena
            domain = Domain(self.uri, self.q.getData()['domain'])
            domain.setGraphicConsoleListen(self.q.getData()['address'])
            
            return r
        
        # Ustawia hasło do konsoli VNC
        if self.q.getCommand() == "setgraphicconsolepasswd":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('setgraphicconsolepasswd')
            
            # Domena
            domain = Domain(self.uri, self.q.getData()['domain'])
            domain.setGraphicConsolePasswd(self.q.getData()['passwd'])
        
            return r
        
        # Ustawia tymczasowe hasło do konsoli VNC
        if self.q.getCommand() == "settemporarygraphicconsolepasswd":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('settemporarygraphicconsolepasswd')
            
            # Najpierw ustawianie hasła
            domain = Domain(self.uri, self.q.getData()['domain'])
            domain.setGraphicConsolePasswd(self.q.getData()['passwd'])
            
            # Zapis hasła w bazie danych
            GraphicPasswords().setPassword(self.q.getData()['domain'], self.q.getData()['passwd'])
            
            return r
        
        # Zapytanie o hasło
        if self.q.getCommand() == "gettemporarypasswd":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand('gettemporarypasswd')
            r.setData(GraphicPasswords().getPassword(self.q.getData()))
            
            return r
        
        # Usuwanie tymczasowego hasła
        if self.q.getCommand() == "removetemporarypasswd":
            # Tworzenie odpowiedzi
            r = Response("removetemporarypasswd")
            
            # Usuwa tymczasowe hasło z bazy danych
            GraphicPasswords().deletePassword(self.q.getData())
            
            return r
            
        
        return None