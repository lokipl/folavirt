#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.permissions.Ownership import Ownership
from folavirt.networking.Response import Response
from folavirt.remote.Domain import Domain
from folavirt.virt.Domain import Statuses

class OwnershipResponse():
    def __init__(self, q):
        self.q = q
        
    def getResponse(self):
        # Dodawanie uprawnień
        if self.q.getCommand() == "ownership":
            # Tworzenie obiektu odpowiedzi
            r = Response()
            r.setCommand("ownership")
            
            # Czy podano parametr
            if len(self.q.getData()) == 2:
                user = r.getData()[0]
                domain = Domain(r.getData()[1])
                
                result = Ownership().isAllowed(domain, user)
                r.setData(result)
                
                return r
        
        # Lista maszyn wirutalnych
        if self.q.getCommand() == "ownership-list":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("ownership-list")
            
            if self.q.getData() == {}:
                # Jesli nie zdefiniowano w zapytaniu uid to zwróć całą listę
                r.setData(Ownership().getList())
            else:
                # Opcjonalnie nazwa użytkownika
                user = self.q.getData()
                
                # UStawianie danych w odpowiedzi
                r.setData(Ownership().getList(user))
            
            return r
        
        # Lista maszyn wirtualnych wraz ze statusami
        if self.q.getCommand() == "ownership-list-withstatuses":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("ownership-list")
            
            # Wymagane wysłanie uid
            user = self.q.getData()
                
            # Ustawianie danych w odpowiedzi
            rows = Ownership().getList(user)
            
            # Tablica wynikowa
            result = []
            
            for row in rows:
                # Tworzenie obiektu domeny
                domain = Domain(row[0])
                
                # Szukanie hosta na jakim znajduje sie domena
		try:
                	domain.searchAgent()
		except:
			continue                

                # Domyślnie nie ma statusu, domeny nie zdefiniowane na hoście, taki mają status
                state = Statuses.DOMAIN_NOSTATE
                
                # Jeśli domena ma hosta, zwróc status
                if domain.getHost() != None:
                    state = domain.getState()
                
                result.append({'name': row[0], 'state': state})
            
            # Ustawianie danych odpowiedzi
            r.setData(result)
            
            return r
        
        # Czyści uprawnienia do domeny
        if self.q.getCommand() == "ownership-cleandomain":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("ownership-cleandomain")
            
            name = Domain(self.q.getData())
            Ownership().cleanDomain(name)
            
            return r
        
        # Zabiera wszystkie uprawnienia użytkownikowi
        if self.q.getCommand() == "ownership-cleanuser":
            r = Response()
            r.setCommand("ownership-cleanuser")
            
            user = self.q.getData()
            Ownership().cleanUser(user)
            
            return r
        
        # Dodawanie uprawnienia lub zabranie
        if self.q.getCommand() == "ownership-add" or self.q.getCommand() == "ownership-delete":
            # Tworzenie odpowiedzi
            r = Response()
            r.setCommand("ownership-add")

            # Format tablicy [user, maszyny]
            if len(self.q.getData()) == 2:
                user = self.q.getData()[0]
                name = self.q.getData()[1]
                domain = Domain(name)
                
                if self.q.getCommand() == "ownership-add":
                    Ownership().add(domain, user)
                if self.q.getCommand() == "ownership-delete":
                    Ownership().delete(domain, user)
                
                r.setData("OK")
                return r
            else:
                r.setErrorCode(1)
                return r                
            
        return None
