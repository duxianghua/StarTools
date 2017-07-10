# -*- coding: utf-8 -*-
from saltfish.service.NodejsService import GameServiceCLI, GameOptionPares
from saltfish.log.setup import setup_logger

class Game(GameOptionPares):
    def run(self):
        self.parse_args()
        print self.config
        GameServiceCLI(**self.config)

setup_logger()

def game_service():
    c = GameOptionPares()
    c.parse_args()
    GameServiceCLI(**c.config)

if __name__ == '__main__':
    game_service()