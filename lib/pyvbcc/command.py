#!/usr/bin/env python3

import os, sys, re
import subprocess, shlex

import pyvbcc
import pyvbcc.utils
import pyvbcc.validate

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

###########################################################################################################################
## Listing stuff commands
###########################################################################################################################
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



###########################################################################################################################
## Basic controller commands
###########################################################################################################################
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

###########################################################################################################################
## Basic dock management commands
###########################################################################################################################
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

###########################################################################################################################
## VM basic management
###########################################################################################################################
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

class _CreateVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._group = "/%s" % (  cfg[ pyvbcc.KEY_GROUP_NAME ] )
        self._ostype = cfg[  pyvbcc.KEY_VM_OSTYPE ]
        self._name = cfg[ pyvbcc.KEY_VM_NAME ]
        self._register = True

        if pyvbcc.KEY_VM_REGISTER in cfg and cfg[ pyvbcc.KEY_VM_NAME ] in (True, False):
            self._register = cfg[ pyvbcc.KEY_VM_NAME ]

        reg_str = ""
        if self._register:
            reg_str = "--register"

        super().__init__( ["VBoxManage",
            "createvm",
            "--name", self._name,
            "--groups", self._group,
            "--ostype", self._ostype,
            reg_str
        ], **opt )


class CreateVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):

        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_VM_OSTYPE: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_GROUP_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_VM_REGISTER: { "match":["True", "False"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._register = True
        if pyvbcc.KEY_VM_REGISTER in self._cfg and self._cfg[ pyvbcc.KEY_VM_NAME ] in (True, False):
            self._register = self._cfg[ pyvbcc.KEY_VM_NAME ]

        reg_str = ""
        if self._register: reg_str = "--register"

        super().__init__( ["VBoxManage",
            "createvm",
            "--name", self._cfg[ pyvbcc.KEY_VM_NAME ],
            "--groups", "/%s" % (  self._cfg[ pyvbcc.KEY_GROUP_NAME ] ),
            "--ostype", self._cfg[  pyvbcc.KEY_VM_OSTYPE ],
            reg_str
        ], **opt )



class DeleteVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_VM_DELETE: { "match":["True", "False"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._delete = True
        if pyvbcc.KEY_VM_DELETE in self._cfg : self._delete = self._cfg[ pyvbcc.KEY_VM_DELETE ]

        del_str = ""
        if self._delete:
            del_str = "--delete"

        super().__init__( ["VBoxManage", "unregistervm", self._cfg[ pyvbcc.KEY_VM_NAME ], del_str ], **opt )


###########################################################################################################################
## Modify VM
###########################################################################################################################
class ModifyVmCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg:
            raise AttributeError("Missing vm name")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]

        self._ostype = None
        self._group = None
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

        if pyvbcc.KEY_VM_OSTYPE in cfg: self._ostype = cfg[ pyvbcc.KEY_VM_OSTYPE ]
        if pyvbcc.KEY_VM_GROUP in cfg: self._group = cfg[ pyvbcc.KEY_VM_GROUP ]
        if pyvbcc.KEY_VM_DESCRIPTION in cfg: self._description = cfg[ pyvbcc.KEY_VM_DESCRIPTION ]
        if pyvbcc.KEY_VM_CPUS in cfg: self._cpus = cfg[ pyvbcc.KEY_VM_CPUS ]
        if pyvbcc.KEY_VM_CPU_HOTPLUG in cfg: self._cpu_hotplug = cfg[ pyvbcc.KEY_VM_CPU_HOTPLUG ]
        if pyvbcc.KEY_VM_CPUCAP in cfg: self._cpu_limit = cfg[ pyvbcc.KEY_VM_CPUCAP ]
        if pyvbcc.KEY_VM_MEMORY in cfg: self._memory = cfg[ pyvbcc.KEY_VM_MEMORY ]
        if pyvbcc.KEY_VM_VRAM in cfg: self._vram = cfg[ pyvbcc.KEY_VM_VRAM ]
        if pyvbcc.KEY_VM_AUDIO in cfg: self._audio = cfg[ pyvbcc.KEY_VM_AUDIO ]
        if pyvbcc.KEY_VM_PAE in cfg: self._pae = cfg[ pyvbcc.KEY_VM_PAE ]
        if pyvbcc.KEY_VM_ACPI in cfg: self._acpi = cfg[ pyvbcc.KEY_VM_ACPI ]
        if pyvbcc.KEY_VM_APIC in cfg: self._apic = cfg[ pyvbcc.KEY_VM_APIC ]
        if pyvbcc.KEY_VM_PAGEFUSION in cfg: self._pagefusion = cfg[ pyvbcc.KEY_VM_PAGEFUSION ]
        if pyvbcc.KEY_VM_FIRMWARE in cfg: self._firmware = cfg[ pyvbcc.KEY_VM_FIRMWARE ]
        if pyvbcc.KEY_VM_CHIPSET in cfg: self._chipset = cfg[ pyvbcc.KEY_VM_CHIPSET ]
        if pyvbcc.KEY_VM_USB in cfg: self. _usb= cfg[ pyvbcc.KEY_VM_USB ]
        if pyvbcc.KEY_VM_KEYBOARD in cfg: self._keyboard = cfg[ pyvbcc.KEY_VM_KEYBOARD ]
        if pyvbcc.KEY_VM_MOUSE in cfg: self._mouse = cfg[ pyvbcc.KEY_VM_MOUSE ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        if self._ostype: params += list( [ "--ostype", self._ostype ] )
        if self._group: params += list( [ "--groups", self._group ] )
        if self._description: params += list( [ "--description", self._description ] )
        if self._cpus: params += list( [ "--cpus", self._cpus ] )
        if self._cpu_limit: params += list( [ "--cpuexecutioncap", self._cpu_limit ] )
        if self._cpu_hotplug: params += list( [ "--cpuhotplug", self._cpu_hotplug ] )
        if self._memory: params += list( [ "--memory", self._memory ] )
        if self._vram: params += list( [ "--vram", self._vram ] )
        if self._pae: params += list( [ "--pae", self._pae ] )
        if self._acpi: params += list( [ "--acpi", self._acpi ] )
        if self._apic: params += list( [ "--apic", self._apic ] )
        if self._pagefusion: params += list( [ "--pagefusion", self._pagefusion ] )
        if self._firmware: params += list( [ "--firmware", self._firmware ] )
        if self._chipset: params += list( [ "--chipset", self._chipset ] )
        if self._usb: params += list( [ "--usb", self._usb ] )
        if self._keyboard: params += list( [ "--keyboard", self._keyboard ] )
        if self._mouse: params += list( [ "--mouse", self._mouse ] )

        super().__init__( params, **opt )



class ModifyVmBootCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_BOOT_ORDER not in cfg:
            raise AttributeError("Missing vm name or boot order index")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._boot_order = cfg[ pyvbcc.KEY_BOOT_ORDER ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )

###########################################################################################################################
## VM NIC modify
###########################################################################################################################
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

###########################################################################################################################
## NAT netwrking
###########################################################################################################################
class CreateNatNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_NETWORK_NAME not in cfg or pyvbcc.KEY_NETWORK_ADDR not in cfg or pyvbcc.KEY_NETWORK_CIDR not in cfg:
            raise AttributeError("Missing nat network name or network address or cidr")

        self._enabled = True
        self._dhcp = True
        self._ipv6 = False
        self._network = cfg[ pyvbcc.KEY_NETWORK_ADDR ]
        self._cidr = cfg[ pyvbcc.KEY_NETWORK_CIDR ]
        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = ["VBoxManage", "natnetwork", "add",
            "--netname", self._nat_name,
            "--network", "%s/%s" % (self._network, self._cidr)
        ]

        if pyvbcc.KEY_NETWORK_ENABLED in cfg: self._enabled = cfg[ pyvbcc.KEY_NETWORK_ENABLED ]
        if pyvbcc.KEY_NETWORK_IPV6 in cfg: self._ipv6 = cfg[ pyvbcc.KEY_NETWORK_IPV6 ]
        if pyvbcc.KEY_NETWORK_DHCP in cfg: self._dhcp = cfg[ pyvbcc.KEY_NETWORK_DHCP ]

        enable_str = "--enable"
        if not self._enabled:
            enable_str = "--disable"

        dhcp_str = "on"
        if not self._dhcp:
            dhcp_str = "off"

        ipv6_str = "off"
        if self._ipv6:
            ipv6_str = "on"

        if self._enabled: params += list( [ enable_str ] )
        if self._dhcp: params += list( [ "--dhcp", dhcp_str ] )
        if self._dhcp: params += list( [ "--ipv6", ipv6_str ] )

        super().__init__( params, **opt )


class ModifyNatNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_NETWORK_NAME not in cfg:
            raise AttributeError("Missing nat network name")

        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]


        self._enabled = None
        self._dhcp = None
        self._ipv6 = None
        self._network = None
        self._cidr = "24"

        params = ["VBoxManage", "natnetwork", "modify", "--netname", self._nat_name ]

        if pyvbcc.KEY_NETWORK_ENABLED in cfg: self._enabled = cfg[ pyvbcc.KEY_NETWORK_ENABLED ]
        if pyvbcc.KEY_NETWORK_IPV6 in cfg: self._ipv6 = cfg[ pyvbcc.KEY_NETWORK_IPV6 ]
        if pyvbcc.KEY_NETWORK_DHCP in cfg: self._dhcp = cfg[ pyvbcc.KEY_NETWORK_DHCP ]
        if pyvbcc.KEY_NETWORK_ADDR in cfg: self._enabled = cfg[ pyvbcc.KEY_NETWORK_ADDR ]
        if pyvbcc.KEY_NETWORK_CIDR in cfg: self._ipv6 = cfg[ pyvbcc.KEY_NETWORK_CIDR ]

        enable_str = "--enable"
        if not self._enabled: enable_str = "--disable"

        dhcp_str = "on"
        if not self._dhcp: dhcp_str = "off"

        ipv6_str = "off"
        if self._ipv6: ipv6_str = "on"

        if self._enabled: params += list( [ enable_str ] )
        if self._dhcp: params += list( [ "--dhcp", dhcp_str ] )
        if self._ipv6: params += list( [ "--ipv6", ipv6_str ] )
        if self._network: params += list( [ "--network", "%s/%s" % (self._network, self._cidr) ] )

        super().__init__( params, **opt )

class DeleteNatNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_NETWORK_NAME not in cfg:
            raise AttributeError("Missing nat network name")

        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = ["VBoxManage", "natnetwork", "remove", self._nat_name ]

        super().__init__( params, **opt )





###########################################################################################################################
## HostOnly netwrking
###########################################################################################################################
class ModifyVmHostOnlyNicCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._net_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )




###########################################################################################################################
## IntNet netwrking
###########################################################################################################################
class ModifyVmIntNetNicCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._nic_id = cfg[ pyvbcc.KEY_NIC_ID ]

        params = ["VBoxManage", "modifyvm", self._vm ]

        super().__init__( params, **opt )




if __name__ == "__main__":
    import time

    info = ListSystemPropertiesCommand().run()
    home = pyvbcc.utils.read_env("HOME")

    vm = "vm2"
    group = "test1"
    vmdir = "%s/%s/%s" % ( info["defaultmachinefolder"], group, vm )
    vmfile = "%s/%s.vmdk" % ( vmdir, vm )
    dvdfile = "%s/Downloads/CentOS-7-x86_64-NetInstall-1810.iso" % ( home )

    vm1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_GROUP_NAME: "test1", pyvbcc.KEY_VM_OSTYPE: "RedHat_64", pyvbcc.KEY_DISKS_FILE: vmfile, pyvbcc.KEY_VM_MOUSE: "ps2", pyvbcc.KEY_VM_MEMORY: "512", pyvbcc.KEY_VM_AUDIO: "null", pyvbcc.KEY_VM_USB: "off", pyvbcc.KEY_VM_CPUCAP: "50", pyvbcc.KEY_VM_CPUS:"1" }
    ctl0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_CONTROLLER_TYPE: "ide", pyvbcc.KEY_CONTROLLER_PCOUNT: "2", pyvbcc.KEY_CONTROLLER_CHIPSET: "PIIX4", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on"}
    ctl1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_CONTROLLER_TYPE: "sas", pyvbcc.KEY_CONTROLLER_CHIPSET: "LSILogicSAS", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on" }
    dks0 = { pyvbcc.KEY_DISKS_FILE: vmfile, pyvbcc.KEY_DISKS_FORMAT:"vmdk", pyvbcc.KEY_DISKS_NAME:"dm1-disk", pyvbcc.KEY_DISKS_SIZE: "4096"}
    atts0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_DISKS_FILE: vmfile }
    atts1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_DISKS_FILE: dvdfile, pyvbcc.KEY_DISKS_TYPE: "dvddrive" }

    cli = CreateVmCommand( vm1 ).run()
    cli = ModifyVmCommand( vm1 ).run()
    cli = CreateControllerCommand( ctl0 ).run()
    cli = CreateControllerCommand( ctl1 ).run()
    cli = CreateDiskCommand( dks0 ).run()
    cli = AttachDiskCommand( atts0 ).run()
    if os.path.exists( dvdfile ):
        cli = AttachDiskCommand( atts1 ).run()
    else:
        print("Install ISO %s was not found ... skipping" % ( dvdfile ) )

    time.sleep(5)
    cli = DeleteVmCommand( vm1 ).run()
    pass
