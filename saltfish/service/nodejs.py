# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re
import os
import sys
import ConfigParser

from saltfish.service.core import BaseService
from saltfish.log import console_handler, file_handler
from saltfish.utils.Trender import render

log = logging.getLogger(__name__)
log.setLevel('DEBUG')
log.addHandler(console_handler())
log.addHandler(file_handler('/var/log/nodejs-service.log'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NodejsService(BaseService):
    config = {'service_dir':'/usr/lib/systemd/system',
              'service_cmd':'systemctl',
              'service_suffix':'service',
              'template':'p2p-template.service',
              'template_dir': os.path.join(BASE_DIR, 'templates')
              }
    def __init__(self, AppName=None,
                 GameType=None,
                 TableID=None):
        self.AppName = AppName
        self.GameType = GameType
        self.TableID = TableID
        self.set_config()
        self.service_name = '{GameType}-{AppName}-{TableID}'.format(GameType=self.GameType,
                                                                    AppName=self.AppName,
                                                                    TableID=self.TableID)
        super(NodejsService, self).__init__(self.service_name, **self.config)

    def create(self, template, template_dir, *args, **kwargs):
        connext = self.render(template_dir, template, *args, **kwargs)
        self.create_service(connext)

    def set_config(self):
        c = self.configparser()
        for keyname in self.config.keys():
            try:
                values = c.get(self.AppName, keyname)
                self.config[keyname] = values
            except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
                pass

    def configparser(self, file=None):
        if not file:
            file = '../config/nodejs_service.conf'

        c = ConfigParser.SafeConfigParser()
        c.read(file)
        return c


def fromat_service(service):
        re_str = "(?P<AppName>\w+)-(?P<GameType>\w+)-TABLE-(?P<TableID>\d+).*"
        name = service.split('.')[0].upper()
        try:
            s = re.match(re_str, name).groupdict()
        except AttributeError as e:
            raise AttributeError('service name can not match: %s \n %s' %(service, re_str))
        return s

def p2p_service(*args, **kwargs):
        action = kwargs['action']
        signal = kwargs['signal']
        service = kwargs['service']
        s = fromat_service(service)
        service = NodejsService(AppName=s['AppName'], GameType=s['GameType'], TableID=s['TableID'])
        if action == 'start':
            status,rev = service.run('is-active')
            if rev == 'unknown':
                service.create_service(s)
            status,rev = service.run('start')
            log.info(rev)
            status, rev = service.run('disable')
            log.info(rev)
            sys.exit(status)
        elif action == 'stop':
            status,rev = service.run('stop')
            log.info(rev)
            status, rev = service.run('disable')
            log.info(rev)
            sys.exit(status)
        elif action == 'kill':
            action = '{action} --signal={signal}'.format(action=action, signal=signal)
            status, rev = service.run(action)
            log.info(rev)
            status, rev = service.run('disable')
            sys.exit(status)
        else:
            status, rev = service.run(action)
            log.info(rev)
            sys.exit(status)
