#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.utils.Database import Database
from folavirt.utils.TableCreator import TableCreator

class GraphicPasswords():
    """
    Hasła dostępu do konsol graficznych. Muszą być zapisywane w bazie, 
    żeby podać użytkownikom, podczas pierwszego logowania
    """
    def __init__(self):
        self.tablename = "graphicpasswords"
        TableCreator().createGraphicConsolePasswordsTableIfNeed(self.tablename)
        self.database = Database()
    
    def deletePassword(self, name):
        """
        Usuwa zdefiniowane hasła do domeny
        
        @param nazwa
        @return void
        """
        query = "DELETE FROM " + self.database.getPrefix() + self.tablename + " WHERE name = '" + name + "'"
        self.database.getCursor().execute(query)
        self.database.commit()
       
    def getPassword(self, name):
        """
        Zwraca hasło
        
        @param nazwa
        @return hasło
        """
        query = "SELECT passwd FROM " + self.database.getPrefix() + self.tablename + " WHERE name = '" + name + "'"
        self.database.getCursor().execute(query)
        result = self.database.getCursor().fetchall()
        
        if len(result) == 0:
            return False
        else:
            return result[0][0]
        
    def setPassword(self, name, passwd):
        """
        Dodaje do bazy danych tymczasowe hasło, usuwa stary wpis
        
        @param nazwa
        @param hasło
        @return void
        """
        self.deletePassword(name)
        
        query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(name, passwd) "
        query += "VALUES('"+name+"', '"+passwd+"')"
        
        self.database.getCursor().execute(query)
        self.database.commit()
        