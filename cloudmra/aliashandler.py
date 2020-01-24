'''
@author: paul
'''
import json

class domain():
	def __init__(self, name, default):
		self.name = name
		self.default = default
		self.alias = dict()
	
	def set_alias(self, source, destination):
		self.alias[source] = destination 

	def get_alias(self, source):
		if source in self.alias:
			return self.alias.get(source)
		else:
			return source
		
	def get_default(self):
		return self.default

		
class aliashandler():
	'''
	classdocs
	'''
	def __init__(self, config_json):
		'''
		Constructor
		'''
		self.domains = dict()
		for entry in json.loads(config_json).get("domains"):
			self.domains[entry['name']] = domain(entry['name'], entry['default'])
			for src, dest in entry['aliases'].items():
				self.domains[entry['name']].set_alias(src, dest)
			

	def get_alias(self, address):
		user, host = address.split(sep='@')
		response = self.domains[host].get_alias(user)
		if '@' in response:
			return response
		else:
			return response + '@' + host
			
	def get_default(self, address):
		user, host = address.split(sep='@')
		response = self.domains[host].get_default()
		if '@' in response:
			return response
		else:
			return response + '@' + host
		
if __name__ == "__main__":
	print("ERROR: This module should not be called directly.")
	exit(1)