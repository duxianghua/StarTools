from __future__ import absolute_import
import sys
import os
from saltfish.service.core import BaseService
import logging
import re


log = logging.getLogger(__name__)
log.setLevel('DEBUG')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
RE_STR = "(?P<APP>\w+)-(?P<GameType>\w+)-\w+-(?P<TableID>\d+).*"


def nodejs_service(*args, **kwargs):
        action = kwargs['action']
        signal = kwargs['signal']
        service = kwargs['service']
        service_kwargs = re.match(RE_STR, service).groupdict()
        service = BaseService(service, **service_kwargs)
        if action == 'stop':
            service.run('stop')
            service.remove_service()
        elif action == 'kill' and signal:
            action_args = "kill --signal=%s" %signal
            service.run(action_args)
            service.remove_service()
        elif action == 'start':
            if service.service_exists() == False:
                service.create_service(TEMPLATE_DIR, 'p2p-template.service')
            service.run('start')
        elif action in ['restart', 'reload', 'status']:
            if service.service_exists():
                status, rev = service.run(action)
                log.info(rev)


def __man__():
    import argparse
    parser = argparse.ArgumentParser(description='Test Process.')
    parser.add_argument('action', choices=['start',
                                           'stop',
                                           'restart',
                                           'reload',
                                           'kill',
                                           'status'])
    parser.add_argument('service')
    parser.add_argument('--signal', metavar='signal')
    args = parser.parse_args()
    nodejs_service(**args.__dict__)

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)
    from saltfish.log import setup_console_logger
    setup_console_logger()
    __man__()