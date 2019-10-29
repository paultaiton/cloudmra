'''
@author: paul
'''
import smtplib
class deliveryhandler():
	INVALIDUSER = False
	def __init__(self, host="localhost", port=24, user=None, password=None):
		self.hostname = host
		self.port = port
		self.user = user
		self.password = password
		self.lmtp = smtplib.LMTP(host=host, port=port)#, user=user, password=password)
		
	def deliver(self, message, receipient):
		try:
			self.lmtp.sendmail(from_addr='', to_addrs=receipient, msg=message)
		except smtplib.SMTPRecipientsRefused :
			return self.INVALIDUSER
		except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused):
			self.lmtp.connect(host=self.hostname, port=self.port)
			self.lmtp.sendmail(from_addr='', to_addrs=receipient, msg=message)
		return True
			
if __name__ == "__main__":
	print("ERROR: This module should not be called directly.")
	exit(1)
