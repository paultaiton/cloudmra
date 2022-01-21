'''
@author: paul
'''
import os
import boto3
import json
import uuid
# import logging


class cloudhandler():
    '''
    classdocs
    '''

    def __init__(self, queue_name, expire_bucket=None):
        '''
            Constructor method takes a string argument of queue_name to represent the name of the
            AWS SQS queue that will hold the messages from SES when a new email is received.
        '''
        self.sqs = boto3.resource('sqs')
        self.s3 = boto3.resource('s3')
        if expire_bucket is not None:
            self.expire_bucket = self.s3.Bucket(expire_bucket)
        else:
            self.expire_bucket = None
        self.filename = '/tmp/' + str(uuid.uuid4().hex)
        # self.buckets = dict()    # empty dict that will be used to hold a resource for each unique bucket.
        try:
            self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        except boto3.client('sqs').exceptions.QueueDoesNotExist:
            print("The queue '" + queue_name + "' does not exist.")
            exit(2)

    def fetch(self):
        returnlist = list()
        messages = self.queue.receive_messages(WaitTimeSeconds=3, MaxNumberOfMessages=10)
        for message in messages:
            payload = json.loads(json.loads(message.body).get("Message"))
            receipients = json.loads(json.loads(message.body).get("Message")).get("receipt").get("recipients")
            bucket_name = payload.get("receipt").get("action").get("bucketName")
            object_key = payload.get("receipt").get("action").get("objectKey")
            s3obj = self.s3.Object(bucket_name, object_key)
            os.umask(0o077)
            s3obj.download_file(self.filename)
            with open(self.filename, 'r') as tempfile:
                email = tempfile.read()
            os.remove(self.filename)
            returnlist.append((  # The odd format is to keep this modular.
                (email, set(receipients)),  # The tuple (email, set(receipients)) is used by main.
                message, s3obj))  # message is included as a return handle to be used in a later call to delete()

        if len(returnlist) > 0:
            return returnlist
        else:
            return False

    def delete(self, handle):
        handle[1].delete()
        self.expire_bucket.copy({'Bucket': handle[2].bucket_name, 'Key': handle[2].key}, handle[2].key)
        handle[2].delete()


if __name__ == "__main__":
    print("ERROR: This module should not be called directly.")
    exit(1)
