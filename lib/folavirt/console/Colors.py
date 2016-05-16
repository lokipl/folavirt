#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Colors():
    bold = u"\033[1m"
    nobold = u"\033[0m"
    green = u"\033[01;32m"
    nogreen = u"\033[0m"
    red = u"\033[01;31m"
    yellow = u"\033[01;33m"
    nocolor = u"\033[0m"
    
    @staticmethod
    def disable():
        Colors.bold = ""
        Colors.nobold = ""
        Colors.green = ""
        Colors.nogreen = ""
        Colors.red = ""
        Colors.yellow = ""
        Colors.nocolor = ""
    
    @staticmethod
    def setbold(text):
        """
        Pogrubia tekst
        """
        return Colors.bold + text + Colors.nobold
    
    @staticmethod
    def setgreen(text):
        """
        Zwraca zielony tekst
        """
        return Colors.green + text + Colors.nocolor
    
    @staticmethod
    def setred(text):
        """
        Zwraca czerwony tekst
        """
        return Colors.red + text + Colors.nocolor
    
    @staticmethod
    def setyellow(text):
        """
        Zwraca żółty tekst
        """
        return Colors.yellow + text + Colors.nocolor