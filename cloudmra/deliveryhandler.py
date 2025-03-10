'''
@author: paul
'''
import smtplib
# from smtplib import SMTPUTF8


class deliveryhandler():
    INVALIDUSER = False

    def __init__(self, host="localhost", port=24, user=None, password=None):
        self.hostname = host
        self.port = port
        self.user = user
        self.password = password
        self.lmtp = smtplib.LMTP(host=host, port=port)  # , user=user, password=password)

    def deliver(self, message, receipient):
        while True:
            try:
                self.lmtp.send_message(msg=message, from_addr=None, to_addrs=receipient)  # , mail_options=(SMTPUTF8))
            except smtplib.SMTPRecipientsRefused:
                return self.INVALIDUSER
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused):
                self.lmtp.connect(host=self.hostname, port=self.port)
            # except UnicodeEncodeError:  # Do not run with this uncommented, will cause endless loop
            #     print("debug")
            else:
                return True


if __name__ == "__main__":
    print("ERROR: This module should not be called directly.")
    exit(1)
