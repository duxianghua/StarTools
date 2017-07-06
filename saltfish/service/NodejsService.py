# -*- coding: utf-8 -*-
import re
import sys
import logging

from saltfish.service.BaseService import Service
from saltfish.utils.parsers import OptionParser


log = logging.getLogger('__name__')

class GameOptionPares(OptionParser):
    choices_list = ['start', 'stop', 'restart', 'reload', 'kill', 'status', 'create']
    def _set_arguments(self):
        self.add_argument('action', choices=self.choices_list, metavar='action', help=str(self.choices_list))
        self.add_argument('service', help='Service Name')
        self.add_argument('--signal', help='Which signal to send')
        self.add_argument('--cover', action='store_true', help='当服务存在时是否覆盖')


def analyze_service_name(service):
    re_str = "(?P<AppName>\w+)-(?P<GameType>\w+)-TABLE-(?P<TableID>\d+).*"
    name = service.split('.')[0].upper()
    try:
        s = re.match(re_str, name).groupdict()
    except AttributeError as e:
        raise AttributeError('service name can not match: %s \n %s' % (service, re_str))
    return s

def write_log(status=0, msg=None):
    if status == 0:
        log.debug(msg)
    else:
        log.error(msg)
    sys.exit(status)

def GameServiceCLI(*args, **kwargs):
    cli_parameter = kwargs
    print kwargs
    service_args = analyze_service_name(cli_parameter['service'])
    s = Service(service_args['GameType'],**service_args)
    if cli_parameter['action'] in ['start', 'stop', 'restart', 'reload', 'status']:
        status, rev = s._exec(cli_parameter['action'])
        write_log(status, rev)
    elif cli_parameter['action'] == 'kill':
        action = '{action} --signal={signal}'.format(action=cli_parameter['action'],
                                                     signal=cli_parameter['signal'])
        status, rev = s._exec(action)
        write_log(status, rev)
    elif cli_parameter['action'] == 'create':
        connext = s.render(service_args)
        if s.create(connext,cover=cli_parameter['cover']):
            status = 0
            msg = 'create service [%s] success.'