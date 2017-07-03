# -*- coding: utf-8 -*-

# Import python libs
import logging
import commands
import os
from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)

# Import SaltFish libs
from saltfish.utils.exceptions import ServiceError

class BaseService(object):
    """docstring for BaseService."""
    def __init__(self, service_name, *args, **kwargs):
        self.service_dir = kwargs['service_dir']
        self.service_cmd = kwargs['service_cmd']
        self.service_suffix = kwargs['service_suffix']
        self.service_name = service_name
        self.service_file = '{service_name}.{service_suffix}'.format(self.service_name, self.service_suffix)
        self.service_file_path = os.path.join(self.service_dir, self.service_file)

    def run(self, action):
        '''执行命令'''
        cmd = "{command} {action} {service}".format(command=self.service_cmd, action=action,
                                                    service=self.service_name)
        return commands.getstatusoutput(cmd)

    def is_exists_service(self):
        return os.path.exists(self.service_file_path)

    def render(self, template_dir, template, *args, **kwargs):
        env = Environment(loader=FileSystemLoader(template_dir))
        t = env.get_template(template)
        connext = t.render(*args, **kwargs)
        return connext

    def create_service(self, connext, cover=False):
        if cover:
            if self.is_exists_service():
                msg = 'service file already exists for %s.' %self.service_file_path
                raise ServiceError(msg)

        with open(self.service_file_path, 'w') as f:
            f.write(connext)
        return True

    def remove_service(self):
        if self.is_exists_service():
            os.remove(self.service_file_path)
            return True
        else:
            msg = 'service file not exists: %s' %(self.service_file_path)
            raise ServiceError(msg)