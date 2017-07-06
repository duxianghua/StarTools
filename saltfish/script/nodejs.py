# -*- coding: utf-8 -*-

from saltfish.service.NodejsService import GameServiceCLI, GameOptionPares
import script

class Game(GameOptionPares):
    def run(self):
        self.parse_args(['create','bigtwo-p2p-table-12'])
        print self.config
        GameServiceCLI(**self.config)

def game_service():
    c = GameOptionPares()
    c.parse_args()
    GameServiceCLI(**c.config)

if __name__ == '__main__':
    game_service()