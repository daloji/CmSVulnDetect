import re,urllib2
from HTMLParser import HTMLParser

class PageParser(HTMLParser):
	
	def __init__(self,url):
		HTMLParser.__init__(self)
		self.ListModule=[]
		self.ListTheme=[]
		self.version = ""
		self.tag=""
		self.url=url
		
	def getAllModules(self):
		return self.ListModule
		
	def getAllThemes(self):
		return self.ListTheme
	
	def getVersion(self):
		response = urllib2.urlopen(self.url+'/CHANGELOG.txt')
		data = response.read()
		regex = "Drupal \s*?([\d.]+),"
		pattern = re.compile(regex,re.MULTILINE)
		result =  re.findall(pattern,data)[:1]
		if len(result)>0:
			self.version=result[0]
		return self.version
		
	
	def __computeModuleFromJQuery(self,data):
		for value in data:
			tuples = re.findall(r'.*modules(.*)', value)
			for attr in tuples:
				moduleName = attr.split("/")[1].split("\\")[0]
				if not any(moduleName == s for s in self.ListModule):
					self.ListModule.append(moduleName)
				
	def __findModule(self,url,splitvalue):
		module = url.split(splitvalue)
		if len(module)>1 :
			if module[0][-1] == '/' or module[0][-1:] == '\\\\':
				moduleName = module[1].split("/")[1].split("\\")[0]
				if not any(moduleName == s for s in self.ListModule):
					self.ListModule.append(moduleName)
				else:
					self.__findModule(module[1],moduleName)
 
				

	def __findTheme(self,url,splitvalue):
		theme = url.split(splitvalue)
		if len(theme)>1 :
			if theme[0][-1] == '/' or theme[0][-1:] == '\\\\':
				themeName = theme[1].split("/")[1].split("\\")[0]
				if not any(themeName == s for s in self.ListTheme):
					self.ListTheme.append(themeName)
				
					
	def handle_starttag(self, tag, attrs):
		if tag == "script" or tag == "link":
			self.tag=1
			for attr in attrs:
				if len(attr)>=2 and (str(attr[0]) == "src" or str(attr[0]) == "href") :
				  self.__findModule(attr[1],"module")
				  self.__findTheme(attr[1],"themes")
				  self.__findModule(attr[1],"plugins")
					
	
	def handle_endtag(self, tag):
		if tag == "script":
			self.tag = 0
	def handle_data(self, data):
		if self.tag == 1:
			data = data.split("\"")
			self.__computeModuleFromJQuery(data)
			
	def handle_comment(self, data):
		pass
		
	def handle_entityref(self, name):
		pass
	
	def handle_charref(self, name):
		pass
	def handle_decl(self, data):
		pass
