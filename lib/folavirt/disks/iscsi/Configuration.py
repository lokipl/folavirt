#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
import datetime

from folavirt.utils.TableCreator import TableCreator
from folavirt.utils.Database import Database

class Configuration():
    def __init__(self):
        self.tablename = "iscsiconf"
        self.database = Database()
        
        result = TableCreator().createIscsiConfigurations(self.tablename)
        if (result):
            self.setValue("iqnbasename", "BaseDisks")
            self.setValue("iqndate", "2014-07")
            self.setIqnhostname(socket.gethostname())
        
    def setValue(self, option, value):
        if (self.getValue(option) != None):
            # Wykonywanie aktualizacji rekordu
            query = "UPDATE " + self.database.getPrefix() + self.tablename + " SET value = '" + value + "' "
            query += "WHERE `option` = '" + option + "' AND host = '" + socket.gethostname() + "';"

            self.database.getCursor().execute(query)
            self.database.commit()
        else:
            query = "INSERT INTO " + self.database.getPrefix() + self.tablename + "(`option`, `value`, `host`) "
            query += "VALUES('" + option + "', '" + value + "', '" + socket.gethostname() + "')"
        
            self.database.getCursor().execute(query)
            self.database.commit()
            
    def getValue(self, option):
        query = "SELECT value FROM " + self.database.getPrefix() + self.tablename + " WHERE `option` = '" + option + "' AND host = '" + socket.gethostname() + "'"
        self.database.getCursor().execute(query)
        result = self.database.getCursor().fetchall()
        if (len(result) == 0):
            return None
        else:
            return result[0][0]
        
    def setIqnbasename(self, value):
        self.setValue("iqnbasename", value)
        
    def getIqnbasename(self):
        """
        Zwraca nazwę zasobu z woluminami bazowymi
        
        @param void
        @return nazwa
        """
        value = self.getValue("iqnbasename")
        if value == None:
            value = "basedisks"
            self.setValue("iqnbasename", value)
        
        return value
    
    def setIqndate(self, value):
        """
        Ustawia datę do IQN
        
        @param void
        @return wartość
        """
        self.setValue("iqndate", value)
        
    def getIqndate(self):
        """
        Zwraca datę do IQN
        
        @param void
        @return data
        """
        value = self.getValue("iqndate")
        if value == None:
            value = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month)
            self.setValue("iqndate", value)          
        
        return value
    
    def setIqnhostname(self, value):
        """
        Ustawia nazwę hosta
        
        @param nazwa
        @return void
        """
        self.setValue("iqnhostname", value)
        
    def getIqnhostname(self):
        """
        Zwraca nazwę hosta. Jeśli nie ustawione ustawia na domyślną wartość (socket.gethostname)
        
        @param void
        @return nazwa
        """
        value = self.getValue("iqnhostname")
        if value == None:
            self.setValue("iqnhostname", socket.gethostname())
            value = socket.gethostname()
        
        return value