#!/usr/bin/env python
import subprocess
import os
import sys
import time
import signal
import httplib
import httplib2
import random

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class make_video:
    config = {
        'PIDFILE': '/var/run/video.pid',
        'FFMPEG_BIN': '/usr/bin/ffmpeg',
        'RTMP_URL': 'rtmp://live.hkstv.hk.lxdns.com/live/hks',
        'TIME': '1800',
        'VIDEOFILE':  '/tmp/out.mp4'
    }
    def __init__(self, args, **kwargs):
        if args.url:
            self.config['RTMP_URL'] = args.url

    def make_video(self):
        command = ['{bin} -i {rtmp_url} -r 29.97 -qscale 4 -t {time} -y {outfile}'.format(bin=self.config['FFMPEG_BIN'],
                                                                                          rtmp_url=self.config['RTMP_URL'],
                                                                                          time=self.config['TIME'],
                                                                                          outfile=self.config['VIDEOFILE']
                                                                                          )]
        c = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        pid = c.pid
        print pid
        try:
            with open(self.config['PIDFILE'], 'w') as f:
                f.write(str(pid))
        except Exception as e:
            c.kill()
            print e.message
            sys.exit(254)

    def get_pid(self):
        try:
            with open(self.config['PIDFILE'], 'r') as f:
                pid = int(f.read().strip())
        except (IOError,SystemExit):
            pid = None
        return pid

    def is_runing(self):
        pid = self.get_pid()
        return pid and os.path.exists('/proc/%d' % pid)

    def del_pid(self):
        if os.path.exists(self.config['PIDFILE']):
            os.remove(self.config['PIDFILE'])

    def start(self):
        self.make_video()

    def stop(self):
        if self.is_runing() == False:
            msg = 'pid file [%s] exist but ffmpeg not running.\n' % self.config['PIDFILE']
            sys.stderr.write(msg)
            sys.exit(253)
        pid = self.get_pid()
        os.kill(pid, 2)
        #for i in range(100):
        #    if self.is_runing():
        #        #os.kill(pid, signal.SIGINT)
        #        time.sleep(0.1)
        #        if i == 99:
        #            msg = 'stop ffmpeg process failure\n'
        #            sys.stderr.write(msg)
        #            sys.exit(253)
        #    break
        msg = 'Video production success: %s\n' %self.config['VIDEOFILE']
        sys.stdout.write(msg)
        sys.exit(0)

class upload_video:
    MAX_RETRIES = 10
    CLIENT_SECRETS_FILE = "client_secrets.json"
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

    def __init__(self, options):
        self.options = options
        httplib2.RETRIES = 1

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
                                       scope=self.YOUTUBE_UPLOAD_SCOPE,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("upload-oauth2.json")
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
            url='https://youtu.be/'+response['id']
            msg = url
            sys.stdout.write(msg)
            sys.exit(0)
        else:
            msg = "The upload failed with an unexpected response: %s" % response
            sys.stderr.write(msg)
            sys.exit(2)

def set_parser():
    argparser.add_argument("--file",default="/tmp/out.mp4")
    argparser.add_argument("--title", help="Video title", default="upload video TEXT!!")
    argparser.add_argument("--description",default="Test Description")
    argparser.add_argument("--category",default="22")
    #argparser.add_argument("--keywords",default="")
    argparser.add_argument("--privacyStatus",default="public")
    argparser.add_argument("--url", default=None)
    argparser.add_argument('action', choices=['start', 'stop', 'upload'])

if __name__ == '__main__':
    set_parser()
    args = argparser.parse_args()
    if args.action == 'start':
        make_video(args).start()
    elif args.action == 'stop':
        make_video(args).stop()
    elif args.action == 'upload':
        u = upload_video(args)
        u.resumable_upload()