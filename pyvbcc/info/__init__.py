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
import pyvbcc.info.commands


def GetVmInfo( opt ):
    res = None
    if opt[ pyvbcc.KEY_VM_NAME ] == "all":
        res = pyvbcc.info.commands.ListVmsCommand( ).run()
    else:
        res = pyvbcc.info.commands.InfoVmCommand( opt[ pyvbcc.KEY_VM_NAME ] ).run()
    return res

def GetGroupInfo( opt ):
    return pyvbcc.info.commands.ListGroupCommand( opt[ pyvbcc.KEY_GROUP_NAME ] ).run()

def GetDiskInfo( opt ):
    return pyvbcc.info.commands.ListDiskCommand( opt[ pyvbcc.KEY_DISKS_NAME ] ).run()

def GetNetworkInfo( opt ):
    allnets = dict()
    for t in ["intnets", "bridgedifs", "hostonlyifs", "natnets"]:
        allnets[ t ] = pyvbcc.info.commands.ListNetworkCommand( t, opt[ pyvbcc.KEY_NETWORK_NAME ] ).run()
    return allnets

def GetSystemInfo( opt ):
    return pyvbcc.info.commands.ListSystemPropertiesCommand( self._opt )

if __name__ == "__main__":
    pass