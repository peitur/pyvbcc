 #!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc
import pyvbcc.config
import pyvbcc.utils
import pyvbcc.validate

import pyvbcc.command

import pyvbcc.vm.commands

def GetVmInfo( opt ):
    if opt[ pyvbcc.KEY_VM_NAME ] == "all":
        return GetVms( opt )
    else:
        vm = opt[ pyvbcc.KEY_VM_NAME ]
        return GetVm( vm, opt )

def GetVms( opt ):
    return pyvbcc.vm.commands.ListVmsCommand( **opt ).run()

def GetVm( vm, opt ):
    return pyvbcc.vm.commands.InfoVmCommand( vm, **opt ).run()
