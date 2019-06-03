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
