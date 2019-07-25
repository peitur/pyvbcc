#!/usr/bin/env python3

import os, sys, re
import subprocess, shlex
import getopt

import pyvbcc
import pyvbcc.utils
import pyvbcc.validate

from pprint import pprint
class GenericCommandResult( object ):
    def __init__( self, cmd, result, exitcode = 0, **opt ):
        self._cmd = cmd
        self._result = result
        self._exitcode = exitcode
        self._debug = False
        self._test = False

        if "debug" in opt and opt['debug'] in (True, False):
            self._debug = opt["debug"]

        if "test" in opt and opt['test'] in (True, False):
            self._test = opt["test"]

    def exitcode( self ):
        return self._exitcode

    def command( self ):
        return self._command

    def result( self ):
        return self._result

class GenericCommand( object ):

    def __init__(self, cmd, **opt ):
        self._cmd = cmd
        self._debug = False
        self._test = False
        self._command = "VBoxManage"

        if "debug" in opt and opt['debug'] in (True, False):
            self._debug = opt["debug"]

        if "test" in opt and opt['test'] in (True, False):
            self._test = opt["test"]

        if pyvbcc.KEY_SYSTEM_DEBUG in opt and opt[ pyvbcc.KEY_SYSTEM_DEBUG ] in (True,False):
            self._debug = opt[ pyvbcc.KEY_SYSTEM_DEBUG ]

        if pyvbcc.KEY_SYSTEM_COMMAND in opt and opt[ pyvbcc.KEY_SYSTEM_COMMAND ] in ("VBoxManage", "VBoxHeadless"):
            self._command = opt[ pyvbcc.KEY_SYSTEM_COMMAND ]


    def run( self, **opt ):
        result = list()
        cmd = self._cmd

        if type( cmd ).__name__ == "str":
            cmd = shlex.split( cmd )

        cmd = [ self._command ] + cmd

        if self._debug: print( " ".join( cmd ) )

        if self._test:
            return GenericCommandResult( cmd, result, 999, **opt )

        prc = subprocess.Popen( cmd, universal_newlines=True, stdout=subprocess.PIPE )
        for line in prc.stdout.readlines():
            result.append( line.lstrip().rstrip() )

        return GenericCommandResult( cmd, result, prc.returncode, **opt )




class CommonCommandLine( object ):
    def __init__( self, argv, shrt=[], lng=[], **opt ):
        self._debug = False
        self._test = False
        self._argv = argv
        self._short = ["hDc:"]+shrt
        self._long = ["help","debug", "config="]+lng
        self._opt = dict()
        self._opts = None
        self._args = None
        self._validator = None

        if 'debug' in opt and opt['debug'] in (True, False):
            self._debug = opt['debug']

        if "test" in opt and opt['test'] in (True, False):
            self._test = opt["test"]

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

    def print_help( self ): pass

if __name__ == "__main__":
    pass
