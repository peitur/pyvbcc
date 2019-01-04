#!/usr/bin/env python3

import os, sys, re
import subprocess, shlex

import pyvbcc
import pyvbcc.utils

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

        if self._debug: print( " ".join( cmd ) )

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

class ListSystemPropertiesCommand( GenericCommand ):
    def __init__( self, vm = None, **opt ):
        super().__init__( ["VBoxManage", "list", "systemproperties", "--long" ], **opt )
        self._vm = vm

    def run( self ):
        data = dict()
        res = super().run()
        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r":", line )

            if len( nldata ) > 1:
                key = re.sub( r"\s+", "", nldata[0].lstrip().rstrip().lower() )
                val = nldata[1].lstrip().rstrip()
                data[ key ] = val

        return data


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
            "--bootable", self._bootable,
            "--hostiocache", self._iocache
        ], **opt )


class CreateDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):

        if pyvbcc.KEY_DISKS_SIZE not in cfg or pyvbcc.KEY_DISKS_FILE not in cfg:
            raise AttributeError("Missing disk size or filename")

        self._size = cfg[ pyvbcc.KEY_DISKS_SIZE ]
        self._filename = cfg[ pyvbcc.KEY_DISKS_FILE ]

        self._format = "vmdk"
        if pyvbcc.KEY_DISKS_FORMAT in cfg:
            self._format = cfg[ pyvbcc.KEY_DISKS_FORMAT ]

        super().__init__( ["VBoxManage",
            "createmedium", "disk",
            "--filename", self._filename,
            "--format", self._format,
            "--size", self._size
        ], **opt )



class CloseDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):

        if pyvbcc.KEY_DISKS_FILE not in cfg:
            raise AttributeError("Missing disk filename trying to close")

        self._filename = cfg[ pyvbcc.KEY_DISKS_FILE ]

        self._delete = True
        if pyvbcc.KEY_DISKS_DELETE in cfg and cfg[ pyvbcc.KEY_DISKS_DELETE ] in (True, False):
            self._delete = cfg[ pyvbcc.KEY_VM_DELETE ]

        del_str = ""
        if self._delete:
            del_str = "--delete"

        super().__init__( ["VBoxManage",
            "closemdium", "disk", self._filename,
            del_str
        ], **opt )

class AttachDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_CONTROLLER_NAME not in cfg or pyvbcc.KEY_DISKS_FILE  not in cfg:
            raise AttributeError("Missint VM or Controller or Disk file in attach")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._controller = cfg[ pyvbcc.KEY_CONTROLLER_NAME ]
        self._disk = cfg[ pyvbcc.KEY_DISKS_FILE ]
        self._type = "hdd"
        self._port = "0"
        self._mtype = None
        self._device = "0"
        self._comment = None

        params = ["VBoxManage",
            "storageattach", self._vm,
            "--storagectl", self._controller,
            "--medium", self._disk
        ]

        if pyvbcc.KEY_DISKS_TYPE in cfg: self._type = cfg[ pyvbcc.KEY_DISKS_TYPE ]
        if pyvbcc.KEY_DISKS_PORT in cfg: self._port = cfg[ pyvbcc.KEY_DISKS_PORT ]
        if pyvbcc.KEY_DISKS_MTYPE in cfg: self._mtype = cfg[ pyvbcc.KEY_DISKS_MTYPE ]
        if pyvbcc.KEY_DISKS_DEVICE in cfg: self._device = cfg[ pyvbcc.KEY_DISKS_DEVICE ]
        if pyvbcc.KEY_DISKS_COMMENT in cfg: self._comment = cfg[ pyvbcc.KEY_DISKS_COMMENT ]

        if self._type: params += list( [ "--type", self._type ] )
        if self._port: params += list( [ "--port", self._port ] )
        if self._device: params += list( [ "--device", self._device ] )
        if self._mtype: params += list( [ "--mtype", self._mtype ] )
        if self._comment: params += list( [ "--comment", self._comment ] )

        super().__init__( params, **opt )


class RegisterVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_DISKS_FILE not in cfg:
            raise AttributeError( "No filename to register" )

        if not os.path.exists( cfg[ pyvbcc.KEY_DISKS_FILE ] ):
            raise RuntimeError("Missing VM disk in registration")

        self._filename = cfg[ pyvbcc.KEY_DISKS_FILE ]

        super().__init__( ["VBoxManage",
            "registervm", self._filename
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
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]

        self._ostype = None
        self._groups = None
        self._description = None
        self._cpus = None
        self._cpu_hotplug = None
        self._cpu_limit = None
        self._memory = None
        self._vram = None
        self._audio = None
        self._pae = None
        self._acpi = None
        self._apic = None
        self._pagefusion = None
        self._firmware = None
        self._chipset = None
        self._usb = None
        self._keyboard = None
        self._mouse = None

        params = ["VBoxManage", "modifyvm", self._vm ]

        if self._port: params += list( [ "--port", self._port ] )

        super().__init__( params, **opt )



class ModifyVmBootCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._boot_id = cfg[ pyvbcc.KEY_BOOT_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )


class ModifyVmNicCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):

        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        self._nic_net = None
        self._nic_mac = None
        self._nic_connected = None
        self._nic_type = None
        self._nic_trace = None
        self._nic_trace_file = None
        self._nic_property = None
        self._nic_speed = None
        self._nic_bootprio = None
        self._nic_promisc = None
        self._nic_bandwidth_group = None
        self._nic_genericdrv = None

        if pyvbcc.KEY_NIC_NET in cfg: self._nic_net = cfg[ pyvbcc.KEY_NIC_NET ]
        if pyvbcc.KEY_NIC_MAC in cfg: self._nic_mac = cfg[ pyvbcc.KEY_NIC_MAC ]
        if pyvbcc.KEY_NIC_CONNECTED in cfg: self._nic_connected = cfg[ pyvbcc.KEY_NIC_CONNECTED ]
        if pyvbcc.KEY_NIC_TYPE in cfg: self._nic_type = cfg[ pyvbcc.KEY_NIC_TYPE ]
        if pyvbcc.KEY_NIC_TRACE in cfg: self._nic_trace = cfg[ pyvbcc.KEY_NIC_TRACE ]
        if pyvbcc.KEY_NIC_TRACEFILE in cfg: self._nic_trace_file = cfg[ pyvbcc.KEY_NIC_TRACEFILE ]
        if pyvbcc.KEY_NIC_PROPERTY in cfg: self._nic_property = cfg[ pyvbcc.KEY_NIC_PROPERTY ]
        if pyvbcc.KEY_NIC_SPEED in cfg: self._nic_speed = cfg[ pyvbcc.KEY_NIC_SPEED ]
        if pyvbcc.KEY_NIC_BOOTPRIO in cfg: self._nic_bootprio = cfg[ pyvbcc.KEY_NIC_BOOTPRIO ]
        if pyvbcc.KEY_NIC_PROMISC in cfg: self._nic_promisc = cfg[ pyvbcc.KEY_NIC_PROMISC ]
        if pyvbcc.KEY_NIC_BANDWIDTH_GROUP in cfg: self._nic_bandwidth_group = cfg[ pyvbcc.KEY_NIC_BANDWIDTH_GROUP ]
        if pyvbcc.KEY_NIC_GENERICDRV in cfg: self._nic_genericdrv = cfg[ pyvbcc.KEY_NIC_GENERICDRV ]

        params = ["VBoxManage", "modifyvm", self._vm ]
        if self._nic_net: params += list( [ "--nic%s" % (self._nic_id), self._nic_net ] )
        if self._nic_mac: params += list( [ "--macaddress%s" % (self._nic_id), self._nic_mac ] )
        if self._nic_connected: params += list( [ "--cableconnected%s" % (self._nic_id), self._nic_connected ] )
        if self._nic_type: params += list( [ "--nictype%s" % (self._nic_id), self._nic_type ] )
        if self._nic_trace: params += list( [ "--nictrace%s" % (self._nic_id), self._nic_trace ] )
        if self._nic_trace_file: params += list( [ "--nictracefile%s" % (self._nic_id), self._nic_trace_file ] )
        if self._nic_speed: params += list( [ "--nicspee%s" % (self._nic_id), self._nic_speed ] )
        if self._nic_bootprio: params += list( [ "--nicbootprio%s" % (self._nic_id), self._nic_bootprio ] )
        if self._nic_promisc: params += list( [ "--nicpromisc%s" % (self._nic_id), self._nic_promisc ] )
        if self._nic_bandwidth_group: params += list( [ "--nicbandwidthgroup%s" % (self._nic_id), self._nic_bandwidth_group ] )
        if self._nic_genericdrv: params += list( [ "--nicgenericdrv%s" % (self._nic_id), self._nic_genericdrv ] )

#        if self._nic_property: params += list( [ "--nicproperty%s" % (self._nic_id), self._nic_property ] )

        super().__init__( params, **opt )


class ModifyVmNatNicCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )


class ModifyVmHostOnlyNicCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )

class ModifyVmInteNetNicCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )

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

    info = ListSystemPropertiesCommand().run()
    home = pyvbcc.utils.read_env("HOME")

    vm = "vm2"
    group = "test1"
    vmdir = "%s/%s/%s" % ( info["defaultmachinefolder"], group, vm )
    vmfile = "%s/%s.vmdk" % ( vmdir, vm )
    dvdfile = "%s/Downloads/CentOS-7-x86_64-NetInstall-1810.iso" % ( home )

    vm1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_GROUP_NAME: "test1", pyvbcc.KEY_VM_OSTYPE: "RedHat_64", pyvbcc.KEY_DISKS_FILE: vmfile }
    ctl0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_CONTROLLER_TYPE: "ide", pyvbcc.KEY_CONTROLLER_PCOUNT: "2", pyvbcc.KEY_CONTROLLER_CHIPSET: "PIIX4", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on" }
    ctl1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_CONTROLLER_TYPE: "sas", pyvbcc.KEY_CONTROLLER_CHIPSET: "LSILogicSAS", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on" }
    dks0 = { pyvbcc.KEY_DISKS_FILE: vmfile, pyvbcc.KEY_DISKS_FORMAT:"vmdk", pyvbcc.KEY_DISKS_NAME:"dm1-disk", pyvbcc.KEY_DISKS_SIZE: "4096"}
    atts0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_DISKS_FILE: vmfile }
    atts1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_DISKS_FILE: dvdfile, pyvbcc.KEY_DISKS_TYPE: "dvddrive" }

    cli = CreateVmCommand( vm1 ).run()
    cli = CreateControllerCommand( ctl0 ).run()
    cli = CreateControllerCommand( ctl1 ).run()
    cli = CreateDiskCommand( dks0 ).run()
    cli = AttachDiskCommand( atts0 ).run()
    if os.path.exists( dvdfile ):
        cli = AttachDiskCommand( atts1 ).run()
    else:
        print("ERROR: Install ISO was not found ... skipping: %s" % ( dvdfile ) )

    time.sleep(60)
    cli = DeleteVmCommand( vm1 ).run()
    pass
