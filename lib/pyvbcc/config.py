#!/usr/bin/env python3

import os, sys, re
import json

from pathlib import Path
from pprint import pprint


class SystemConfiguration( object ):
    def __init__(self, **data ):
        pass

class NetworkConfiguration( object ):
    def __init__(self, **data ):
        pass

class VmConfiguration( object ):
    def __init__(self, **data ):
        pass

class VbManageConfiguration( object ):
    def __init__(self, **data ):
        pass


class Configuration( object ):

    def __init__( self, filename, **opt ):
        self.debug = False

        if 'system.debug' in opt:
            if opt['system.debug'] in ("true", "True", True): opt['system.debug'] = True
            elif opt['system.debug'] in ("false","False", False): opt['system.debug'] = False
            else: raise AttributeError("Invalid debug set value in config %s" % (opt['system.debug']) )

if __name__ == "__main__":
    pass
