# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from saltfish.service.core import BaseService

log = logging.getLogger(__name__)
log.setLevel('DEBUG')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


def format_service_name(service):
    RE_STR = "(?P<AppName>\w+)-(?P<GameType>\w+)-TABLE-(?P<TableID>\d+).*"
    p = re.match(RE_STR, service).groupdict()
    s = service.split('.')[0]
    return s,p

class NodejsService(BaseService):
    def check(self, parameter):
        status, rev = self.run('show')
        l = rev.split('\n')
        d = {}
        for i in l:
            stl = i.split('=', 1)
            d[stl[0]] = stl[1]
        return d[parameter]

    def stop(self):
        self.service.run('stop')
        if self.check('ActiveState') != 'active':
            self.remove_service()
            if self.check('LoadState') != 'loaded':
                log.debug('DELETE SERVICE FILE: %s Done' %self.service)
                sys.exit(0)
            else:
                log.error('DELETE SERVICE FILE: %s Failure' %self.service)
                sys.exit(101)
        else:
            log.error('STOPING SERVICE: %s Failuer')
            sys.exit(102)

    def start(self):
        if self.check('LoadState') != 'loaded':
            if self.create_service(TEMPLATE_DIR, 'p2p-template.service'):
                log.debug('Create service: %s Done' %self.service)
            else:
                log.error('Create service: %s Failure' %self.service)
                sys.exit(103)
        self.run('start')
        time.sleep(2)
        if self.check('ActiveState') == 'active':
            log.debug('Start service: %s Done' % self.service)
            sys.exit(0)
        else:
            log.error('Start service: %s Failure' % self.service)
            sys.exit(104)

    def kill(self, signal):
        action = "kill --signal=%s" %signal
        self.run(action)
        log.debug('EXEC Command: %s %s' %(action, self.service))
        time.sleep(1)
        self.stop()

    def other(self, action):
        status, rev = self.run(action)
        log.info(rev)
        sys.exit(status)

def p2p_service(*args, **kwargs):
        action = kwargs['action']
        signal = kwargs['signal']
        service = kwargs['service']
        SName, Sparameter = format_service_name(service)
        service = NodejsService(SName, **Sparameter)
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
    from saltfish.log import setup_console_logger
    setup_console_logger()
    __man__()