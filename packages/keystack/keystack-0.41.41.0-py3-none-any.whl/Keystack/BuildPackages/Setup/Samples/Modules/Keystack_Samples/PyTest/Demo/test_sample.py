"""
PyTest sample to show how to use PyTest fixtures to connect to IxNetwork API server,
run traffic and get stats.

This sample script requires passing in a config file on the CLI.

Requirements:
    - ConfigFiles/qaSetup.yml
    - BGP folder with bgp.py script

Usage:
   pytest -v -s -x --configFile ConfigFiles/qaSetup.yml BGP

"""
import sys, os, traceback
import pytest


class Sample(): 
    def test_setup_ixia(self):
        """
        Simple sample
        """
        # IxNetwork config params are passed into this script from pytest fixtures middleware
        print('\n--- pytest: Demo: sample.py ----')
        pytest.fail('pytest script failed message')


