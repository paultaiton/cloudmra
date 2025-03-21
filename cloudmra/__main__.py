#!/usr/bin/python3
'''
@author: paul
'''
import sys
import json
import os
import argparse
import signal
import email

from cloudmra.cloudhandler import cloudhandler
from cloudmra.aliashandler import aliashandler
from cloudmra.deliveryhandler import deliveryhandler


class overseer():

    def __init__(self, CONFIG, ALIAS, LOOP=False):
        QUEUE_NAME = CONFIG.get("CLOUD").get("QUEUE_NAME")
        EXPIRE_BUCKET = CONFIG.get("CLOUD").get("EXPIRE_BUCKET")
        DELIVERY_HOST = CONFIG.get("DELIVERY").get("HOST")
        DELIVERY_PORT = CONFIG.get("DELIVERY").get("PORT")
        self.SLEEP_TIME = CONFIG.get("DAEMON").get("SLEEP")
        if self.SLEEP_TIME is None:
            self.SLEEP_TIME = 60

        self.CONTINUE = LOOP

        self.inhandler = cloudhandler(queue_name=QUEUE_NAME, expire_bucket=EXPIRE_BUCKET)
        self.outhandler = deliveryhandler(host=DELIVERY_HOST, port=DELIVERY_PORT)
        self.alias = aliashandler(ALIAS)
        # self.email_parser = email.parser.Parser()
        self.email_parser = email.parser.BytesParser()

    def signal_handler(self, sig_int, frame_object=0):
        if sig_int is signal.SIGINT or sig_int is signal.SIGTERM:
            print("Terminate signal caught, shutting down. Please wait for graceful termination.")
            self.CONTINUE = False

    def process(self):
        email_list = True
        while email_list:
            email_list = self.inhandler.fetch()
            if email_list:
                print("Processing {0} new messages.".format(len(email_list)))
                for mail in email_list:
                    raw_message, receipients = mail[0]
                    # parsed_message = self.email_parser.parsestr(raw_message)
                    parsed_message = self.email_parser.parsebytes(raw_message.encode("utf-8"))
                    default = self.alias.get_default(list(receipients)[0])
                    adressee = set()
                    confirmed = set()
                    todefault = False
                    for address in receipients:
                        adressee.add(self.alias.get_alias(address))
                    for i in adressee:
                        if (self.outhandler.deliver(parsed_message, i)):
                            confirmed.add(i)
                        else:
                            todefault = True
                    if todefault and default not in confirmed:
                        self.outhandler.deliver(parsed_message, default)
                        confirmed.add(default)
                    if len(confirmed) > 0:
                        self.inhandler.delete(mail)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--aliasFile",
                        action="store",
                        default=(os.environ["HOME"] + "/.cloudmra/alias.json"),
                        help="Filesystem path to alias json file.")
    parser.add_argument("-c",
                        "--configFile",
                        action="store",
                        default=(os.environ["HOME"] + "/.cloudmra/cloudmra.config"),
                        help="Filesystem path to config json file.")
    parser.add_argument("-S",
                        "--systemd",
                        action="store_true",
                        help="Run as a systemd service.")  # store_true is false by default, and returns True when flag is set.
    arguments = parser.parse_args()

    with open(arguments.aliasFile, 'r') as aliasjson:
        ALIAS = (aliasjson.read())

    with open(arguments.configFile, 'r') as configjson:
        CONFIG = json.loads(configjson.read())

    main_overseer = overseer(CONFIG, ALIAS, LOOP=arguments.systemd)
    signal.signal(signalnum=signal.SIGTERM, handler=main_overseer.signal_handler)
    signal.signal(signalnum=signal.SIGINT, handler=main_overseer.signal_handler)

    if not main_overseer.CONTINUE:
        main_overseer.process()
    else:
        while main_overseer.CONTINUE:
            main_overseer.process()
            if signal.sigtimedwait(set([signal.SIGTERM, signal.SIGINT]), main_overseer.SLEEP_TIME):
                main_overseer.signal_handler(signal.SIGTERM)
    return 0


if __name__ == '__main__':
    sys.exit(main())
