#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys,urllib2,urllib,re
from Cms import Cms
from PageParser import PageParser

class CmsWP(Cms):
	
	  def __init__(self,url):
		Cms.__init__(self,url)
		self.isWordPress = 0
		
		  
	  def firstDectectionWP(self):
	      self.verbose("  *  Récuperation configuration")
	      self.isWordPress = 0
	      
	      htmltext = ""
	      try:
		
		response = urllib2.Request(self.url+"/wp-config.php", None, headers=self.headers)
		htmltext = urllib2.urlopen(response).read()
		if len(htmltext):
		  self.verbose("  =>  CMS Wordpress")
		  self.isWordPress = 1
	      except urllib2.HTTPError, e:
		#print e.code
		if e.code == 403 and len(htmltext):
		     self.verbose("  =>  CMS Wordpress")
		     self. isWordPress = 1
	 
	    
	  def secondDetectionWP(self):
		self.verbose("  *  Lecture de la page")
		self.isWordPress = 0
		try:
		    response = urllib2.Request(self.url, None, headers=self.headers)
		    data =  urllib2.urlopen(response).read().decode('utf-8')
		    parse = PageParser(self.url)
		    parse.feed(data)
		    self.Modules_List=parse.getAllModules()
		    self.Modules_List=sorted(list(set(self.Modules_List)))
		    self.Theme_List=parse.getAllThemes()
		    self.Theme_List=sorted(list(set(self.Theme_List)))
		except urllib2.HTTPError, e:
		    self.verbose(e)
		


		  
		
	  def scan(self):
	      self.verbose("[+] Detection WordPress ")
	      self.getversion()
	      if self.isWordPress:
		self.firstDectectionWP()
		self.secondDetectionWP()
		self.verbose("    -  CMS Wordpress version " +self.version)
		self.detection()
		self.showThemes()
		self.showPlugins()
	      
	  
	  
	  def getversion(self):
	      try:
		response = urllib2.Request(self.url+'/readme.html', None, headers=self.headers)
		data =  urllib2.urlopen(response).read()
		regex = "Version\s*?([\d.]+)"
		pattern = re.compile(regex,re.MULTILINE)
		result =  re.findall(pattern,data)[:1]
		if len(result)>0:
		    self.version=result[0]
		    self.isWordPress = 1
	      except urllib2.HTTPError, e:
		  self.verbose(e)
		  
	  
	  def isCmsWP(self):
	    return self.isWordPress
		  
		  
	  def debug(self):
	    print self.Modules_List
	    print self.Theme_List
	    
	      
	    
		      


if __name__ == "__main__":
	cvedb = cmsWP(sys.argv[1:][0])
	cvedb.scan()
	
	  
