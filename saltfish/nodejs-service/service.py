import sys
import os
from core import BaseService
import logging


log = logging.getLogger(__name__)

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
re_str = "(?P<APP>\w+)-(?P<GameType>\w+)-\w+-(?P<TableID>\d+).*"

def nodejs_service(*args, **kwargs):
        action = kwargs['action']
        signal = kwargs['signal']
        service = kwargs['service']
        service = BaseService(service, re_str)
        if action == 'stop':
            service.run('stop')
            service.remove_service()
        elif action == 'kill' and signal:
            action_args = "kill --signal=%s" %signal
            service.run(action_args)
            service.remove_service()
        elif action == 'start':
            if service.check_service() == False:
                service.create_service(template_dir, 'p2p-template.service')
            service.run('start')
        elif action in ['restart', 'reload', 'status']:
            if service.check_service():
                status, rev = service.run('restart')
                log.info(rev)


def __man__():
    import argparse
    parser = argparse.ArgumentParser(description='Test Process.')
    parser.add_argument('action', choices=['start',
                                           'stop',
                                           'restart',
                                           'reload',
                                           'kill'])
    parser.add_argument('service')
    parser.add_argument('--signal', metavar='signal')
    args = parser.parse_args()
    nodejs_service(**args.__dict__)

if __name__ == '__main__':
    __man__()