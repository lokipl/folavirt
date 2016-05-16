#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.utils.TableCreator import TableCreator
from folavirt.utils.Database import Database

class Ownership():
    def __init__(self):
        TableCreator().createOwnershipTableIfNeeded('ownership')
        self.database = Database()

    def add(self, domain, user):
        """
        Dodaj własność
        
        @param Domena
        @param uid
        """
        query =  "INSERT INTO " + self.database.getPrefix() + "ownership(name, user) "
        query += "VALUES('" + domain.getName() + "','" + user + "')"   
      
        self.database.getCursor().execute(query)
        self.database.commit()
    
    def delete(self, domain, user):
        """
        Usuwa własność
        
        @param Domena
        @param user
        @return void
        """
        query =  "DELETE FROM " + self.database.getPrefix() + "ownership WHERE "
        query += "name ='" + domain.getName() + "' and user = '" + user + "'"
        
        print query
        
        self.database.getCursor().execute(query)
        self.database.commit()
    

    def cleanDomain(self, domain):
        """
        Usuwa wszelkie prawa od domeny
        
        @param Domena
        """ 
        query = "DELETE FROM " + self.database.getPrefix() + "ownership WHERE name='" + domain.getName() + "'"
        print query
        
        self.database.getCursor().execute(query)
        self.database.commit()
    
    def cleanUser(self, user):
        """
        Zabiera wszystkie maszyny użytkownikowi
        
        @param user
        """
        query = "DELETE FROM " + self.database.getPrefix() + "ownership WHERE user='" + user + "'"
        
        self.database.getCursor().execute(query)
        self.database.commit()
    
    def isAllowed(self, domain, user):
        """
        Sprawdza czy użytkownik ma prawa do domeny
        
        @param Domena
        @param Uid 
        @return Boolean
        """
        query =  "SELECT * FROM " + self.database.getPrefix() + "ownership WHERE "
        query += "name='" + domain.getName() + "' AND user = '" + user + "';"

        self.database.getCursor().execute(query)
        result = self.database.getCursor().fetchall()

        if len(result) >= 1:
            return 1
        else:
            return 0
    
    def getList(self, user = -1):
        """
        Zwraca listę własności
        
        @param uid - opcjonalnie
        """        
        if user != -1 and user != None:
            query = "SELECT DISTINCT name,user FROM " + self.database.getPrefix() + "ownership WHERE user = '" + user + "' ORDER BY name,user"
        else:
            query = "SELECT DISTINCT name,user FROM " + self.database.getPrefix() + "ownership ORDER BY name,user"       

        self.database.getCursor().execute(query)
        result = self.database.getCursor().fetchall()
        
        ownlist = [[y for y in x] for x in result]
        ownlist = sorted(ownlist, key = lambda x:x[0])
        ownlist = sorted(ownlist, key = lambda x:x[1])
        
        return ownlist