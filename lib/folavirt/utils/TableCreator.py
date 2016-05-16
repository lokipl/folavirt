#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from folavirt.utils.Database import Database

class TableCreator():    
    def __init__(self):
        self.database = Database()
        
    def createOwnershipTableIfNeeded(self, tablename):
        """
        Tworzenie tabeli dla właśności maszyn wirtualnych
        
        @param Nazwa tabeli
        """
        # Sprawdzanie czy tabela istnieje
        self.database.getCursor().execute('SHOW TABLES;')
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            # Jeśli nie ustnieje, utwórz tabelę
            print "Tworzenie tabeli " + self.database.getPrefix() + tablename
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename +"""(
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100),
                    user VARCHAR(100)
                )
               """
            self.database.getCursor().execute(query)
            
    def createVolumeGroupsTableIfNeeded(self, tablename):
        """
        Tabela grup woluminowych
        """
        # Pobieranie tabel z bazy danych
        self.database.getCursor().execute('SHOW TABLES;')
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    vgname VARCHAR(100),
                    host VARCHAR(100)
                )
                """
            self.database.getCursor().execute(query)
            
    def createBaseDisksTableIfNeeded(self, tablename):
        """
        Tabela dysków bazowych
        
        @param void
        @return void
        """
        self.database.getCursor().execute('SHOW TABLES;')
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    baselv VARCHAR(100),
                    vgname VARCHAR(100),
                    host VARCHAR(100)
                )
                """
            self.database.getCursor().execute(query)
    
    def createIscsiConfigurations(self, tablename):
        """
        Tabela konfiguracji dysków iSCSI
        
        @param nazwa tabeli
        @return void
        """
        self.database.getCursor().execute('SHOW TABLES')    
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `option` VARCHAR(100),
                    `value` VARCHAR(100),
                    `host` VARCHAR(100)
                );
                """
            self.database.getCursor().execute(query)
            return True
        
        return False

    def createSnapshotTableIfNeed(self, tablename):
        """
        Tabela snapshotów
        
        @param nazwa tabeli
        @return void
        """
        self.database.getCursor().execute('SHOW TABLES')    
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `vgname` VARCHAR(100),
                    `baselv` VARCHAR(100),
                    `host` VARCHAR(100),
                    `device` VARCHAR(100)
                );
                """
            self.database.getCursor().execute(query)
            return True
        
        return False
    
    def createGraphicConsolePasswordsTableIfNeed(self, tablename):
        """
        Tabela tymczasowych haseł do konsol graficznych
        
        @param nazwa tabeli
        @return void
        """
        self.database.getCursor().execute('SHOW TABLES')    
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `name` VARCHAR(100),
                    `passwd` VARCHAR(100)
                );
                """
            self.database.getCursor().execute(query)
            return True
        
        return False
    
    def createLaboratoryTableIfNeed(self, tablename):
        """
        Tworzy tabelę laboratoriów
        
        @param nazwa tabeli
        @return void
        """
        self.database.getCursor().execute('SHOW TABLES')    
        tables = self.database.getCursor().fetchall()
        try:
            [x[0] for x in tables].index(self.database.getPrefix() + tablename)
        except ValueError:
            query = """
                CREATE TABLE """ + self.database.getPrefix() + tablename + """(
                    `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `lab` VARCHAR(100),
                    `baselv` VARCHAR(100),
                    `name` VARCHAR(100),
                    `agent` VARCHAR(100),
                    `lun` INT,
                    `idonhost` INT
                );
                """
            self.database.getCursor().execute(query)
            return True
        
        return False