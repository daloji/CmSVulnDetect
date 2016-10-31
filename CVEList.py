#! /usr/bin/python -tt
# -*- coding: utf-8 -*- 

import urllib2
import zipfile
import os
import sys
import tempfile
import shutil
import xml.etree.ElementTree as ET
import xml.parsers.expat


EXIT_ERROR = 1
EXIT_SUCCESS = 0

NAMESPACES = {
    'def'  : 'http://scap.nist.gov/schema/feed/vulnerability/2.0',
    'vuln' : 'http://scap.nist.gov/schema/vulnerability/0.4',
    'cvss' : 'http://scap.nist.gov/schema/cvss-v2/0.2',
	'nvdcve' :'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-2016.xml.zip'
}

class CVEList(object):
    
	def __init__(self):
	    self.filename =""
	    self.vulnfields = [ "last-modified-datetime",
                            "published-datetime",
                            "summary" ]
	    self.cvssfields = [ "access-complexity",
                            "access-vector",
                            "authentication",
                            "availability-impact",
                            "confidentiality-impact",
                            "integrity-impact",
                            "score" ]
	    self.data = {}
	    for field in self.vulnfields + self.cvssfields:
		self.data[field]=""
	    self.data['refs'] = []
	    self.data['vulnerable-software-list'] = []
		
	def __downloadNISTCve(self):
		self.verbose("  * Connexion vers NIST CVE ")
		url = NAMESPACES['nvdcve'];
		file_name = url.split('/')[-1]
		u = urllib2.urlopen(url)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		self.verbose("  * Téléchargement dernière mise à jour des Vulnérabilités")
		self.verbose("   %s Bytes: %s" % (file_name, file_size))
		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break

			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			print status,
		f.close()
		self.filename = file_name	
	
	def __extractFile(self,directory):
		self.verbose(" * Extraction du fichier de vulnerabilité")
		with zipfile.ZipFile(self.filename) as zip_file:
			for member in zip_file.namelist():
				filename = os.path.basename(member)
				# skip directories
				if not filename:
					continue

				# copy file (taken from zipfile's extract)
				source = zip_file.open(member)
				target = file(os.path.join(directory, filename), "wb")
				with source, target:
					shutil.copyfileobj(source, target)
		
					
	def parseInput(self):
		self.verbose("[+] Récupération dernière mise à jour des Vulnérabilées")
		try:
			directory_name = tempfile.mkdtemp()
			self.__downloadNISTCve()
			self.__extractFile(directory_name)
			xml_file = self.filename.split(".zip")[0]
			tree = ET.parse(directory_name+"/"+xml_file)
		except xml.parsers.expat.ExpatError, e:
			sys.stderr.write("Unable to parse input as valid XML: %s\n" % e.args[0])
			sys.exit(EXIT_ERROR)
            # NOTREACHED
	
	
	
	def updateDB(self,xml,typeCms):
	    self.verbose("[+] Lecture fichier des vulnerabilites")
	    root = xml.getroot()
	    for child in root.findall('./{%s}entry' % NAMESPACES['def']):
		cve = CVE()
		cve.data['id'] = child.attrib['id']
		for field in cve.vulnfields:
		    node = child.find('./{%s}%s' % (NAMESPACES['vuln'], field))
		    cve.data[field] = node.text
		swlist = child.find('./{%s}vulnerable-software-list' % NAMESPACES['vuln'])
		if swlist is not None:
		    for sw in swlist.findall('./{%s}product' % NAMESPACES['vuln']):
			cve.data['vulnerable-software-list'].append(sw.text)

		for ref in child.findall('./{%s}references' % NAMESPACES['vuln']):
		    r = ref.find('./{%s}reference' % NAMESPACES['vuln'])
		    if r is not None:
			cve.data['refs'].append(r.attrib['href'])

		cvss = child.find('./{%s}cvss/{%s}base_metrics' % (NAMESPACES['vuln'],
								    NAMESPACES['cvss']))
		if cvss is not None:
		    for field in cve.cvssfields:
			node = cvss.find('./{%s}%s' % (NAMESPACES['cvss'], field))
			if node is not None:
			    cve.data[field] = node.text
			else:
			    sys.stderr.write("Unable to find cvss field '%s' for %s" % (field, cve.data['id']))

		if typeCms in cve.data["summary"]:
		    self.verbose("   *  id vulnerabilité %s..." % cve.data['id'])
		    self.verbose("    -  é %s..." % cve.data["summary"])
		if not self.cveInDB(cve, conn):
		    #self.insertCVE(cve, conn)
		    pass
			
	def verbose(self, msg, level=1):
         sys.stderr.write(" %s\n" % (msg))
    

