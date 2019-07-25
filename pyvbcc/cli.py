 #!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc
import pyvbcc.config
import pyvbcc.validate
import pyvbcc.command

import pyvbcc.info
import pyvbcc.vm
import pyvbcc.disk
import pyvbcc.net
import pyvbcc.utils

"""
    Initial handling of all subcommands. Each command has its own handling class and parser.
    Each class inherits its basic behaviour from the pyvbcc.command.CommonCommandLine class, basic CLI handler.

    Each class needs a
    - constructor : builds the class
    - print_help method : prints help for the speciffic sub-command
    - parse method : parses the input arguments
    - action method : runs the actions for the speciffic sub-command (it's like a main for each sub-class).
"""

class HelpCommandLine( pyvbcc.command.CommonCommandLine ):
    """
        Help subcommand.
    """
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InfoCommandLine( pyvbcc.command.CommonCommandLine ):
    """
        Handles all the input from the info sub-command.
    """
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","v:","n:","d","g:", "o:"], ["help","test","debug","vm=","network=","dhcp=","group=","vm-disk=", "ostype="], **opt )

        self._validmap = {
            pyvbcc.KEY_VM_NAME :{ "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_VM_OSTYPE :{ "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_NETWORK_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_DHCP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_DISKS_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_GROUP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }

        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def print_help( self ):
        pass

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("--test"):
                self._opt[ pyvbcc.KEY_SYSTEM_TEST ] = True
            elif o in ("-v", "--vm"):
                self._opt[ pyvbcc.KEY_VM_NAME ] = a
            elif o in ("-n", "--network"):
                self._opt[ pyvbcc.KEY_NETWORK_NAME ] = a
            elif o in ("-d", "--dhcp"):
                self._opt[ pyvbcc.KEY_DHCP_NAME ] = a
            elif o in ("-g", "--group"):
                self._opt[ pyvbcc.KEY_GROUP_NAME ] = a
            elif o in ("-o", "--ostype"):
                self._opt[ pyvbcc.KEY_VM_OSTYPE ] = a
            elif o in ("--vm-disk"):
                self._opt[ pyvbcc.KEY_DISKS_NAME ] = a

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt

    def action( self ):
        if pyvbcc.KEY_VM_NAME in self._opt:
            return pyvbcc.vm.GetVmInfo( self._opt )

        if pyvbcc.KEY_VM_OSTYPE in self._opt:
            return pyvbcc.vm.GetOsTypesInfo( self._opt )

        if pyvbcc.KEY_NETWORK_NAME in self._opt:
            return pyvbcc.net.GetNetworkInfo( self._opt )

        if pyvbcc.KEY_DISKS_NAME in self._opt:
            return pyvbcc.disk.GetDiskInfo( self._opt )

        if pyvbcc.KEY_GROUP_NAME in self._opt:
            return pyvbcc.info.GetGroupInfo( self._opt )



class CreateCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def print_help( self ):
        pass

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("--test"):
                self._opt[ pyvbcc.KEY_SYSTEM_TEST ] = True

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt

class SysInfoCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__( self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("--test"):
                self._opt[ pyvbcc.KEY_SYSTEM_TEST ] = True

        return self._opt

    def action( self ):
        return pyvbcc.info.GetSystemInfo( self._opt )

class StartCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


class StopCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


class DestroyCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }

        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("--test"):
                self._opt[ pyvbcc.KEY_SYSTEM_TEST ] = True

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt

class SshCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


class ProvisionCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


class InsertCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )


class EjectCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["h","d"], ["help","debug", "test"], **opt )
        self._validmap = {
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_TEST : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
        }
        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )



def CommandLine( mode, argv, **opt ):
    if mode == "help": return HelpCommandLine( argv, **opt )
    elif mode == "info" : return InfoCommandLine( argv, **opt )
    elif mode == "create" : return CreateCommandLine( argv, **opt )
    elif mode == "start" : return StartCommandLine( argv, **opt )
    elif mode == "stop" : return StopCommandLine( argv, **opt )
    elif mode == "destroy" : return DestroyCommandLine( argv, **opt )
    elif mode == "insert" : return InsertCommandLine( argv, **opt )
    elif mode == "eject" : return EjectCommandLine( argv, **opt )
    elif mode == "sysinfo" : return SysInfoCommandLine( argv, **opt )
    else:
        raise AttributeError( "Unknown commandline mode '%s'" % ( mode ) )

if __name__ == "__main__":
    pass
