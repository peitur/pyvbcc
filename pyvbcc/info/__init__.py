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


if __name__ == "__main__":
    pass