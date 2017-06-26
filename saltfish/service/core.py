from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging
import commands
import os
import platform
import re

log = logging.getLogger(__name__)

def loader_template(name, searchpath='templates', *args, **kwargs):
    env = Environment(loader=FileSystemLoader(searchpath))
    __template = env.get_template(name)
    __str = __template.render(*args, **kwargs)
    return __str



class BaseService:
    def __init__(self, service, *args, **kwargs):
        self.set_system_variable()
        self.service = service
        self.service_file_name = "%(service).%(suffix)" % (service, self.service_suffix)
        self.service_args = kwargs
        self.service_file_abspath = os.path.join(self.service_dir, self.service_file_name)

    def set_system_variable(self):
        system_version = int(platform.dist()[1].split('.')[0])
        if int(system_version) < 7:
            self.service_dir = '/etc/init'
            self.service_suffix = 'conf'
            self.service_command = 'initctl'
        else:
            self.service_dir = '/etc/systemd/system'
            self.service_suffix = 'service'
            self.service_command = 'systemctl'

    def run(self, action):
        cmd = "{command} {action} {service}".format(command=self.service_command, action=action, service=self.service)
        return commands.getstatusoutput(cmd)

    def service_exists(self):
        return os.path.exists(self.service_file_abspath )

    def create_service(self, t_dir, t_name):
        if self.service_exists():
            _msg = 'Create service failure: %s exits.' %self.service
            raise IOError(msg)
        try:
            s_connext = loader_template(name=t_name, searchpath=t_dir, **self.service_args)
        except TemplateNotFound as e:
            log.error(e)
            log.error("Template Dir: %s" %template_dir)
            return False
        with open(self.service_file_abspath , 'w') as f:
            f.write(s_connext)
        return True

    def remove_service(self):
        if os.path.exists(self.service_file_abspath  ):
            os.remove(self.service_file_abspath )