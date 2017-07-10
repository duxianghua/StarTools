# -*- coding: utf-8 -*-
import os

from saltfish.service.NodejsService import GameServiceCLI, GameOptionPares

class Game(GameOptionPares):
    def run(self):
        self.parse_args()
        print self.config
        GameServiceCLI(**self.config)

def game_service():
    c = GameOptionPares()
    c.parse_args()
    GameServiceCLI(**c.config)

if __name__ == '__main__':
    game_service()