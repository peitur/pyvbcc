#!/usr/bin/env python3

import os, sys, re
from pathlib import Path
from pprint import pprint


class VbEnvironment( object ):

    def __init__( self, mode, filename, **opt ):

        if "debug" in opt and opt['debug'] in (True, False):
            self._debug = opt["debug"]

        pass



class VbManage(object):

    def __init__( self, config, opt ):

        if "debug" in opt and opt['debug'] in (True, False):
            self._debug = opt["debug"]

        self._main_condfig = config
        self._env_config = pyvbcc.vbm.VbEnvironment( opt[ pyvbcc.KEY_SYSTEM_MODE ], opt[ pyvbcc.KEY_SYSTEM_ENVFILE ], **opt  )

        pass




if __name__ == "__main__":
    pass
