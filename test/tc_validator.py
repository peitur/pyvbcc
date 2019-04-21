#!/usr/bin/env python3

import os, sys, re
import unittest

import pyvbcc.validate

class TestValidator( unittest.TestCase ):

    def setUp( self ):
        self._map = {
            "alfan": { "match": ["([a-zA-Z0-9]+)"], "mandatory": True },
            "alfa1": { "match": "([a-zA-Z0-9]+)", "mandatory": True },
            "num1": { "match": ["([0-9]+)"], "mandatory": False },
            "bool1": { "match": ["True","False"], "mandatory": False },
            "bool2": { "match": ["True","False"], "mandatory": False },
        }

        self._ok_data  = { "alfan": "abc123", "alfa1": "123" }
        self._ok_datax  = { "alfan": "abc123", "alfa1": "123", "num1": 123, "bool1": "True", "bool2": True }
        self._nok_data = {}


    def test_valid_values_match_strict_ok( self ):
        self.assertTrue( pyvbcc.validate.Validator( self._map, strict=True ).validate( self._ok_data ) )

    def test_valid_values_match_unstrict_ok( self ):
        self.assertTrue( pyvbcc.validate.Validator( self._map, strict=False ).validate( self._ok_datax ) )

    def test_valid_values_match_strict_ok2( self ):
        self.assertTrue( pyvbcc.validate.Validator( self._map, strict=True ).validate( self._ok_datax ) )

    def test_valid_values_match_unstrict_ok2( self ):
        self.assertTrue( pyvbcc.validate.Validator( self._map, strict=False ).validate( self._ok_datax ) )

if __name__ == "__main__":
    unittest.main( verbosity=2 )
