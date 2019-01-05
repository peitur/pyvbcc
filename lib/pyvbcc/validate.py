 #!/usr/bin/env python3

import os, sys, re
import json
import getopt

from pprint import pprint

import pyvbcc
import pyvbcc.config


class Validator( object ):

    def __init__( self, valmap, **opt ):
        if 'debug' in opt and opt['debug'] in (True, False):
            self._debug = opt['debug']

        if not type( valmap ).__name__ == "dict":
            raise AttributeError( "Bad validator map given. Must be dict.")

        self._strict = True
        if "strict" in opt and opt["strict"] in (True,False):
            self._strict = opt["strict"]

        self._map = valmap
        self._mandatory = [ k for k in self._map if 'mandatory' in self._map[k] and self._map[k]['mandatory'] == True ]


    def get_mandatory( self ):
        return self._mandatory


    def _matches( self, rxtype, key, data, **opt ):
        matches = 0
        patterns = self._map[key][ rxtype ]
        
        for p in patterns:
            if rxtype == "match":
                if re.match( p, data ): matches += 1
            if rxtype == "search":
                if re.search( p, data ): matches += 1
        return matches

    def _all_pattern( self, rxtype, key, data, **opt ):
        expmatches = len( self._map[key][ rxtype ] )
        matches = self._matches( rxtype, key, data )
        if expmatches == matches:
            return True
        return False

    def _any_pattern( self, rxtype, key, data, **opt ):
        matches = self._matches( rxtype, key, data )
        if matches > 0:
            return True
        return False


    def validate( self, valdata, **opt ):
        results = dict()
        if not type( valdata ).__name__ == "dict": raise AttributeError( "Validate input must be of type dict.")

        for m in self._mandatory:
            if m not in valdata: raise AttributeError("Missing mandatory key %s" % ( m ) )

        for v in valdata:
            if self._strict and v not in self._map: raise AttributeError( "Input key %s not in validator map" % ( v ) )

            rxtype = None
            if v in self._map:
                if 'search' in self._map[ v ]: rxtype = "search"
                if 'match' in self._map[ v ]: rxtype = "match"

            if v in self._map:
                if 'match_all' in self._map[ v ] and self._map[ v ]['match_all'] == True:
                    results[v] = self._all_pattern( rxtype, v, valdata[v] )
                else:
                    results[v] = self._any_pattern( rxtype, v, valdata[v] )

        falses = [ x for x in results if results[x] == False ]
        if len( falses ) > 0 :
            raise RuntimeError( "Validation failed for keys: %s" % ( ",".join( falses )) )
        return True



if __name__ == "__main__":
    pass
