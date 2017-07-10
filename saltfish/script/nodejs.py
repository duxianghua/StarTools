# -*- coding: utf-8 -*-
import os

from saltfish.service.NodejsService import GameServiceCLI, GameOptionPares

class Game(GameOptionPares):
    def run(self):
        self.parse_args(['create','bigtwo-p2p-table-12'])
        print self.config
        GameServiceCLI(**self.config)

def game_service():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print BASE_DIR
    c = GameOptionPares()
    c.parse_args(['start', 'bigtwo-P2P-table-123.service'])
    GameServiceCLI(**c.config)

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print BASE_DIR
    #game_service()