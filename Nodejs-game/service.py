from jinja2 import Environment, FileSystemLoader
import logging
#import log
import commands
import re
import sys
import os

def setup_console_logger():
    logging.root.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)-8s] %(message)s', datefmt='%H:%M:%S'
    )
    StreamHandler = logging.StreamHandler()
    StreamHandler.setFormatter(formatter)
    StreamHandler.setLevel(logging.DEBUG)
    logging.root.addHandler(StreamHandler)

setup_console_logger()

local_log = logging.getLogger(__name__)

def loader_template(name, searchpath='templates', *args, **kwargs):
    env = Environment(loader=FileSystemLoader(searchpath))
    __template = env.get_template(name)
    __str = __template.render(*args, **kwargs)
    return __str

class BaseService:
    def __init__(self, service_name, service_directory="/etc/systemd/system"):
        re_str = "(?P<appname>\w+)-(?P<gametype>\w+)-\w+-(?P<tableid>\d+).*"
        m = re.match(re_str, service_name).groupdict()
        self.service_name = service_name
        self.appname = m['appname']
        self.tableid = m['tableid']
        self.gametype = m['gametype']
        self.service_directory = service_directory

    def start(self):
        cmd = "systemctl start %s" % self.service_name
        if self.check_service():
            status,rev = commands.getstatusoutput(cmd)
            if status == 0:
                return True
            else:
                local_log.error('Execute %s receive error info (%s)' %(cmd, rev))
                return False
        else:
            self.add_service(start=True)

    def stop(self):
        cmd = "systemctl stop %s" % self.service_name
        if self.check_service():
            status, rev = commands.getstatusoutput(cmd)
            self.remove_service()

    def enable(self):
        cmd = "systemctl enable %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)

    def disable(self):
        cmd = "systemctl disable %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)

    def check_service(self):
        servicefile = os.path.join(self.service_directory, self.service_name)
        return os.path.exists(servicefile)

    def add_service(self, start=False):
        servicefile = os.path.join(self.service_directory, self.service_name)
        service = {'project': self.appname,
                   'tableid': self.tableid,
                   'gametype': self.gametype
                   }
        service_connext = loader_template(name='p2p-templates.service', searchpath='templates', service=service)
        with open(servicefile, 'w') as f:
            f.write(service_connext)
        self.enable()
        if start == True:
            self.start()

    def remove_service(self):
        self.disable()
        servicefile = os.path.join(self.service_directory, self.service_name)
        if os.path.exists(servicefile):
            os.remove(servicefile)
        return True


def man():
    argv = sys.argv[0:]
    active = sys.argv[1]
    active_list = ['start', 'stop']
    if active not in active_list:
        sys.exit(244)
    service = BaseService(argv[2])
    if active == 'start':
        service.start()
    elif active == 'stop':
        service.stop()

if __name__ == '__main__':
    man()