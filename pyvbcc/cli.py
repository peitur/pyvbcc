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



class HelpCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InfoCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["v:","n:","d","g:"], ["debug","vm=","network=","dhcp=","group=","vm-disk="], **opt )

        self._validmap = {
            pyvbcc.KEY_VM_NAME :{ "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_NETWORK_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_DHCP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_DISKS_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_GROUP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] },
            pyvbcc.KEY_SYSTEM_DEBUG : {"match":[".*"]},
            pyvbcc.KEY_SYSTEM_HELP : {"match":[".*"]}
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
                self._opt[ pyvbcc.KEY_DISKS_NAME ] = a

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt


    def action( self ):
        if pyvbcc.KEY_VM_NAME in self._opt:
            res = pyvbcc.info.GetVmInfo( self._opt ) 
            pprint( res )

        if pyvbcc.KEY_NETWORK_NAME in self._opt:
            allnets = pyvbcc.info.GetNetworkInfo( self._opt )
            pprint( allnets )
            
        if pyvbcc.KEY_DISKS_NAME in self._opt:
            res = pyvbcc.info.GetDiskInfo( self._opt[ pyvbcc.KEY_DISKS_NAME ] ).run()
            pprint( res )

        if pyvbcc.KEY_GROUP_NAME in self._opt:
            res = pyvbcc.info.GetGroupInfo( self._opt )
            pprint( res )

class CreateCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["g:"], ["group="], **opt )
        self._validmap = {
            pyvbcc.KEY_GROUP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] }
        }

        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("-g", "--group"):
                self._opt[ pyvbcc.KEY_GROUP_NAME ] = a

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt

class StartCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class StopCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class DestroyCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, ["g:"], ["group="], **opt )
        self._validmap = {
            pyvbcc.KEY_GROUP_NAME : { "match":["^[a-zA-Z0-9\-\._]+$"] }
        }

        self._validator = pyvbcc.validate.Validator( self._validmap, **opt )

    def parse( self ):
        for o, a in self._opts:
            if a in ("-h", "--help"):
                self._opt[ pyvbcc.KEY_SYSTEM_HELP ] = True
            elif o in ("-d", "--debug"):
                self._opt[ pyvbcc.KEY_SYSTEM_DEBUG ] = True
            elif o in ("-g", "--group"):
                self._opt[ pyvbcc.KEY_GROUP_NAME ] = a

        ## Either this is true, or get exception
        self._validator.validate( self._opt )

        return self._opt

class SshCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class ProvisionCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class InsertCommandLine( pyvbcc.command.CommonCommandLine ):
    def __init__(self, argv, **opt ):
        super().__init__( argv, [], [], **opt )


class EjectCommandLine( pyvbcc.command.CommonCommandLine ):
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
