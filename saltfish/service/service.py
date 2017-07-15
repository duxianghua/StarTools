# -*- coding: utf-8 -*-

''' Import Sys lib '''
from __future__ import absolute_import
import os
import ConfigParser
from jinja2 import Environment, FileSystemLoader
import commands

from saltfish.utils.exceptions import ServiceError


def Get_ConfigParser(file):
    if os.path.exists(file):
        c = ConfigParser.SafeConfigParser()
        c.read(file)
        return c
    msg = "No such file or directory: '%s'" % file
    raise ServiceError(msg)

class BaseService(object):
    def __init__(self,
                 SERVICE_DIR,
                 SERVICE_CMD,
                 SERVICE_SUFFIX,
                 SERVICE_TEMP = None,
                 SERVICE_TEMP_DIR = None,
                 *args, **kwargs):
        '''
        :param SERVICE_DIR:
        :param SERVICE_CMD:
        :param SERVICE_SUFFIX:
        :param SERVICE_TEMP:
        :param SERVICE_TEMP_DIR:
        :param args:
        :param kwargs:
        '''
        self.SERVICE_DIR = SERVICE_DIR
        self.SERVICE_CMD = SERVICE_CMD
        self.SERVICE_SUFFIX = SERVICE_SUFFIX
        self.SERVICE_TEMP = SERVICE_TEMP
        self.SERVICE_TEMP_DIR = SERVICE_TEMP_DIR
        super(BaseService, self).__init__()

    def get_service_path(self, service):
        path = os.path.join(self.SERVICE_DIR, '{Name}.{Suffix}'.format(Name=service, Suffix=self.SERVICE_SUFFIX))
        return path

    def exists(self, service):
        '''
        检查服务配置文件是否存在
        :return: True or False
        '''
        ServiceFile = self.get_service_path(service)
        return os.path.exists(ServiceFile)

    def render(self, *args, **kwargs):
        if not self.SERVICE_TEMP_DIR or self.SERVICE_TEMP:
            msg = 'Not define template dir or template name.'
            raise ServiceError(msg)
        env = Environment(loader=FileSystemLoader(self.SERVICE_TEMP_DIR))
        t = env.get_template(self.SERVICE_TEMP)
        connext = t.render(*args, **kwargs)
        return connext

    def create(self, service, connext, cover=False):
        ServiceFile = self.get_service_path(service)
        if self.exists() and cover == False:
            msg = 'service file already exists for %s.' % ServiceFile
            raise ServiceError(msg)
        try:
            with open(ServiceFile, 'w') as f:
                f.write(connext)
            return True
        except Exception as e:
            raise ServiceError(e)

    def remove(self, service):
        ServiceFile = self.get_service_path(service)
        if self.exists():
            os.remove(ServiceFile)
        else:
            msg = 'No such file: %s' %(ServiceFile)
            raise ServiceError(msg)

    def _exec(self, action, service):
        '''执行命令'''
        cmd = "{command} {action} {service}".format(command=self.config['SERVICE_CMD'],
                                                    action=action,
                                                    service=service)
        return commands.getstatusoutput(cmd)

def

def render():
    pass

def create():
    pass

def remove():
    pass

def run():
    pass