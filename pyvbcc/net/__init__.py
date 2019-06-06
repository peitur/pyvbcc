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
import pyvbcc.net.commands




def GetNetworkInfo( opt ):
    allnets = dict()
    types = ["intnets", "bridgedifs", "hostonlyifs", "natnets"]

    if pyvbcc.KEY_NETWORK_TYPE in opt and opt[ pyvbcc.KEY_NETWORK_TYPE ] in types:
        types = [ opt[ pyvbcc.KEY_NETWORK_TYPE ] ]

    for t in types:
        allnets[ t ] = pyvbcc.net.commands.ListNetworkCommand( t, opt[ pyvbcc.KEY_NETWORK_NAME ] ).run()
    return allnets

def CreateNatNetwork( opt ):
    pass

def ModifyNatNetwork( net, opt ):
    pass

def DeleteNatNetwork( net, opt ):
    pass