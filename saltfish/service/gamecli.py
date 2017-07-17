# -*- coding: utf-8 -*-
import re
import logging
import sys

from saltfish.utils.parsers import OptionParser
from saltfish.service.Nodejs import *
from saltfish.modules import service
from saltfish.log.setup import setup_logger

log = logging.getLogger(__name__)
class GameOptionPares(OptionParser):
    choices_list = ['start', 'stop', 'restart', 'reload', 'kill', 'status', 'create']
    def _set_arguments(self):
        self.add_argument('action', choices=self.choices_list, metavar='ACTION', help=str(self.choices_list))
        self.add_argument('name', help='Service Name', metavar='ServiceName')
        self.add_argument('--signal', help='Which signal to send')
        self.add_argument('--cover', action='store_true', help='当服务存在时是否覆盖')

class GameCLI(GameOptionPares):
    def run(self):
        self.parse_args('start BIGTWO-P2P-TABLE-12.service'.split())
        self.analyze_service_name()
        self.config['file'] = os.path.join(BASE_DIR, 'config/staging/service.conf')
        self.config['env'] = 'staging'
        if self.config['action'] == 'start':
            self.start()
        elif self.config['action'] == 'stop':
            self.stop()
        elif self.config['action'] == 'kill':
            self.kill()
        else:
            self.other()

    def analyze_service_name(self):
        re_str = "(?P<appname>\w+)-(?P<project>\w+)-TABLE-(?P<tableid>\d+).*"
        name = self.config['name'].split('.')[0].upper()
        try:
            s = re.match(re_str, name).groupdict()
            self.config['appname'] = s['appname']
            self.config['project'] = s['project']
            self.config['startid'] = int(s['tableid'])
            self.config['endid'] = int(s['tableid'])
        except AttributeError as e:
            log.error('service name can not match: %s, Name rule [%s]' % (service, re_str))
            sys.exit(245)
        return s
    def write_log(self, status, msg):
        if not status:
            log.info(msg)
            sys.exit(status)
        else:
            log.error(msg)
            sys.exit(status)
    def create(self):
        nodejs(**self.config)

    def start(self):
        if not os.path.exists(self.config['file']):
            self.create()
        print self.config['name']
        service.run(self.config['name'], 'enable')
        retcode,rev = service.start(self.config['name'])
        self.write_log(retcode, rev)

    def stop(self):
        service.run(self.config['name'], 'disable')
        retcode, rev = service.stop(self.config['name'])
        self.write_log(retcode, rev)

    def kill(self):
        cmd = 'kill --signal=%s' %self.config['signal']
        service.run(self.config['name'], 'disable')
        retcode, rev = service.run(self.config['name'], cmd)
        self.write_log(retcode, rev)

    def other(self):
        retcode,rev = service.run(self.config['name'], self.config['action'])
        self.write_log(retcode, rev)

