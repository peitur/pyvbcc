#!/usr/bin/env python3

import os, sys, re
import json
import hashlib
from pprint import pprint

from pathlib import Path


################################################################################
## Hashing large files
################################################################################
def data_hash( buffer, **opt ):

    chksum = "md5"
    if 'checksum' in opt:
        chksum = opt['checksum']

    if chksum in ("md5", "sha1", "sha224", "sha256", "sha384","sha512"):
        if chksum == "md5":
            hasher = hashlib.md5()
        elif chksum == "sha1":
            hasher = hashlib.sha1()
        elif chksum == "sha224":
            hasher = hashlib.sha224()
        elif chksum == "sha256":
            hasher = hashlib.sha256()
        elif chksum == "sha384":
            hasher = hashlib.sha384()
        elif chksum == "sha512":
            hasher = hashlib.sha512()

#        print( type(buffer ) )
        try:
            hasher.update( buffer.encode('utf-8', "ignore") )
            return hasher.hexdigest()
        except Exception as e:
            print_exception(e)

    raise RuntimeError( "Unknown hash function %s" % ( chksum ) )


################################################################################
## Hashing large files
################################################################################
def file_hash( filename, chksum="sha256" ):
    BLOCKSIZE = 65536

    if chksum == "sha1":
        hasher = hashlib.sha1()
    elif chksum == "sha224":
        hasher = hashlib.sha224()
    elif chksum == "sha256":
        hasher = hashlib.sha256()
    elif chksum == "sha384":
        hasher = hashlib.sha384()
    elif chksum == "sha512":
        hasher = hashlib.sha512()
    else:
        hasher = hashlib.sha256()

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


################################################################################
## Local file operaitons
################################################################################

def _read_text( filename ):
    result = list()
    try:
        fd = open( filename, "r" )
        for line in fd.readlines():
            result.append( line.lstrip().rstrip() )
        return result
    except Exception as e:
        print("ERROR Reading %s: %s" % ( filename, e ))

    return result

def _read_json( filename ):
    return json.loads( "\n".join( _read_text( filename ) ) )

def load_file( filename ):
    filesplit = re.split( r"\.", filename )
    if filesplit[-1] in ( "json" ):
        return _read_json( filename )
    else:
        return _read_text( filename )


def _write_json( filename, data ):
    return _write_text( filename, json.dumps( data, indent=2, sort_keys=True ) )

def _write_text( filename, data ):
    fd = open( filename, "w" )
    fd.write( str( data ) )
    fd.close()

def write_file( filename, data ):
    filesplit = re.split( "\.", filename )
    if filesplit[-1] in ( "json" ):
        return _write_json( filename, data )
    else:
        return _write_text( filename, data )

def file_is_json( filename ):
    filesplit = re.split( r"\.", filename )
    if filesplit[-1] in ( "json" ):
        return True
    return False

################################################################################

def read_tree( path, rx=r".*" ):
    result = list()
    for f in os.listdir( path ):
        p = "%s/%s" % ( path, f )
        if os.path.isdir( p ):
            result += read_tree( p, rx )
        else:
            if re.search( rx, f ):
                result.append( p )
    return result

################################################################################


def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )

################################################################################



if __name__ == "__main__":
    pass
