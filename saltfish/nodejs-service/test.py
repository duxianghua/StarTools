import argparse

parser = argparse.ArgumentParser(description='Test Process.')
parser.add_argument('action', choices=['start',
                                                  'stop',
                                                  'restart',
                                                  'reload',
                                                  'kill'])
parser.add_argument('service')
parser.add_argument('--signal',metavar='signal')
args = parser.parse_args()
print args
print args.__dict__