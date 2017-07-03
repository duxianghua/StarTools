# -*- coding: utf-8 -*-
'''
This module is a central location for all saltfish exceptions
'''

from __future__ import absolute_import

# Import python libs
import copy
import logging
import time

class SaltFishException(Exception):
    '''
    Base exception class; all SaltFish-specific exceptions should subclass this
    '''
    def __init__(self, message=''):
        super(SaltFishException, self).__init__(message)
        self.strerror = message

class ServiceError(SaltFishException):
    '''all service error'''