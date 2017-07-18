import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['CODE_DIR'] = BASE_DIR

from saltfish.service.Nodejs import ServiceOptionPares, taskmq

class CreateService(ServiceOptionPares):
    def run(self):
        #self.parse_args('--project taskmq-manager  --appname bigtwo --env staging'.split())
        self.parse_args()
        if not self.config['file']:
            self.config['file'] = os.path.join(os.environ['CODE_DIR'], 'config/%s/service.conf' %self.config['env'])
        s = taskmq(**self.config)



if __name__ == '__main__':
    c=CreateService()
    c.run()