#!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc.config


class CommonCommandLine( object ):
    def __init__( self, argv, shrt=[], lng=[], **opt ):
        self._debug = False
        self._argv = argv
        self._short = ["hD"]+shrt
        self._long = ["help","debug"]+lng
        self._opt = dict()
        self._opts = None
        self._args = None

        if 'debug' in opt and opt['debug'] in (True, False):
            self._debug = opt['debug']

        try:
            self._opts, self._args = getopt.getopt( self._argv, "".join( self._short ), self._long )
        except getopt.GetoptError as err:
            raise err

    def parse(self):
        pass

class HelpCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InfoCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["v:n:d:"], ["vm=","network=","dhcp="], **opt )

    def parse( self ):

        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt['system.help'] = True
            elif o in ("-d", "--debug"):
                self._opt['system.debug'] = True
            elif o in ("-c", "--config"):
                self._opt['config.file'] = a
            elif o in ("-g", "--group"):
                self._opt['group.name'] = a
        return self._opt

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
