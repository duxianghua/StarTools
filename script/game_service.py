#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from saltfish.script import game_service
from saltfish.service.gamecli import GameCLI

if __name__ == '__main__':
    g = GameCLI()
    g.run()