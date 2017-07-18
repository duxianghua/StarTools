import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['CODE_DIR'] = BASE_DIR

from saltfish.service.Nodejs import ServiceOptionPares, nodejs

class CreateService(ServiceOptionPares):
    def run(self):
        #self.parse_args('--project p2p  --appname bigtwo --startid 10 --endid 10 --env staging'.split())
        self.parse_args()
        if not self.config['file']:
            self.config['file'] = os.path.join(os.environ['CODE_DIR'], 'config/%s/service.conf' %self.config['env'])
        s = nodejs(**self.config)



if __name__ == '__main__':
    c=CreateService()
    c.run()