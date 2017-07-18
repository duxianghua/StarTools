# -*- coding: utf-8 -*-
import ConfigParser
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from saltfish.utils.parsers import OptionParser
from saltfish.modules import service
from saltfish.utils.exceptions import ServiceError

class ServiceOptionPares(OptionParser):
    description = 'Create Nodejs Service'
    optionals_title = ''
    def _set_arguments(self):
        self.description = '%s --project p2p  --appname bigtwo --startid 10 --endid 10 --interval 2' % self.prog

        self.add_argument('--project', metavar='ProjectName', action='store', required=True)
        self.add_argument('--appname', metavar='AppName')
        self.add_argument('--env', metavar='Environment', choices=['staging', 'production'],  required=True)
        self.add_argument('--startid', metavar='Number', type=int, default=0, help='specify service ID,default is 0')
        self.add_argument('--endid', metavar='Number', type=int, default=0, help='specify service ID,default is 0')
        self.add_argument('--interval', metavar='Number', type=int, default=1, help='specify service ID interval,default is 1')
        self.add_argument('-f', '--file', help='Specify the configuration file')
        self.add_argument('--cover', action='store_true', help='Whether it is covered')


class CreateService(object):
    options = {
        'template': None,
        'template_dir': None,
        'name_rule': None,
        'service_dir': None,
        'suffix': None
    }
    def __init__(self, project, appname, file, startid=0, endid=0, interval=1, cover=False, *args, **kwargs):
        if isinstance(project, str):
            project = project.upper()
        else:
            raise ServiceError('The project name is [None]')

        if isinstance(appname, str):
            appname = appname.upper()
        else:
            raise ServiceError('The app name is not a string type')

        self.set_options(project, file)

        id_list = [int(startid), int(endid) + 1, int(interval)]

        self.options['ProjectName'] = project
        self.options['AppName'] = appname
        self.options['id_list'] = id_list
        self.options['cover'] = cover
        self.options['env'] = kwargs['env']
        self.options['template_dir'] = os.path.join(BASE_DIR, self.options['template_dir'])
        super(CreateService, self).__init__()

    def set_options(self, section, file=None):
        #if not file:
        #   file = os.path.join(BASE_DIR, 'saltfish/config/staging/service.conf')
        c = ConfigParser.ConfigParser()
        l = c.read(file)
        #os.path.isfile('saltfish/config/service.conf')
        if c.has_section(section):
            for i in c.options(section):
                self.options[i] = c.get(section, i)
        else:
            msg = '在配置文件中没有找到项目[%s]' % section
            raise ServiceError(msg)

    def generate_name(self, **kwargs):
        try:
            name = self.options['name_rule'].format(**kwargs)
            return name
        except KeyError as e:
            raise ServiceError('name rule: "%s". return error: %s' %(self.options['name_rule'], e.message))

    def generate_args(self):
        _kwargs = {}
        if self.options['id_list'] != [0, 1, 1]:
            for i in range(*self.options['id_list']):
                _kwargs['name'] = self.generate_name(ID=i, **self.options)
                _kwargs['ID'] = i
                _kwargs['file'] = os.path.join(self.options['service_dir'], _kwargs['name'] + '.' + self.options['suffix'])
                yield dict(_kwargs, **self.options)
        else:
            _kwargs['name'] = self.generate_name(**self.options)
            _kwargs['file'] = os.path.join(self.options['service_dir'], _kwargs['name'] + '.' + self.options['suffix'])
            yield dict(_kwargs, **self.options)


    def run(self):
        for i in self.generate_args():
            connext = service.render(**i) + '\n'
            try:
                service.write(connext=connext, **i)
                sys.stdout.write('service "%s" create success.\n' %i['name'])
            except ServiceError as e:
                sys.stderr.write(e.message + '\n')



class TaskMQ(CreateService):
    options = {
        'template': None,
        'template_dir': None,
        'name_rule': None,
        'service_dir': None,
        'suffix': None,
        'project_path': None
    }
    def generate_args(self):
        s_list_file = os.path.join()


def nodejs(*args, **kwargs):
    try:
        s = CreateService(*args, **kwargs)
        s.run()
    except ServiceError as e:
        sys.stderr.write(e.message + '\n')

#a=ServiceOptionPares()
#'--project p2p  --appname bigtwo --startid 10 --endid 10'.split()
#a.parse_args()
#nodejs(**a.config)