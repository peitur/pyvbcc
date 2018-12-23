#!/usr/bin/env python3

import os, sys, re

import subprocess, shlex


class GerictCommand( object ):

    def __init__(self, **opt ):
        pass
        
    def run( cmd, mode = {} ):

        result = list()
        if type( cmd ).__name__ == "str":
            cmd = shlex.split( cmd )

        prc = subprocess.Popen( cmd, universal_newlines=True, stdout=subprocess.PIPE )
        for line in prc.stdout.readlines():
            result.append( line.lstrip().rstrip() )
        return result


if __name__ == "__main__":
    pass
