#!/usr/bin/env python
import subprocess
import os
import sys
import time
import ConfigParser
import json
import commands
import argparse
import httplib2
import signal

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class MakeVideo(object):
    config = {
        'timestamp': time.time(),
        'rtmp_bin': '/usr/bin/ffmpeg',
        'config_file': '/tmp/video.ini',
        'error': None,
    }

    def __init__(self, **kwargs):
        super(MakeVideo, self).__init__()

    def set_options(self):
        c = ConfigParser.ConfigParser()
        c.read(self.config['config_file'])
        c.add_section(self.config['jobid'])

        for i in self.config:
            c.set(self.config['jobid'], i, self.config[i])

        c.write(open(self.config['config_file'], 'w'))

    def get_options(self, jobid):
        c = ConfigParser.ConfigParser()
        c.read(self.config['config_file'])
        if not c.has_section(jobid):
            msg = 'Not find job[%s]' % jobid
            sys.stderr.write(msg)
            sys.exit(1)

        for i in c.options(jobid):
            self.config[i] = c.get(jobid, i)

    def remove_options(self, jobid):
        c = ConfigParser.ConfigParser()
        c.read(self.config['config_file'])
        c.remove_section(jobid)
        c.write(open(self.config['config_file'], 'w'))

    def make_video(self):
        # cmd = 'WSLINK=wss://xlw32.718188.com:481 FILEPATH=/tmp/{jobid}.mpeg NODE_PATH=/usr/lib/node_modules /usr/bin/node /usr/local/bin/record.js'
        # cmd = '{bin} -i "{rtmp_url}" -filter:v "crop=1200:500:450:350" -r 15 -t {time} -y {outfile}'
        command = ['WSLINK={rtmp_url} FILEPATH=/tmp/{jobid}.mpeg NODE_PATH=/usr/lib/node_modules /usr/bin/node /usr/local/bin/record.js'.format(**self.config)]
        c = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        self.config['pid'] = c.pid
        for i in range(1, 5):
            time.sleep(1)
            if c.poll():
                self.config['error'] = c.stderr.read()
                self._exit()

    def watermark(self, video, image, outdir='/data/video', *args, **kwargs):
        # cmd = 'ffmpeg -i {video} -loop 1 -i {image} -acodec copy -filter_complex "[1:v] fade=in:st=3:d=0 [logo]; [0:v][logo] overlay=0:0" -t 5 {outfile}'
        cmd_str = 'ffmpeg -i {video} -loop 1 -i {image} -acodec copy -filter_complex "[1:v] fade=in:st={stime}:d=0 [logo]; [0:v][logo] overlay=0:0" -crf 35 -t {duration} {outfile}'
        self.gettime(video)
        st = self.config['_time'] - 2
        self.config['jobid'] = hash(time.time())
        outfile = os.path.join(outdir, '%s.mp4'%self.config['jobid'])
        command = cmd_str.format(video=video, image=image, outfile=outfile, stime=st, duration=self.config['_time'])
        c = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        c.communicate()
        if c.returncode == 0:
            self.config['outfile'] = outfile
            self.extract()
            os.remove(video)
            self._exit()
        else:
            try:
                self.config['error'] = c.stderr.read()
            except Exception as e:
                self.config['error'] = e.message
            self._exit()

    def extract(self):
        cmd_str = 'ffmpeg -i {video} -y -f image2 -ss {sstime} -t 0.01 -s 528x312 {image}'
        cfg = {
            'sstime': self.config['_time'] - 0.2,
            'video': self.config['outfile'],
            'image': os.path.join('/data/image', '%s.jpg'%self.config['jobid'])
        }
        command = cmd_str.format(**cfg)
        c = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        c.communicate()
        if c.returncode == 0:
            self.config['image'] = cfg['image']
        else:
            self.config['error'] = 'extract frname fail'

    def gettime(self, video):
        # cmd = 'ffmpeg -i test.mp4 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//'
        if os.path.exists(video):
            cmd = "ffmpeg -i %s 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//" % video
            returncode, rev = commands.getstatusoutput(cmd)
            if returncode == 0:
                self.config['duration'] = rev
                self.config['_time'] = self.formatduration(rev)
            else:
                self.config['error'] = 'Failed to get video duration'
                self._exit()
        else:
            self.config['error'] = 'No such file or directory: "%s"' %video
            self._exit()

    def formatduration(self, t):
        try:
            l = t.split(':')
            return int(int(l[0])*3600 + int(l[1])*60 + float(l[2]))
        except Exception as e:
            self.config['error'] = e.message
            self._exit()

    def is_runing(self):
        try:
            pid = self.config['pid']
            return os.path.exists('/proc/%s' % pid)
        except KeyError:
            return False

    def start(self, options):
        if not options.duration:
            duration = '15'
        else:
            duration = options.duration
        self.config['jobid'] = str(hash(time.time()))
        self.config['rtmp_url'] = options.url
        self.config['duration'] = duration
        self.config['outfile'] = '/tmp/%s.mp4' % self.config['jobid']
        if self.is_runing():
            self.config['error'] = 'Job "%s" already exists' % self.config['rtmp_url']
            self._exit()
        self.make_video()
        self.set_options()
        self._exit()

    def stop(self, options):
        jobid = options.jobid
        self.get_options(jobid)
        if not self.is_runing():
            #msg = 'job [%s] exists, but ffmpeg process not running.\n' % self.config['pid']
            #self.config['error'] = msg
            #self._exit()
            pass
        else:
            os.kill(int(self.config['pid']), signal.SIGTERM)
            for i in range(1, 100):
                if not self.is_runing():
                    break
                else:
                    time.sleep(1)
        command = '/usr/bin/ffmpeg -i /tmp/{jobid}.mpeg {outfile}'.format(**self.config)
        status, rev = commands.getstatusoutput(command)
        new_tiemstamp = time.time()
        self.config['duration'] = new_tiemstamp - float(self.config['timestamp'])
        self.remove_options(jobid)
        self.config['error'] = None
        self._exit()

    def _exit(self):
        if self.config['error']:
            returncode = 1
        else:
            returncode = 0
        sys.stdout.write(json.dumps(self.config))
        sys.exit(returncode)


class upload_video:
    MAX_RETRIES = 10
    CLIENT_SECRETS_FILE = "/var/www/config/client_secrets.json"
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

    def __init__(self, options):
        self.options = options
        if not self.options.file:
            sys.stderr.write('Need to provide upload video file')
            sys.exit(1)
        httplib2.RETRIES = 1

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
                                       scope=self.YOUTUBE_UPLOAD_SCOPE,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("/var/www/config/upload-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, self.options)

        return build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    def initialize_upload(self):
        youtube = self.get_authenticated_service()
        body = dict(
            snippet=dict(
                title=self.options.title,
                # description=options.description,
                # tags=tags,
                categoryId=self.options.category
            ),
            status=dict(
                privacyStatus=self.options.privacyStatus
            )
        )

        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(self.options.file, chunksize=-1, resumable=True)
        )
        return insert_request

    def resumable_upload(self):
        status, response = self.initialize_upload().next_chunk()
        if 'id' in response:
            url = 'https://youtu.be/' + response['id']
            msg = url
            sys.stdout.write(msg)
            sys.exit(0)
        else:
            msg = "The upload failed with an unexpected response: %s" % response
            sys.stderr.write(msg)
            sys.exit(2)

def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File Name")
    parser.add_argument("--title", help="Video title", default="video....")
    parser.add_argument("--description", default="Test Description")
    parser.add_argument("--category", default="22")
    parser.add_argument("--privacyStatus", default="public")
    parser.add_argument("--url", default=None)
    parser.add_argument("--jobid", default=None)
    parser.add_argument("--duration", default=None)
    parser.add_argument("--video", default=None)
    parser.add_argument("--image", default=None)
    parser.add_argument('action', choices=['start', 'stop', 'upload', 'watermark'])
    return parser


def man(options):
    if options.action == 'start':
        MakeVideo().start(options)

    elif options.action == 'stop':
        MakeVideo().stop(options)

    elif options.action == 'upload':
        up = upload_video(options)
        up.resumable_upload()
    elif options.action == 'watermark':
        MakeVideo().watermark(options.video, options.image)


if __name__ == '__main__':
    p = set_parser()
    args = p.parse_args()
    man(args)
