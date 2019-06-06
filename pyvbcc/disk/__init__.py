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
import pyvbcc.disk.commands


def GetDiskInfo( opt ):
    return pyvbcc.disk.commands.ListDiskCommand( opt[ pyvbcc.KEY_DISKS_NAME ] ).run()
