# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re
import os
import sys
import time

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(BASE_DIR)

from saltfish.service.core import BaseService
from saltfish.log import console_handler, file_handler
from saltfish.utils.Trender import render

log = logging.getLogger(__name__)
log.setLevel('DEBUG')
log.addHandler(console_handler())
log.addHandler(file_handler('/var/log/nodejs-service.log'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


ServiceConfig = {
    'TemplateName' : 'p2p-template.service',
    'TemplatePath' : os.path.join(BASE_DIR, 'templates')

}

class NodejsService(BaseService):
    def __init__(self, service):
        self.SName, self.SArgs = self.fromat_service(service)
        super(NodejsService, self).__init__(self.SName)

    def fromat_service(self, service):
        RE_STR = "(?P<AppName>\w+)-(?P<GameType>\w+)-TABLE-(?P<TableID>\d+).*"
        try:
            _serviceArgs = re.match(RE_STR, service).groupdict()
            _ServiceName = service.split('.')[0]
        except AttributeError as e:
            raise AttributeError('service name can not match: %s \n %s' %(service, RE_STR))
        return _ServiceName.upper(),_serviceArgs

    def disable(self):
            status,rev = self.run('disable')
            log.debug(rev)

    def enable(self):
        status,rev = self.run('enable')
        log.debug(rev)

    def __create_service(self):
        service_connext = render(ServiceConfig['TemplateName'], ServiceConfig['TemplatePath'], **self.SArgs)
        self.create_service(service_connext)

    def start(self):
        if self.is_exists_service():
            status, rev = self.run('start')
            if status == '0':
                self.enable()
                print 'asdf'
            if rev:
                log.info(rev)
            sys.exit(status)
        else:
            self.__create_service()
            self.start()

    def stop(self):
        if self.is_exists_service():
            status, rev = self.run('stop')
            if rev:
                log.debug(rev)
            self.disable()
            sys.exit(status)
        else:
            log.error('service not exists: %s' % self.ServiceName)

    def kill(self, signal):
        action = "kill --signal=%s" %signal
        status, rev = self.run(action)
        if rev:
            log.debug(rev)
        self.disable()
        sys.exit(status)

    def other(self, action):
        status, rev = self.run(action)
        log.info(rev)
        sys.exit(status)

def p2p_service(*args, **kwargs):
        log.error('asdfasdf')
        action = kwargs['action']
        signal = kwargs['signal']
        service = kwargs['service']
        service = NodejsService(service)
        if action == 'start':
            service.start()
        elif action == 'stop':
            service.stop()
        elif action == 'kill':
            service.kill(signal=signal)
        else:
            service.other(action=action)

def __man__():
    import argparse
    parser = argparse.ArgumentParser(description='Test Process.')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'reload', 'kill', 'status'])
    parser.add_argument('service')
    parser.add_argument('--signal', metavar='signal')
    args = parser.parse_args()
    p2p_service(**args.__dict__)

if __name__ == '__main__':
    __man__()