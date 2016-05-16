#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from random import randint

from folavirt.console.Colors import Colors
from folavirt.console.Params import Params
from folavirt.networking.Query import Query
from folavirt.remote.RemoteObject import RemoteObject
from folavirt.remote.Agent import getOnlineAgents

class OwnershipConsole():
    """
    Polecenia służące do nadawania uprawnień do maszyn
    """
    def __init__(self):
        # Obiekt zdalnego połączenia
        self.ro = None
        
        if Params().getArg(0) == "ownership":
            # Lista uprawnień
            if Params().getArg(1) == "list":
                self.list()
                sys.exit(0)
            
            # Dodawanie uprawnień
            if Params().getArg(1) == "add":
                self.add()
                sys.exit(0)
            
            # Usuwanie uprawnień
            if Params().getArg(1) == "delete":
                self.delete()
                sys.exit(0)
                
            # Czyszczenie uprawnień
            if Params().getArg(1) == "clean":
                self.clean()
                sys.exit(0)       
            
            # Lista użytkowników
            if Params().getArg(1) == "users":
                self.users()
                sys.exit(0)
            
            self.printhelp()
            sys.exit(0)
            
    @staticmethod          
    def printhelp(ljust1 = 37, ljust2 = 15):
        """
        Wypisuje pomoc
        
        @param void
        @return void
        """
        print("\n " + u"Uprawnienia do maszyn wirtualnych")
        print("  " + Colors.setbold("ownership list".ljust(ljust1)) + u"wypisuje wszystkie prawa własności do domen")
        print("  " + Colors.setbold("ownership add $VM $U".ljust(ljust1)) + u"dodaje prawo własności")
        print("  " + Colors.setbold("ownership delete $VM $U".ljust(ljust1)) + u"zabiera prawo własności")
        print("  " + Colors.setbold("ownership clean vm $VM".ljust(ljust1)) + u"czyści wszystkie prawa do domeny")
        print("  " + Colors.setbold("ownership clean user $U".ljust(ljust1)) + u"zabiera wszystkie prawa użytkownikowi")
    
    def _getRemoteObject(self):
        """
        Zwraca zdalny obiekt, do wysyłania poleceń
        
        @param void
        @return folavirt.remote.RemoteObject
        """
        if self.ro == None:
            # Pobieranie listy agentów
            agents = getOnlineAgents()
            
            if len(agents) == 0:
                print(Colors.setred(" * ") + u"Brak konfiguracji agentów. Wykonaj najpierw " + Colors.setbold(u"agent discover"))
                sys.exit(0)
            
            # Losowanie agenta
            i = randint(0,len(agents)-1)
            
            # Tworzenie obiektu połączenia
            ro = RemoteObject()
            ro.setAddress(agents[i].getAddress())
            ro.setPort(agents[i].getPort())
            
            self.ro = ro
        
        return self.ro
    
    def list(self):
        """
        Wyświetla listę wszystkich uprawnień
        
        @param void
        @return void
        """
        # Tworzenie zapytania
        q = Query("ownership-list")
        
        # Sprawdzenie czy podano nazwę użytkownika
        if Params().argLen() == 3:
            # Dodawanie uid do zapytania
            q.setData(Params().getArg(2))

        # Wykonywanie zapytania i uzyskiwanie odpowiedzi
        response = self._getRemoteObject().execute(q)
        self._getRemoteObject().quit()
        
        records = response.getData()
        
        if len(records) > 0:
            print(Colors.setbold("Nazwa domeny".ljust(31)) + Colors.setbold(u"Użytkownik"))
        
            # Wyświetlanie tabelki
            for record in records:
                print(record[0].ljust(30)),
                print(str(record[1]))
    
    def add(self):
        """
        Dodaje uprawnienie
        
        @param void
        @return void
        """
        if Params().argLen() == 4:
            # Pobieranie parametrów
            name = Params().getArg(2)
            users = Params().getArgList(3)

            for user in users:
                # Tworzenie zapytania
                q = Query()
                q.setCommand("ownership-add")
                q.setData([user, name])
                
                # Wykonywanie zapytania
                self._getRemoteObject().execute(q)
                
                print(Colors.setgreen(" * ") + u"Dodano maszynę " + Colors.setbold(name) + u" użytkownikowi " + Colors.setbold(user))

            
            self._getRemoteObject().quit()
            
    def delete(self):
        """
        Usuwa wpis
        
        @param void
        @return void
        """
        # Pobieranie parametrów
        name = Params().getArg(2)
        users = Params().getArgList(3)
            
        owns = self._getRemoteObject().execute(Query("ownership-list")).getData()
                   
        if name == "":
            print(Colors.setred(" * ") + u"Nie podany nazwy maszyny wirtualnej")
            sys.exit(0)
           
        if not name in [own[0] for own in owns]:
            print(Colors.setred(" * ") + u"Nie ma zdefiniowanych praw dla takiej maszyny wirtualnej")
            sys.exit(0)
                    
        if users == []:
            print(Colors.setred(" * ") + u"Musisz zdefiniować użytkownika")
            sys.exit(0)
            
        if len([user for user in users if user in [own[1] for own in owns if own[0] == name]]) == 0:
            print(Colors.setred(" * ") + u"Maszyna nie jest przypisana do żadnego z podanych użytkowników")
            sys.exit(0)
            
        for user in users:
            if not user in [own[1] for own in owns if own[0] == name]:
                print(Colors.setred(" * ") + u"Użytkownik " + user + u" nie posiada praw do maszyny " + name)
                continue
            
            # Tworzenie nowego zapytania
            q = Query()
            q.setCommand("ownership-delete")
            q.setData([user, name])
                
            # Wykonywanie zapytania
            self._getRemoteObject().execute(q)
            
            print(Colors.setgreen(" * ") + u"Użytkownikowi " + user + u" usunięto prawa do maszyny " + name)
            
        # Koniec połączenia
        self._getRemoteObject().quit()
             
    def clean(self):
        """
        Czyści uprawnienia do domeny lub wszystkie użytkownikowi
        """
        # Czyszczenie domeny
        if Params().getArg(2) == "vm":
            owns = self._getRemoteObject().execute(Query("ownership-list")).getData()
            
            if not Params().getArg(3) in [own[0] for own in owns]:
                print(Colors.setred(" * ") + u"Nie ma zdefiniowanych praw dla takiej maszyny wirtualnej")
                sys.exit(0)
            
            # Tworzenie zapytania
            q = Query()
            q.setCommand('ownership-cleandomain')
            q.setData(Params().getArg(3))
                
            self._getRemoteObject().execute(q)
            self._getRemoteObject().quit()
                
            print (Colors.setgreen(" * ") + u"Wyczyszczono wszystkie uprawnienia do domeny " + Params().getArg(3))
            
            sys.exit(0)
            
        # Czyszczenie uid
        if Params().getArg(2) == "user":
            users = Params().getArgList(3)
            
            owns = self._getRemoteObject().execute(Query("ownership-list")).getData()
            
            if len([own[1] for own in owns if own[1] in users]) == 0:
                print(Colors.setred(" * ") + u"Nie ma żadnych przypisanych maszyn dla podanych użytkowników")
                sys.exit(0)
            
            for user in users:
                if not user in [own[1] for own in owns if own[1] in users]:
                    print(Colors.setred(" * ") + u"Użytkownik " + user + u" nie posiada żadnych maszyn wirtualnych")
                    continue
                
                # Tworzenie zapytania
                q = Query()
                q.setCommand('ownership-cleanuser')
                q.setData(user)
                    
                # Wykonywanie zapytania
                self._getRemoteObject().execute(q)
                    
                print(Colors.setgreen(" * ") + u"Usunięto wszystkie uprawnienia użytkownikowi " + user)
                
            self._getRemoteObject().quit()
            
            sys.exit(0)
            
        self.printhelp()
