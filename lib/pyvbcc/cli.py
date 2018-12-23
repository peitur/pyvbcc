#!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc.config


class CommonCommandLine( object ):
    def __init__( self, argv, **opt ):
        pass

class HelpCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class CreateCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class StartCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class StopCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class DestroyCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class SshCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class ProvisionCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class InsertCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass

class EjectCommandLine( CommonCommandLine ):
    def __init__(self, argv, **opt ):
        pass


def CommandLine( mode, argv, **opt ):
    if mode == "help": return HelpCommandLine( argv, **opt )
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
