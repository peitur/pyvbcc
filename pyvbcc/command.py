#!/usr/bin/env python3

import os, sys, re
import subprocess, shlex
import getopt

import pyvbcc
import pyvbcc.utils
import pyvbcc.validate

from pprint import pprint
class GenericCommandResult( object ):
    def __init__( self, cmd, result, exitcode = 0, **opt ):
        self._cmd = cmd
        self._result = result
        self._exitcode = exitcode

    def exitcode( self ):
        return self._exitcode

    def command( self ):
        return self._command

    def result( self ):
        return self._result

class GenericCommand( object ):

    def __init__(self, cmd, **opt ):
        self._cmd = cmd
        self._debug = False
        self._command = "VBoxManage"


        if pyvbcc.KEY_SYSTEM_DEBUG in opt and opt[ pyvbcc.KEY_SYSTEM_DEBUG ] in (True,False):
            self._debug = opt[ pyvbcc.KEY_SYSTEM_DEBUG ]

        if pyvbcc.KEY_SYSTEM_COMMAND in opt and opt[ pyvbcc.KEY_SYSTEM_COMMAND ] in ("VBoxManage", "VBoxHeadless"):
            self._command = opt[ pyvbcc.KEY_SYSTEM_COMMAND ]


    def run( self, **opt ):
        result = list()
        cmd = self._cmd

        if type( cmd ).__name__ == "str":
            cmd = shlex.split( cmd )

        cmd = [ self._command ] + cmd

        if self._debug: print( " ".join( cmd ) )

        prc = subprocess.Popen( cmd, universal_newlines=True, stdout=subprocess.PIPE )
        for line in prc.stdout.readlines():
            result.append( line.lstrip().rstrip() )
        
        return GenericCommandResult( cmd, result, prc.returncode, **opt )


class CommonCommandLine( object ):
    def __init__( self, argv, shrt=[], lng=[], **opt ):
        self._debug = False
        self._argv = argv
        self._short = ["hDc:"]+shrt
        self._long = ["help","debug", "config="]+lng
        self._opt = dict()
        self._opts = None
        self._args = None
        self._validator = None

        if 'debug' in opt and opt['debug'] in (True, False):
            self._debug = opt['debug']

        try:
            self._opts, self._args = getopt.getopt( self._argv[1:], "".join( self._short ), self._long )
        except getopt.GetoptError as err:
            raise err

    def get( self, key ):
        if key in self._opt:
            return self._opt[ key ]
        return None

    def parse(self): pass

    def action( self ): pass


###########################################################################################################################
## Basic controller commands
###########################################################################################################################
class CreateControllerCommand( GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_TYPE: { "match": ["ide","sata","scsi","floppy","sas","usb","pcie"], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_CHIPSET: { "match": [ "LSILogic","LSILogicSAS","BusLogic","IntelAHCI","PIIX3","PIIX4","ICH6","I82078","USB","NVMe"
 ], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_NAME: { "match": [ "^[a-zA-Z0-9\-\._/ ]+$" ], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_PCOUNT: { "match": ["^[0-9]+$"] },
            pyvbcc.KEY_CONTROLLER_BOOTABLE: { "match": ["on","off"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._vm = self._cfg[ pyvbcc.KEY_VM_NAME ]
        self._type = self._cfg[ pyvbcc.KEY_CONTROLLER_TYPE ]
        self._chipset = self._cfg[ pyvbcc.KEY_CONTROLLER_CHIPSET ]
        self._name = self._cfg[ pyvbcc.KEY_CONTROLLER_NAME ]
        self._pcount = "8"
        self._bootable = "off"
        self._iocache = "on"


        if pyvbcc.KEY_CONTROLLER_PCOUNT in self._cfg:
            self._pcount = self._cfg[ pyvbcc.KEY_CONTROLLER_PCOUNT ]

        if pyvbcc.KEY_CONTROLLER_BOOTABLE in self._cfg:
            self._bootable = self._cfg[ pyvbcc.KEY_CONTROLLER_BOOTABLE ]

        super().__init__( [
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
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_DISKS_FILE: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True },
            pyvbcc.KEY_DISKS_SIZE: { "match": ["^[0-9]+$"] },
            pyvbcc.KEY_DISKS_FORMAT: {"match": [ "vdi","vmdk" ,"vhd" ] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._filename = self._cfg[ pyvbcc.KEY_DISKS_FILE ]
        self._size = self._cfg[ pyvbcc.KEY_DISKS_SIZE ]

        self._format = "vmdk"
        if pyvbcc.KEY_DISKS_FORMAT in self._cfg :
            self._format = self._cfg[ pyvbcc.KEY_DISKS_FORMAT ]

        super().__init__( [
            "createmedium", "disk",
            "--filename", self._filename,
            "--format", self._format,
            "--size", self._size
        ], **opt )



class CloseDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):

        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_DISKS_FILE: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True },
            pyvbcc.KEY_DISKS_DELETE: { "match": ["True","False"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._delete = True
        if self._cfg[ pyvbcc.KEY_DISKS_DELETE ]:
            self._delete = self._cfg[ pyvbcc.KEY_DISKS_DELETE ]

        del_str = ""
        if self._delete:
            del_str = "--delete"

        super().__init__( [
            "closemdium", "disk", self._cfg[ pyvbcc.KEY_DISKS_FILE ],
            del_str
        ], **opt )


class AttachDiskCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):

        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_DISKS_FILE: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True },
            pyvbcc.KEY_DISKS_TYPE: {"match": ["hdd","dvddrive","fdd"] },
            pyvbcc.KEY_DISKS_PORT: {"match": ["^[0-9]+$"] },
            pyvbcc.KEY_DISKS_MTYPE: {"match": ["normal","writethrough","immutable","shareable","readonly","multiattach"] },
            pyvbcc.KEY_DISKS_DEVICE: {"match": ["^[0-9]+$"] },
            pyvbcc.KEY_DISKS_COMMENT: {"match": ["^.*$"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        if pyvbcc.KEY_DISKS_PORT not in self._cfg: self._cfg[ pyvbcc.KEY_DISKS_PORT ] = "0"
        if pyvbcc.KEY_DISKS_TYPE not in self._cfg: self._cfg[ pyvbcc.KEY_DISKS_TYPE ] = "hdd"
        if pyvbcc.KEY_DISKS_DEVICE not in self._cfg: self._cfg[ pyvbcc.KEY_DISKS_DEVICE ] = "0"

        params = [
            "storageattach", self._cfg[ pyvbcc.KEY_VM_NAME ],
            "--storagectl", self._cfg[ pyvbcc.KEY_CONTROLLER_NAME ],
            "--medium", self._cfg[ pyvbcc.KEY_DISKS_FILE ]
        ]

        if pyvbcc.KEY_DISKS_TYPE in self._cfg: params += list( [ "--type", self._cfg[ pyvbcc.KEY_DISKS_TYPE ] ] )
        if pyvbcc.KEY_DISKS_PORT in self._cfg: params += list( [ "--port", self._cfg[ pyvbcc.KEY_DISKS_PORT ] ] )
        if pyvbcc.KEY_DISKS_MTYPE in self._cfg: params += list( [ "--mtype", self._cfg[ pyvbcc.KEY_DISKS_MTYPE ] ] )
        if pyvbcc.KEY_DISKS_DEVICE in self._cfg: params += list( [ "--device", self._cfg[ pyvbcc.KEY_DISKS_DEVICE ] ] )
        if pyvbcc.KEY_DISKS_COMMENT in self._cfg: params += list( [ "--comment", self._cfg[ pyvbcc.KEY_DISKS_COMMENT ] ] )

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

        params = [ "modifyvm", self._vm ]
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
        self._cidr = "24"

        self._network = cfg[ pyvbcc.KEY_NETWORK_ADDR ]
        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        if pyvbcc.KEY_NETWORK_CIDR in cfg: self._cidr = cfg[ pyvbcc.KEY_NETWORK_CIDR ]
        if pyvbcc.KEY_NETWORK_ENABLED in cfg: self._enabled = cfg[ pyvbcc.KEY_NETWORK_ENABLED ]
        if pyvbcc.KEY_NETWORK_IPV6 in cfg: self._ipv6 = cfg[ pyvbcc.KEY_NETWORK_IPV6 ]
        if pyvbcc.KEY_NETWORK_DHCP in cfg: self._dhcp = cfg[ pyvbcc.KEY_NETWORK_DHCP ]

        params = [ "natnetwork", "add",
            "--netname", self._nat_name,
            "--network", "%s/%s" % (self._network, self._cidr)
        ]

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

        params = [ "natnetwork", "modify", "--netname", self._nat_name ]

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

        params = [ "natnetwork", "remove", "--netname", self._nat_name ]

        super().__init__( params, **opt )

class StartNatNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_NETWORK_NAME not in cfg:
            raise AttributeError("Missing nat network name")

        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = [ "natnetwork", "start", "--netname", self._nat_name ]

        super().__init__( params, **opt )

class StopNatNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_NETWORK_NAME not in cfg:
            raise AttributeError("Missing nat network name")

        self._nat_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = [ "natnetwork", "stop", "--natname", self._nat_name ]

        super().__init__( params, **opt )




###########################################################################################################################
## HostOnly netwrking
###########################################################################################################################
class CreateHostOnlyNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._net_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = [ "hostonlyif","ipconfig", "create", self._vm ]

        super().__init__( params, **opt )

class DeleteHostOnlyNetworkCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_NIC_ID not in cfg:
            raise AttributeError("Missing vm name and NIC id")

        self._net_name = cfg[ pyvbcc.KEY_NETWORK_NAME ]

        params = [ "hostonlyif", "remove",self._vm ]

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

        params = [ "modifyvm", self._vm ]

        super().__init__( params, **opt )


###########################################################################################################################
## Power manage
###########################################################################################################################
class ModifyVmStartCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg:
            raise AttributeError("Missing vm name")

        self._type = "headless"
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        if pyvbcc.KEY_VM_STYPE in cfg: self._type = cfg[ pyvbcc.KEY_VM_STYPE ]
        if pyvbcc.KEY_VM_SENV in cfg: self._startenv = cfg[ pyvbcc.KEY_VM_SENV ]

        params = [ "startvm", self._vm, "--type", self._type ]

        super().__init__( params, **opt )

###########################################################################################################################
## Power manage
###########################################################################################################################
class ModifyVmPowerOffCommand( GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg:
            raise AttributeError("Missing vm name")

        self._type = "poweroff"
        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        if pyvbcc.KEY_VM_OFFTYPE in cfg and cfg[ pyvbcc.KEY_VM_OFFTYPE] in ("hard", "soft"):
            if cfg[ pyvbcc.KEY_VM_OFFTYPE] == "hard":
                self._type = "poweroff"
            elif cfg[ pyvbcc.KEY_VM_OFFTYPE] == "soft":
                self._type = "acpipowerbutton"

        params = [ "controlvm", self._vm, self._type ]

        super().__init__( params, **opt )


if __name__ == "__main__":
    import time

    info = ListSystemPropertiesCommand().run()
    home = pyvbcc.utils.read_env("HOME")

    pprint( info )

    vm = "vm2"
    group = "test1"
    vmdir = "%s/%s/%s" % ( info["defaultmachinefolder"], group, vm )
    vmfile = "%s/%s.vmdk" % ( vmdir, vm )
    dvdfile = "%s/Downloads/CentOS-7-x86_64-NetInstall-1810.iso" % ( home )

    vm1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_VM_OFFTYPE: "hard", pyvbcc.KEY_VM_STYPE: "gui" ,pyvbcc.KEY_GROUP_NAME: "test1", pyvbcc.KEY_VM_OSTYPE: "RedHat_64", pyvbcc.KEY_DISKS_FILE: vmfile, pyvbcc.KEY_VM_MOUSE: "ps2", pyvbcc.KEY_VM_MEMORY: "512", pyvbcc.KEY_VM_AUDIO: "null", pyvbcc.KEY_VM_USB: "off", pyvbcc.KEY_VM_CPUCAP: "50", pyvbcc.KEY_VM_CPUS:"1" }
    ctl0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_CONTROLLER_TYPE: "ide", pyvbcc.KEY_CONTROLLER_PCOUNT: "2", pyvbcc.KEY_CONTROLLER_CHIPSET: "PIIX4", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on"}
    ctl1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_CONTROLLER_TYPE: "sas", pyvbcc.KEY_CONTROLLER_CHIPSET: "LSILogicSAS", pyvbcc.KEY_CONTROLLER_BOOTABLE: "on" }
    dks0 = { pyvbcc.KEY_DISKS_FILE: vmfile, pyvbcc.KEY_DISKS_FORMAT:"vmdk", pyvbcc.KEY_DISKS_NAME:"dm1-disk", pyvbcc.KEY_DISKS_SIZE: "4096"}
    atts0 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "SAS", pyvbcc.KEY_DISKS_FILE: vmfile }
    atts1 = { pyvbcc.KEY_VM_NAME: vm, pyvbcc.KEY_CONTROLLER_NAME: "IDE", pyvbcc.KEY_DISKS_FILE: dvdfile, pyvbcc.KEY_DISKS_TYPE: "dvddrive" }

    nat1 = { pyvbcc.KEY_NETWORK_NAME: "nat%s" % ( vm1[pyvbcc.KEY_GROUP_NAME] ), pyvbcc.KEY_NETWORK_ADDR: "192.168.101.0", pyvbcc.KEY_NETWORK_CIDR: "24", pyvbcc.KEY_NETWORK_DHCP: True }

    cli = CreateVmCommand( vm1 ).run()
    cli = ModifyVmCommand( vm1 ).run()
    cli = CreateControllerCommand( ctl0 ).run()
    cli = CreateControllerCommand( ctl1 ).run()
    cli = CreateDiskCommand( dks0 ).run()
    cli = AttachDiskCommand( atts0 ).run()

    cli = CreateNatNetworkCommand( nat1 ).run()

    if os.path.exists( dvdfile ):
        cli = AttachDiskCommand( atts1 ).run()
    else:
        print("Install ISO %s was not found ... skipping" % ( dvdfile ) )

    cli = ModifyVmStartCommand( vm1 ).run()

    time.sleep(10)
    print("power")
    cli = ModifyVmPowerOffCommand( vm1 ).run()

    state = InfoVmCommand( vm1[pyvbcc.KEY_VM_NAME] ).run()['VMState']
    print("Waiting for shutdown %s - %s" % ( vm1[pyvbcc.KEY_VM_NAME], state ) )
    while state != "poweroff":
        print("Waiting for shutdown %s - %s" % ( vm1[pyvbcc.KEY_VM_NAME], state ) )
        state = InfoVmCommand( vm1[pyvbcc.KEY_VM_NAME] ).run()['VMState']
        time.sleep(1)

    time.sleep(5)

    cli = DeleteNatNetworkCommand( nat1 ).run()

    print("off")
    cli = DeleteVmCommand( vm1 ).run()
    pass
    