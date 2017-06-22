from jinja2 import Environment, FileSystemLoader
import logging
import commands
import re
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)



log = logging.getLogger(__name__)

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
                log.debug("status code:[%s],info:%s" %(status,rev))
                return True
            else:
                log.error('Execute %s receive error info (%s)' %(cmd, rev))
                return False
        else:
            return self.create_service(start=True)

    def stop(self):
        cmd = "systemctl stop %s" % self.service_name
        if self.check_service():
            status, rev = commands.getstatusoutput(cmd)
            self.remove_service()
            return True

    def enable(self):
        cmd = "systemctl enable %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)
        log.debug(rev)

    def disable(self):
        cmd = "systemctl disable %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)
        log.debug(rev)

    def restart(self):
        cmd = "systemctl restart %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)
        if status == '0':
            return True
        else:
            return False
            log.error(rev)

    def reload(self):
        cmd = "systemctl reload %s" % self.service_name
        status, rev = commands.getstatusoutput(cmd)
        log.debug(rev)
        if status == '0':
            return True
        else:
            return False
            log.error(rev)

    def check_service(self):
        servicefile = os.path.join(self.service_directory, self.service_name)
        return os.path.exists(servicefile)

    def create_service(self, start=False):
        TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        servicefile = os.path.join(self.service_directory, self.service_name)
        service = {'project': self.appname, 'tableid': self.tableid, 'gametype': self.gametype}
        service_connext = loader_template(name='p2p-template.service', searchpath=TEMPLATE_DIR, service=service)
        with open(servicefile, 'w') as f:
            f.write(service_connext)
        self.enable()
        if start == True:
            return self.start()
        else:
            log.debug('not start service')

    def remove_service(self):
        self.disable()
        servicefile = os.path.join(self.service_directory, self.service_name)
        if os.path.exists(servicefile):
            os.remove(servicefile)
        return True


def man():
    argv = sys.argv[0:]
    if len(argv) <= 2:
        sys.exit(244)
    active = sys.argv[1]
    active_list = ['start', 'stop', 'restart', 'reload']
    service_name = argv[2]
    if active not in active_list:
        log.error('Unknow command: %s' % active)
        sys.exit(244)
    service = BaseService(service_name)
    if active == 'start':
        if service.start() == True:
            log.info('Start service %s done' % service_name)
            sys.exit(0)
        else:
            log.info('Start service %s error' % service_name)
            sys.exit(1)
    elif active == 'stop':
        if service.stop() == True:
            log.info('Stop service %s done' % service_name)
            sys.exit(0)
        else:
            log.info('Stop service %s error' % service_name)
            sys.exit(1)
    elif active == 'restart':
        if service.stop() == True:
            log.info('Restart service %s done' % service_name)
            sys.exit(0)
        else:
            log.info('Restart service %s error' % service_name)
            sys.exit(1)
    elif active == 'reload':
        if service.stop() == True:
            log.info('Reload service %s done' % service_name)
            sys.exit(0)
        else:
            log.info('Reload service %s error' % service_name)
            sys.exit(1)

if __name__ == '__main__':
    from log import setup_console_logger
    setup_console_logger()
    man()