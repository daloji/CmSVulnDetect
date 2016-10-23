#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import abc
import urllib2
import re
from PageParser import PageParser

REGEX = {
    'Drupal'  : 'Drupal \s*?([\d.]+),',
    'WordPress' : 'Version\s*?([\d.]+)',
    'Joomla' : 'Joomla\s*?([\d.]+)'
      }

FILE  = {
    'Drupal'  : 'CHANGELOG.txt',
    'WordPress' : 'readme.html',
    'Joomla' : 'README.txt'
      }

class Cms:
  
    def __init__(self,url):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
        self.url = url
        self.Modules_List=[]
	self.Theme_List=[]
	self.version = None
        self.error = ""
        
    @abc.abstractmethod
    def scan(self):
        """Debut scan de la cible ."""
        return
      
    def detection(self):
	self.verbose("\t *  Detection Thèmes, plugins et modules")
	try:
	    response = urllib2.Request(self.url, None, headers=self.headers)
	    data =  urllib2.urlopen(response).read().decode('utf-8')
	    parse = PageParser(self.url)
	    parse.feed(data)
	    self.Modules_List=parse.getAllModules()
	    self.Modules_List=sorted(list(set(self.Modules_List)))
	    self.__deleteJQueryModules()
	    self.Theme_List=parse.getAllThemes()
	    self.Theme_List=sorted(list(set(self.Theme_List)))
	except urllib2.HTTPError, e:
	     self.error = e
	     
	      
	      
    def __deleteJQueryModules(self):
      if len(self.Modules_List) > 0:
	for module in self.Modules_List:
	    if "jquery." in module:
		self.Modules_List.remove(module)
	
	
	
    def getVersion(self,type):
      """ recuperation de la version """
      file = None
      regex = None
      for keys in FILE:
	 if keys == type:
	   file = FILE[keys]
	   regex = REGEX[keys]
      
      if file is None or regex is None:
	 return
      
      try:
	 response = urllib2.Request(self.url+'/'+file, None, headers=self.headers)
	 data =  urllib2.urlopen(response).read()
	 pattern = re.compile(regex,re.MULTILINE)
	 result =  re.findall(pattern,data)[:1]
	 if len(result)>0:
	     self.version=result[0]
	  
      except urllib2.HTTPError, e:
	  self.error = e
    
    def verbose(self,msg):
	sys.stderr.write(" %s\n" % (msg))
	
	
    def showThemes(self):
      if len(self.Theme_List)>0:
	theme =""
	for thm in self.Theme_List:
	     theme = theme + "  " + thm
	     
	self.verbose("\t -  themes[*]  " +theme)  

    
    def showPlugins(self):
      if len(self.Modules_List)>0:
	module =""
	for modl in self.Modules_List:
	     module = module + "  " + modl
	     
	self.verbose("\t -  modules[*]  " +module)  
   
