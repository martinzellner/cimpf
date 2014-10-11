#!/usr/bin/python
import sys
import PyCIM
import logging
from simulationModel import *
from cimModel import *
from solver import *

"""
    prints the usage information
"""


def print_usage():
    print "Useage:"
    print "python cimpf [CIM15 RDF file]"

"""
    run a power flow calulation for the specified CIM file
"""


def runpf(path):

    # load CIM model
    model = PyCIM.cimread(path)
    cimmodel = CIMModel(model)

    # create simulation model / do cim <-> bus/branch mapping
    simulationModel = SimulationModel(cimmodel)

    # solve the power flow
    solve(simulationModel)


def main():
    logging.basicConfig(level=logging.INFO)

    if(len(sys.argv) <= 1):
        print_usage()
    else:
        path = sys.argv[1]
        runpf(path)

main()
