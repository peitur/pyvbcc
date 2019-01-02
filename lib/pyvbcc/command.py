#!/usr/bin/env python3

import os, sys, re
import subprocess, shlex

import pyvbcc

from pprint import pprint

class GenericCommand( object ):

    def __init__(self, cmd, **opt ):
        self._cmd = cmd
        self._debug = False
        if pyvbcc.KEY_SYSTEM_DEBUG in opt and opt[ pyvbcc.KEY_SYSTEM_DEBUG ] in (True,False):
            self._debug = opt[ pyvbcc.KEY_SYSTEM_DEBUG ]

    def run( self, **opt ):
        result = list()
        cmd = self._cmd
        if type( cmd ).__name__ == "str":
            cmd = shlex.split( cmd )

        prc = subprocess.Popen( cmd, universal_newlines=True, stdout=subprocess.PIPE )
        for line in prc.stdout.readlines():
            result.append( line.lstrip().rstrip() )
        return result


class ListVmsCommand( GenericCommand ):
    def __init__( self, **opt ):
        super().__init__( ["VBoxManage", "list", "vms", "--sorted"], **opt )

    def run( self ):
        data = dict()
        res = super().run()
        for r in res:
            m = re.match(r"\"(.+)\"\s+{(.+)}", r )
            data[ m.group(1) ] = m.group(2)
        return data

class InfoVmCommand( GenericCommand ):
    def __init__( self, vm, **opt ):
        super().__init__( ["VBoxManage", "showvminfo", "--machinereadable",vm ], **opt )

    def run( self ):
        data = dict()
        res = super().run()

        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r"=", line )
            data[ nldata[0] ] = nldata[1]
        return data

class ListNetworkCommand( GenericCommand ):
    def __init__( self, mode, net = None, **opt ):
        super().__init__( ["VBoxManage", "list", mode ], **opt )
        self._net = net
        self._mode = mode

    def run( self ):
        data = dict()
        res = super().run()
        item = dict()
        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r":", line )

            if len( nldata ) > 1:
                key = nldata[0].lstrip().rstrip().lower()
                val = nldata[1].lstrip().rstrip()

                #for some reason natnet names are called "NetworkName"
                if key == "networkname" :
                    key = "name"

                if re.match( "name", key ) and len( item ) > 0:
                    data[ item[ 'name' ] ] = item
                    item = dict()
                item[ key ] = val

            if len( line ) == 0 and len( item ) > 0:
                data[ item['name'] ] = item

        if self._net == "all": return data
        elif self._net in data: return data[ self._net ]

        return []


class ListDiskCommand( GenericCommand ):
    def __init__( self, vm = None, **opt ):
        super().__init__( ["VBoxManage", "list", "hdds", "--long" ], **opt )
        self._vm = vm

    def run( self ):
        data = dict()
        res = super().run()
        item = dict()
        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r":", line )

            if len( nldata ) > 1:
                key = re.sub( r"\s+", "", nldata[0].lstrip().rstrip().lower() )
                val = nldata[1].lstrip().rstrip()

                if key == "inusebyvms":
                    linex = re.sub( r"\s+", "", line )
                    m = re.compile("\S+:(\S+)\(UUID:(\S+)\)").match( linex )
                    val = {"name": m.group(1), "uuid":m.group(2)}

                if re.match( "uuid", key ) and len( item ) > 0:
                    data[ item[ 'uuid' ] ] = item
                    item = dict()
                item[ key ] = val

            if len( line ) == 0 and len( item ) > 0:
                data[ item['uuid'] ] = item

        if self._vm == "all":
            return data

        return [ data[i] for i in data if data[i]['inusebyvms']['name'] == self._vm ]

class ListGroupCommand( GenericCommand ):
    def __init__( self, group, **opt ):
        super().__init__( ["VBoxManage", "list", "groups", "--long" ], **opt )
        self._group = group

    def run( self ):
        data = dict()
        res = super().run()

        for line in res:
            line = re.compile( r"\"" ).sub(  "", line )
            linex = re.compile( r"\/" ).sub(  "", line )
            if len( linex ) == 0:
                linex = "default"
            data[linex] = { "name": linex, "path": line }

        if self._group == "all":
            return data

        return [ data[x] for x in data if x == self._group ]

class CreateControllerCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._type = cfg[ pyvbcc.KEY_CONTROLLER_TYPE ]
        self._chipset = cfg[ pyvbcc.KEY_CONTROLLER_CHIPSET ]
        self._name = cfg[  pyvbcc.KEY_CONTROLLER_NAME ]
        self._pcount = "8"
        self._bootable = "off"
        self._iocache = "on"

        if pyvbcc.KEY_CONTROLLER_PCOUNT in cfg:
            self._pcount = cfg[ pyvbcc.KEY_CONTROLLER_PCOUNT ]

        if pyvbcc.KEY_CONTROLLER_BOOTABLE in cfg:
            self._bootable = cfg[ pyvbcc.KEY_CONTROLLER_BOOTABLE ]

        super().__init__( ["VBoxManage",
            "storagectl", self._vm,
            "--add", self._type,
            "--controller", self._chipset,
            "--name", self._name,
            "--portcount", self._pcount,
            "--bootable", self._bootable
        ], **opt )


class CreateDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        self._size = cfg[ pyvbcc.KEY_DISK_NAME ]
        self._filename = cfg[ pyvbcc.KEY_DISK_FILE ]

        self._format = "VMDK"
        if pyvbcc.KEY_DISK_FORMAT in cfg:
            self._format = cfg[ pyvbcc.KEY_DISK_FORMAT ]

        super().__init__( ["VBoxManage"
            "createmedium", "disk",
            "--filename", self._filename,
            "--format", self._format
        ], **opt )

class AttachDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._filename = cfg[ pyvbcc.KEY_DISK_FILE ]

        super().__init__( ["VBoxManage"
            "storageattach", self._vm
        ], **opt )


class CreateVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._group = "/%s" % (  cfg[ pyvbcc.KEY_GROUP_NAME ] )
        self._ostype = cfg[  pyvbcc.KEY_VM_OSTYPE ]
        self._name = cfg[ pyvbcc.KEY_VM_NAME ]

        super().__init__( ["VBoxManage",
            "createvm",
            "--name", self._name,
            "--groups", self._group,
            "--ostype", self._ostype,
            "--register"
        ], **opt )


class ModifyVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        super().__init__( ["VBoxManage", "modifyvm" ], **opt )
        self._group = group


class DeleteVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._delete = True


        if pyvbcc.KEY_VM_DELETE in cfg and cfg[ pyvbcc.KEY_VM_DELETE ] in (True, False):
            self._delete = cfg[ pyvbcc.KEY_VM_DELETE ]

        del_str = ""
        if self._delete:
            del_str = "--delete"

        super().__init__( ["VBoxManage", "unregistervm", self._vm, del_str ], **opt )




if __name__ == "__main__":
    import time
    vm1 = { pyvbcc.KEY_VM_NAME: "vm1", pyvbcc.KEY_GROUP_NAME: "test1", pyvbcc.KEY_VM_OSTYPE: "RedHat_64" }
    ctl1 = { pyvbcc.KEY_VM_NAME: "vm1", pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_CONTROLLER_TYPE: "sas", pyvbcc.KEY_CONTROLLER_CHIPSET: "LSILogicSAS", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on" }

    cli = CreateVmCommand( vm1 ).run()
    cli = CreateControllerCommand( ctl1 ).run()
    time.sleep(10)
    cli = DeleteVmCommand( vm1 ).run()
    pass
