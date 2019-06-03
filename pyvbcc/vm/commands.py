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

###########################################################################################################################
## VM listing
###########################################################################################################################

class ListVmsCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, **opt ):
        super().__init__( [ "list", "vms", "--sorted"], **opt )

    def run( self ):
        data = dict()
        res = super().run().result()
        for r in res:
            m = re.match(r"\"(.+)\"\s+{(.+)}", r )
            if m.group(1) != "<inaccessible>":
                data[ m.group(1) ] = m.group(2)
        return data

class InfoVmCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, vm, **opt ):
        super().__init__( [ "showvminfo", "--machinereadable",vm ], **opt )

    def run( self ):
        data = dict()
        res = super().run().result()

        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r"=", line )
            data[ nldata[0] ] = nldata[1]
        return data


###########################################################################################################################
## VM basic management
###########################################################################################################################
class RegisterVmCommand( pyvbcc.command.GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_DISKS_FILE: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        if not os.path.exists( self._cfg[ pyvbcc.KEY_DISKS_FILE ] ):
            raise RuntimeError("Missing VM disk in registration")

        super().__init__( [
            "registervm", self._cfg[ pyvbcc.KEY_DISKS_FILE ]
        ], **opt )

class CreateVmCommand( pyvbcc.command.GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._ ]+$"], "mandatory":True },
            pyvbcc.KEY_VM_OSTYPE: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_GROUP_NAME: { "match": ["^[a-zA-Z0-9\-\._]+$"], "mandatory":True },
            pyvbcc.KEY_VM_REGISTER: { "match":["True", "False"] }
        }

        opt["strict"] = False
        pyvbcc.validate.Validator( self._validmap, **opt ).validate( self._cfg )

        self._register = True
        if pyvbcc.KEY_VM_REGISTER in self._cfg:
            self._register = self._cfg[ pyvbcc.KEY_VM_NAME ]

        reg_str = ""
        if self._register: reg_str = "--register"

        super().__init__( [
            "createvm",
            "--name", self._cfg[ pyvbcc.KEY_VM_NAME ],
            "--groups", "/%s" % (  self._cfg[ pyvbcc.KEY_GROUP_NAME ] ),
            "--ostype", self._cfg[  pyvbcc.KEY_VM_OSTYPE ],
            reg_str
        ], **opt )



class DeleteVmCommand( pyvbcc.command.GenericCommand ):

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

        super().__init__( [ "unregistervm", self._cfg[ pyvbcc.KEY_VM_NAME ], del_str ], **opt )


###########################################################################################################################
## Modify VM
###########################################################################################################################
class ModifyVmCommand( pyvbcc.command.GenericCommand ):

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

        params = [ "modifyvm", self._vm ]

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



class ModifyVmBootCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, cfg = {}, **opt ):
        if pyvbcc.KEY_VM_NAME not in cfg or pyvbcc.KEY_BOOT_ORDER not in cfg:
            raise AttributeError("Missing vm name or boot order index")

        self._vm = cfg[ pyvbcc.KEY_VM_NAME ]
        self._boot_order = cfg[ pyvbcc.KEY_BOOT_ORDER ]

        params = [ "modifyvm", self._vm ]

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

