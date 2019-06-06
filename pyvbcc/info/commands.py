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



class ListDiskCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, vm = None, **opt ):
        super().__init__( [ "list", "hdds", "--long" ], **opt )
        self._vm = vm

    def run( self ):
        data = dict()
        res = super().run().result()
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

class ListSystemPropertiesCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, vm = None, **opt ):
        super().__init__( [ "list", "systemproperties", "--long" ], **opt )
        self._vm = vm

    def run( self ):
        data = dict()
        res = super().run().result()
        for line in res:
            line = re.compile( "\"" ).sub(  "", line )
            nldata = re.split(r":", line )

            if len( nldata ) > 1:
                key = re.sub( r"\s+", "", nldata[0].lstrip().rstrip().lower() )
                val = nldata[1].lstrip().rstrip()
                data[ key ] = val

        return data


class ListGroupCommand( pyvbcc.command.GenericCommand ):
    def __init__( self, group, **opt ):
        super().__init__( [ "list", "groups", "--long" ], **opt )
        self._group = group

    def run( self ):
        data = dict()
        res = super().run().result()

        for line in res:
            line = re.compile( r"\"" ).sub(  "", line )
            linex = re.compile( r"\/" ).sub(  "", line )
            if len( linex ) == 0:
                linex = "default"
            data[linex] = { "name": linex, "path": line }

        if self._group == "all":
            return data

        return [ data[x] for x in data if x == self._group ]


if __name__ == "__main__":
    pass