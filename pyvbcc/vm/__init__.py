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

#import pyvbcc.info
#import pyvbcc.disk
#import pyvbcc.net


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

def GetOsTypesInfo( opt ):
    if opt[ pyvbcc.KEY_VM_OSTYPE ] == "all":
        del opt[ pyvbcc.KEY_VM_OSTYPE ]
    return pyvbcc.vm.commands.ListOsTypesCommand( **opt ).run()

def RunOnVm( vm, cmd, cmdargs, opt ):
    pass

def PutToVm( vm, src, trg, opt ):
    pass

def GetFromVm( vm, src, trg, opt ):
    pass