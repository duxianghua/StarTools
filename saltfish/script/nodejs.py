# -*- coding: utf-8 -*-
import sys
import os

from saltfish.utils.parsers import SaltfishJsOptionPares

class SaltFishService(SaltfishJsOptionPares):
    def run(self):
        print 'asdfsf'
        self.parse_args()
        from saltfish.service.nodejs import p2p_service
        print self.config
        p2p_service(**self.config)

if __name__ == '__main__':
    SaltFishService().run()