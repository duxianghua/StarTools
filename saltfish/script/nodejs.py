# -*- coding: utf-8 -*-
import sys

from saltfish.service.NodejsService import GameServiceCLI, GameOptionPares
from saltfish.log.setup import setup_logger

setup_logger()

def game_service():
    c = GameOptionPares()
    c.parse_args()
    if sys.argv[1:]:
        c.parse_args()
        GameServiceCLI(**c.config)
    else:
        c.print_help()

if __name__ == '__main__':
    game_service()