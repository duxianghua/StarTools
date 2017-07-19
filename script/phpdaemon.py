# coding: utf-8
#!/bin/env python
import sys
import json
import commands
import os
import re
import shutil
import argparse

parse = argparse.ArgumentParser()
parse.add_argument('appname', metavar='AppName')
parse.add_argument('serviceid', metavar='SERVER_ID')
args = parse.parse_args()

SERVER_ID = 1
PROJECT_NAME = 'bigtwo'
PHP_BIN = '/usr/bin/php'
EXEC = '/var/www/html/bigtwo_engine_web_v2/{0}/install.php' .format(args.appname)
BACK_PATH = '/tmp/init_back'
INIT_PATH = '/etc/init'

temp = '''description "PHP CRON Daemon {0}"
author      "STAGING"

{1}

start on started sshd
stop on runlevel [S016]

respawn
respawn limit 20 3

script
    [ $(/usr/bin/php {2} {3}) = 'ERROR' ] && ( stop; exit 1; )
end script
'''

(status, output) = commands.getstatusoutput('{0} {1} {2}' .format(PHP_BIN, EXEC, args.serviceid))
if status != 0:
    print output
    print "PHP EXEC Error"
    sys.exit(1)
try:
    data = json.loads(output)
    if data['status'] != 'ok':
        print '返回结果不正确'
        sys.exit(2)
except Exception as e:
    print e
    sys.exit(3)

iteams = data['result']

#### BACKUP Old Init File ######
if os.path.exists(BACK_PATH):
    for file in os.listdir(BACK_PATH):
        targetFile = os.path.join(BACK_PATH, file)
        os.remove(targetFile)
else:
    os.mkdir(BACK_PATH)

OLD_INIT_FILES = [i for i in os.listdir(INIT_PATH) if re.match(r'^GE_{0}_.*' .format(PROJECT_NAME.upper()), i)]

for i in OLD_INIT_FILES:
    sourceFile = os.path.join(INIT_PATH, i)
    targetFile = os.path.join(BACK_PATH, i)
    shutil.copyfile(sourceFile, targetFile)

OLD_SERVICE = [i.split('.conf')[0] for i in OLD_INIT_FILES]
NEW_SERVICE = [i['service'] for i in iteams]
DEL_SERVICE = list(set(OLD_SERVICE).difference(set(NEW_SERVICE)))
ADD_SERVICE = list(set(NEW_SERVICE).difference(set(OLD_SERVICE)))

DelCOUNT = 0
if DEL_SERVICE:
    for i in  DEL_SERVICE:
        (status, output) = commands.getstatusoutput('initctl stop {0}' .format(i))
        if status == 0:
            DeleteFile = os.path.join(INIT_PATH, '{0}.conf' .format(i))
            os.remove(DeleteFile)
            DelCOUNT += 1
        else:
            print "移除{0}遇到意外错误" .format(i)
            print output
AddCOUNT = 0
if ADD_SERVICE:
    for iteam in [i for i in iteams if i['service'] in ADD_SERVICE]:
        service_name = iteam['service']
        exec_path = iteam['exec']
        params = iteam['params']
        env = ""
        for key in iteam['env']:
            env = env + "env {0}={1}\n" .format(key, iteam['env'][key])
        content = temp .format(service_name, env, exec_path, params)
        FilePATH = os.path.join(INIT_PATH, '{0}.conf' .format(service_name))
        try:
            f = open(FilePATH,'w')
            f.write(content)
            f.close()
            AddCOUNT += 1
        except Exception as e:
            print "添加启动文件{0}遇到未知错误；" .format(service_name)
            print e

print "移除启动文件:\t{0}" .format(DelCOUNT)
print "添加启动文件:\t{0}" .format(AddCOUNT)