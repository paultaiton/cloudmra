#!/usr/bin/python3
'''
Created on Oct 12, 2019

@author: paul
'''
import sys
import json
import os
#import logging

from cloudmra.cloudhandler import cloudhandler
from cloudmra.aliashandler import aliashandler
from cloudmra.deliveryhandler import deliveryhandler

def main(args=None):
	if args is None:
		args = sys.argv[1:]
	with open("alias.json", 'r') as aliasjson:
		alias = aliashandler(aliasjson.read())
		
	with open(os.environ["HOME"] + "/.cloudmra/cloudmra.config", 'r') as configjson:
		CONFIG = json.loads(configjson.read())
	
	QUEUE_NAME = CONFIG.get("CLOUD").get("QUEUE_NAME")
	EXPIRE_BUCKET = CONFIG.get("CLOUD").get("EXPIRE_BUCKET")
	DELIVERY_HOST = CONFIG.get("DELIVERY").get("HOST")
	DELIVERY_PORT = CONFIG.get("DELIVERY").get("PORT")

	inhandler = cloudhandler(queue_name=QUEUE_NAME, expire_bucket=EXPIRE_BUCKET)
	outhandler = deliveryhandler(host=DELIVERY_HOST, port=DELIVERY_PORT)
	emails = True
	while emails is not False:
		emails = inhandler.fetch()
		if emails:
			for email in emails:
				message, receipients = email[0]
				default = alias.get_default(list(receipients)[0])
				adressee = set()
				confirmed = set()
				todefault = False
				for address in receipients:
					adressee.add(alias.get_alias(address))
				for i in adressee:
					if (outhandler.deliver(message, i)):
						confirmed.add(i)
					else:
						todefault = True 
				if todefault and default not in confirmed: 
					outhandler.deliver(message, default)
					confirmed.add(default)
				if len(confirmed) > 0:
					inhandler.delete(email)
	return 0

if __name__ == '__main__':
	sys.exit(main())