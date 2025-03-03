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
            if not self.domains.get(entry.get('name', None).lower()):  # todo None.lower will cause exceptions, what should be done?
                self.domains[entry.get('name', None).lower()] = domain(entry.get('name', None).lower(),
                                                                     entry.get('default', None).lower())
                for src, dest in entry['aliases'].items():
                    self.domains[entry['name']].set_alias(src, dest)
            else:
                print("ERROR: your alias configuration is broken. Do you have multiple definitions for the same domain?")
                exit(2)

    def get_alias(self, address):
        user, host = address.split(sep='@')
        response = self.domains.get(host.lower()).get_alias(user)  # todo needs a way to catch invalid domains.
        if '@' in response:
            return response
        else:
            return response + '@' + host

    def get_default(self, address):
        user, host = address.split(sep='@')
        response = self.domains.get(host.lower()).get_default()  # todo needs a way to catch invalid domains.
        if '@' in response:
            return response
        else:
            return response + '@' + host


if __name__ == "__main__":
    print("ERROR: This module should not be called directly.")
    exit(1)
