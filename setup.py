'''
Created on Oct 12, 2019

@author: paul
'''

from setuptools import setup

setup(name='cloudmra',
      version='0.1.0',
      packages=['cloudmra'],
      install_requires=['boto3'],
      entry_points={'console_scripts': [
                        'cloudmra = cloudmra.__main__:main'
                    ]
                    },

      author="Paul Aiton",
      author_email="paul@aiton.info",
      description="Mail Retrieval agent for connecting a cloud provider to an on premise mail hosting server.\
      As of this version, only AWS is supported as input, and only LMTP is supported for delivery. \
      Contact me or make a request on github if you would like a different cloud provider or delivery mechanism"
      )
