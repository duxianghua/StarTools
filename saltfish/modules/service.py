# -*- coding: utf-8 -*-
# Import Sys lib
import os
import commands
from jinja2 import Environment, FileSystemLoader

# Import saltfish lib
from saltfish.utils.exceptions import ServiceError

def render(template, template_dir, *args, **kwargs):
    env = Environment(loader=FileSystemLoader(template_dir))
    t = env.get_template(template)
    connext = t.render(*args, **kwargs)
    return connext

def write(connext, file, cover=False):
    if not cover:
        if os.path.exists(file):
            msg = 'file already exists for %s.' % file
            raise ServiceError(msg)

    with open(file, 'w') as f:
        f.write(connext)
    return True

#def create(*args, **kwargs):



def remove(file):
    os.remove(file)


def which(cmd):
    status, rev = commands.getstatusoutput('which %s' %cmd)
    return not status

def get_options():
    config = {}
    if which('systemctl'):
        config['service_suffix'] = 'service'
        config['service_dir'] = '/etc/systemd/system'
    else:
        config['service_suffix'] = 'conf'
        config['service_dir'] = '/etc/init/'
    return config

def run(name, action):
    ret = []
    if which('systemctl'):
        ret.append('systemctl')
    else:
        ret.append('initctl')
    ret.extend(action)
    ret.extend(name)
    return commands.getstatusoutput(' '.join(ret))

def start(name):
    run(name, 'start')

def stop(name):
    run(name, 'stop')

def get_all():
    pass