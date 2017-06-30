# -*- coding: utf-8 -*-
import logging
import commands
import os
import platform


log = logging.getLogger(__name__)


class BaseService(object):
    """docstring for BaseService."""
    def __init__(self, ServiceName):
        super(BaseService, self).__init__()
        self.set_system_variable()
        self.ServiceName = ServiceName
        self.ServicePath = os.path.join(self.service_dir, '{service}.{suffix}'.format(service=Self.ServiceName,
                                                                                      suffix=self.service_suffix))

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
        '''执行命令'''
        cmd = "{command} {action} {service}".format(command=self.service_command,
                                                    action=action,
                                                    service=self.service)
        return commands.getstatusoutput(cmd)

    def is_exists_service(self):
        return os.path.exists(self.ServicePath)

    def create_service(self, service_connext):
        if is_exists_service:
            raise IOError('service file already exists: %s' %(self.ServiceName))

        with open(self.ServicePath, 'w') as f:
            f.write(service_connext)
        return True

    def remove_service(self):
        if is_exists_service:
            os.remove(self.ServicePath)
        else:
            raise IOError('service file not exists: %s' % (self.ServiceName))