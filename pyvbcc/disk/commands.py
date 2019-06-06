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
## Basic controller commands
###########################################################################################################################
class CreateControllerCommand( pyvbcc.command.GenericCommand ):

    def __init__( self, cfg = {}, **opt ):
        self._cfg = cfg
        self._validmap = {
            pyvbcc.KEY_VM_NAME: { "match": ["^[a-zA-Z0-9\-\._/ ]+$"], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_TYPE: { "match": ["ide","sata","scsi","floppy","sas","usb","pcie"], "mandatory":True },
            pyvbcc.KEY_CONTROLLER_CHIPSET: { "match": [ "LSILogic","LSILogicSAS","BusLogic","IntelAHCI","PIIX3","PIIX4","ICH6","I82078","USB","NVMe"], "mandatory":True },
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
class CreateDiskCommand( pyvbcc.command.GenericCommand ):
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



class CloseDiskCommand( pyvbcc.command.GenericCommand ):
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


class AttachDiskCommand( pyvbcc.command.GenericCommand ):
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
