 #!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc
import pyvbcc.config
import pyvbcc.validate
import pyvbcc.command

class CommonCommandLine( object ):
    def __init__( self, argv, shrt=[], lng=[], **opt ):
        self._debug = False
        self._argv = argv
        self._short = ["hDc:"]+shrt
        self._long = ["help","debug", "config="]+lng
        self._opt = dict()
        self._opts = None
        self._args = None
        self._validator = None

        if 'debug' in opt and opt['debug'] in (True, False):
            self._debug = opt['debug']

        try:
            self._opts, self._args = getopt.getopt( self._argv[1:], "".join( self._short ), self._long )
        except getopt.GetoptError as err:
            raise err

    def get( self, key ):
        if key in self._opt:
            return self._opt[ key ]
        return None

    def parse(self): pass

    def action( self ): pass

class HelpCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InfoCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["v:","n:","d:","g:"], ["vm=","network=","dhcp=","group=","vm-disk="], **opt )

        self._validmap = {
            pyvbcc.KEY_VM_NAME :{ "match":["^[a-zA-Z0-9\-\.]+$"] },
            pyvbcc.KEY_NETWORK_NAME : { "match":["^[a-zA-Z0-9\-\.]+$"] },
            pyvbcc.KEY_DHCP_NAME : { "match":["^[a-zA-Z0-9\-\.]+$"] },
            pyvbcc.KEY_DISKS_VM_NAME : { "match":["^[a-zA-Z0-9\-\.]+$"] },
            pyvbcc.KEY_GROUP_NAME : { "match":["^[a-zA-Z0-9\-\.]+$"] }
        }

        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("-v", "--vm"):
                self._opt[ pyvbcc.KEY_VM_NAME ] = a
            elif o in ("-n", "--network"):
                self._opt[ pyvbcc.KEY_NETWORK_NAME ] = a
            elif o in ("-d", "--dhcp"):
                self._opt[ pyvbcc.KEY_DHCP_NAME ] = a
            elif o in ("-g", "--group"):
                self._opt[ pyvbcc.KEY_GROUP_NAME ] = a
            elif o in ("--vm-disk"):
                self._opt[ pyvbcc.KEY_DISKS_VM_NAME ] = a

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt


    def action( self ):
        if pyvbcc.KEY_VM_NAME in self._opt:
            res = pyvbcc.command.InfoVmCommand( self._opt[ pyvbcc.KEY_VM_NAME ] ).run()
            pprint( res )
        elif pyvbcc.KEY_NETWORK_NAME in self._opt:
            allnets = dict()
            for t in ["intnets", "bridgedifs", "hostonlyifs", "natnets"]:
                allnets[ t ] = pyvbcc.command.ListNetworkCommand( t, self._opt[ pyvbcc.KEY_NETWORK_NAME ] ).run()
            pprint( allnets )
        elif pyvbcc.KEY_DISKS_VM_NAME in self._opt:
            res = pyvbcc.command.ListDiskCommand( self._opt[ pyvbcc.KEY_DISKS_VM_NAME ] ).run()
            pprint( res )


class CreateCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class StartCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class StopCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class DestroyCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class SshCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class ProvisionCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InsertCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class EjectCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )



def CommandLine( mode, argv, **opt ):
    if mode == "help": return HelpCommandLine( argv, **opt )
    elif mode == "info" : return InfoCommandLine( argv, **opt )
    elif mode == "create" : return CreateCommandLine( argv, **opt )
    elif mode == "start" : return StartCommandLine( argv, **opt )
    elif mode == "stop" : return StopCommandLine( argv, **opt )
    elif mode == "destroy" : return DestroyCommandLine( argv, **opt )
    elif mode == "insert" : return InsertCommandLine( argv, **opt )
    elif mode == "eject" : return EjectCommandLine( argv, **opt )
    else:
        raise AttributeError( "Unknown commandline mode '%s'" % ( mode ) )

if __name__ == "__main__":
    pass
