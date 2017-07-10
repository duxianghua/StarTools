# -*- coding: utf-8 -*-

''' Import Sys lib '''
from __future__ import absolute_import
import os
import sys
import ConfigParser
from ConfigParser import NoSectionError, NoOptionError
from jinja2 import Environment, FileSystemLoader
import commands

from saltfish.utils.exceptions import ServiceError


class Service(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config = {'service_dir'     :   '/usr/lib/systemd/system',
              'service_cmd'     :   'systemctl',
              'service_suffix'  :   'service',
              'template'        :   'p2p-template.service',
              'name_rule'       :   None,
              'template_dir'    :   os.path.join(BASE_DIR, 'templates')
              }
    def __init__(self, ServiceType, ConfingFile=None, *args, **kwargs):
        print self.BASE_DIR
        self.set_config(ServiceType, ConfingFile)
        if self.config['name_rule']:
            try:
                self.config['service_name'] = self.config['name_rule'].format(*args, **kwargs)
                print "name:" + self.config['service_name']
            except KeyError as e:
                raise KeyError('Missing parameters: %s' %e)
        else:
            raise KeyError('config file not define: "name rule".')
        service_file_name = '{name}.{suffix}'.format(name=self.config['service_name'], suffix=self.config['service_suffix'])
        self.config['service_file'] = os.path.join(self.config['service_dir'], service_file_name)
        super(Service, self).__init__()

    def configparser(self, file=None):
        if not file:
            file = os.path.join(self.BASE_DIR, 'saltfish/config/nodejs_service.conf')
            print file
        c = ConfigParser.SafeConfigParser()
        c.read(file)
        return c

    def set_config(self, section, ConfingFile=None):
        c = self.configparser(ConfingFile)
        if section not in c.sections():
            print c.sections()
            raise ServiceError('未在配置文件中定义的服务类型[%s]' %section)
        for keyname in self.config.keys():
            try:
                values = c.get(section, keyname)
                self.config[keyname] = values
            except NoOptionError:
                pass

    def is_exists(self):
        return os.path.exists(self.config['service_file'])

    def render(self, *args, **kwargs):
        env = Environment(loader=FileSystemLoader(self.config['template_dir']))
        t = env.get_template(self.config['template'])
        connext = t.render(*args, **kwargs)
        return connext

    def create(self, connext, cover=False):
        if cover:
            if self.is_exists():
                msg = 'service file already exists for %s.' %self.config['service_file']
                raise ServiceError(msg)

        with open(self.config['service_file'], 'w') as f:
            f.write(connext)
        return True

    def remove(self):
        if self.is_exists():
            os.remove(self.config['service_file'])
        else:
            msg = 'No such file: %s' %(self.config['service_file'])
            raise OSError(msg)

    def _exec(self, action):
        '''执行命令'''
        cmd = "{command} {action} {service}".format(command=self.config['service_cmd'],
                                                    action=action,
                                                    service=self.config['service_name'])
        return commands.getstatusoutput(cmd)

if __name__ == '__main__':
    a = Service('p2p',AppName='bitwo', GameType='xxxx', TableID='12')
    print a.render()