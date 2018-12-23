#!/usr/bin/env python3

import os, sys, re
import json

from pathlib import Path
from pprint import pprint

import pyvbcc.utils

################################################################################################
## Tool specific configuration
################################################################################################

DEF_SC_DEBUG=False
class SystemConfiguration( object ):
    def __init__(self, data ):
        self.debug = DEF_SC_DEBUG

DEF_VBM_DEBUG=False
class VbManageConfiguration( object ):
    def __init__(self, data ):
        self.debug = DEF_VBM_DEBUG


class Configuration( object ):

    def __init__( self, filename, **opt ):
        self.debug = False
        self.filename = filename
        self.__raw_config = None

        if 'system.debug' in opt:
            if opt['system.debug'] in ("true", "True", True): opt['system.debug'] = True
            elif opt['system.debug'] in ("false","False", False): opt['system.debug'] = False
            else: raise AttributeError("Invalid debug set value in config %s" % (opt['system.debug']) )
            self.debug = opt['system.debug']

        if pyvbcc.utils.file_is_json( self.filename ):
            try:

                self.__raw_config = pyvbcc.utils.load_file( self.filename )
                if 'system' in self.__raw_config: self.__system_config = SystemConfiguration( self.__raw_config['system'] )
                if 'vbm' in self.__raw_config: self.__vbmanage_config = VbManageConfiguration( self.__raw_config['vbm'] )

            except Exception as e:
                raise
        else:
            raise RuntimeError("Unexpected configuration file, must be json")

        try:
            self.__populate_config()
        except Exception as e:
            raise e

    def __populate_config( self ):
        pass

    def pprint_raw( self ):
        pprint( self.__raw_config )


################################################################################################
## Group specific configuration
################################################################################################
DEF_GC_DEBUG=False
class GroupConfiguration( object ):

    def __init__( self, **data ):
        self.debug = DEF_GC_DEBUG


if __name__ == "__main__":
    pass
