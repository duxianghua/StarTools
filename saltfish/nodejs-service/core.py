from jinja2 import Environment, FileSystemLoader
import logging
import commands
import os
import platform

log = logging.getLogger(__name__)

def loader_template(name, searchpath='templates', *args, **kwargs):
    env = Environment(loader=FileSystemLoader(searchpath))
    __template = env.get_template(name)
    __str = __template.render(*args, **kwargs)
    return __str

class BaseService:
    def __init__(self, service, re_str, *args, **kwargs):
        self.set_system_variable()
        if self.format_service_name(service, re_str) == False:
            raise NameError('Input Service Error: %s' %service)

    def set_system_variable(self):
        system_info = platform.platform().split('-')
        system_version = system_info[-2].split('.')[0]
        if int(system_version) <= 7:
            self.service_dir = '/etc/init'
            self.service_suffix = 'conf'
        else:
            self.service_dir = '/etc/systemd/system'
            self.service_suffix = 'service'

    def format_service_name(self, service, re_str):
        r = re.match(re_str, service.upper())
        if r:
            self.service_args = r.groupdict()
            self.service_name = service.upper().split('.')[0]
            self.FileName = "%s.%s" % (self.service_name, self.service_suffix)
            self.FileFullPath = os.path.join(self.service_dir, FileName)
            return True
        else:
            return False

    def run(self, active):
        cmd = "{command} {active} {service}".format(command=self.service, active=active, service=self.service_name)
        return commands.getstatusoutput(cmd)

    def check_service(self):
        FileName = "%s.%s" % (self.service_name, self.service_suffix)
        FileFullPath = os.path.join(self.service_dir, FileName)
        return os.path.exists(FileFullPath)

    def create_service(self, template_dir, template_name):
        FileName = "%s.%s" %(self.service_name, self.service_suffix)
        FileFullPath = os.path.join(self.service_dir, FileName)
        service = self.service_args
        service_connext = loader_template(name=template_name, searchpath=template_dir, service=service)
        with open(FileFullPath, 'w') as f:
            f.write(service_connext)

    def remove_service(self):
        if os.path.exists(self.FileFullPath):
            os.remove(self.FileFullPath)