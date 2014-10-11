from numpy import *
import CIM15


class SimulationModel:

    """
        This class contains the bus/branch representation of the CIM model
    """

    def __init__(self, cimmodel):
        """
        create a simulation model from the given CIM mode_equivalents

        Args:
            cimmodel: the CIM model the simulation model should be generated from
        """

        print "Creating SimulationModel..."

        # the CIM model
        self.model = cimmodel

        # number of busses and branches
        self.numberOfBusses = len(self.model.getTopologicalNodes())
        self.numberOfBranches = len(self.model.getLines())

        print "... with " + str(self.numberOfBusses) + " busses and " + str(self.numberOfBranches) + " branches."

        self.initVariables(self.numberOfBusses, self.numberOfBranches)
        self.mapNodes()
        self.createLines()
        self.createLoads()
        self.createGenerators()
        self.createBusVoltages()
        self.createTransformers()
        self.evalBusTypes()

        print "Created  a simulation model with " + str(self.numberOfBusses) + " busses."

    def initVariables(self, numberOfBusses, numberOfBranches):
        """
            initialized all necessary variables for the bus/branch mode_equivalents

            args:
                numberOfBusses: how many busses we have in the model
                numberOfBranches: how many branches we have in the model
        """

        # maps for mapping the busses and branches
        self.nodeNumberMap = dict()
        self.numberNodeMap = dict()
        self.lineNumberMap = dict()
        self.numberLineMap = dict()

        #
        self.lineFrom = dict()
        self.lineTo = dict()
        self.lineSet = []

        # bus types
        self.pqNodeIds = []
        self.pvNodeIds = []

        # initialize variables for the admittance matrix, the load and
        # generation vector and the voltage vector
        self.y = zeros(
            (self.numberOfBusses, self.numberOfBusses), dtype=complex)
        self.y_from = zeros(
            (self.numberOfBusses, self.numberOfBusses), dtype=complex)
        self.y_to = zeros(
            (self.numberOfBusses, self.numberOfBusses), dtype=complex)
        self.s_d = zeros(self.numberOfBusses, dtype=complex)
        self.s_g = zeros(self.numberOfBusses, dtype=complex)
        self.v = zeros(self.numberOfBusses, dtype=complex)

    def mapNodes(self):
        """
            map the topological nodes form the CIM model to the busses of the simulation model
        """
        i = 0
        for node in self.model.getTopologicalNodes():
            # bidirectional mapping
            self.numberNodeMap[i] = node
            self.nodeNumberMap[node] = i
            i = i + 1

        print "[MAPPING]" + str(i) + " busses have been successfully mapped to the simulation model."

    def createLines(self):
        """
            process through the ac line segment objects in the CIM model and enter the line data into the admittance matrix y
        """

        index = 0
        # line index
        for line in self.model.getLines():

            # indentify the bus numbers the line connects to
            fromBus = self.nodeNumberMap[
                line.getTerminals()[0].getTopologicalNode()]
            toBus = self.nodeNumberMap[
                line.getTerminals()[1].getTopologicalNode()]

            # map line
            self.lineNumberMap[line] = index
            self.numberLineMap[index] = line

            # line connection set
            self.lineFrom[index] = fromBus
            self.lineTo[index] = toBus
            self.lineSet.append(index)

            # calculate line properties
            r = line.r
            x = line.x
            g = line.gch
            b = line.bch
            ys = 1.0 / complex(r, x)
            bc = complex(g, b)

            # modify admittance matrix
            self.y[fromBus, fromBus] += bc / 2 + ys
            self.y[fromBus, toBus] += - ys
            self.y[toBus, fromBus] += - ys
            self.y[toBus, toBus] += (bc / 2) + ys

            # add matrix elements to y_from matrix
            self.y_from[index, fromBus] += ys + bc / 2
            self.y_from[index, toBus] += - ys

            # add matrix elements to y_to matrix
            self.y_to[index, fromBus] += ys + bc / 2
            self.y_to[index, toBus] += - ys

            print "[MAPPING] Added line " + str(index) + " with y_s= " + str(ys) + " b_c=" + str(bc)
            index += 1

        print "[MAPPING] Calculated admittance matrix"

    def createLoads(self):
        """
            creates the demand vector S_d from the EnergyConsumer objects in the CIM model
        """
        for load in self.model.getLoads():
            nodeId = self.nodeNumberMap[
                load.getTerminals()[0].getTopologicalNode()]
            self.s_d[nodeId] = complex(load.pfixed, load.qfixed)
        print "[MAPPING] Calculated demand vector S_d = " + str(self.s_d)

    def createGenerators(self):
        """
            creates the generation vector S_g from the EnergySource objects in the CIM model
        """
        for source in self.model.getSources():
            nodeId = self.nodeNumberMap[
                source.getTerminals()[0].getTopologicalNode()]
            self.s_g[nodeId] = complex(source.activePower, 0.0)

        print "[MAPPING] Calculated demand vector S_g = " + str(self.s_g)

    def createBusVoltages(self):
        """
            creates the starting voltage vector from the base voltages of the nodes
        """
        for node in self.model.getTopologicalNodes():
            self.v[self.nodeNumberMap.get(node)] = complex(
                node.getBaseVoltage().nominalVoltage, 0.0)

        print "[MAPPING] Calculated start voltage vector V = " + str(self.v)

    def createTransformers(self):
        """
            TBD
        """
        pass

    def evalBusTypes(self):
        """
            classifies the different nodes into PV and PQ busses depending on which equipment is connected.
        """
        self.swingNodeId = self.nodeNumberMap[self.model.getSWINGNode()]

        for node in self.model.getTopologicalNodes():
            # if node is connected to at least one load, treat it as a PQ node
            isSet = False
            for terminal in node.getTerminal():
                if terminal.getConductingEquipment().__class__ == CIM15.IEC61970.Wires.EnergyConsumer:
                    self.pqNodeIds.append(self.nodeNumberMap[node])
                    isSet = True
                    print "[MAPPING] Treating bus " + str(self.nodeNumberMap[node]) + " as a PQ Bus"
                    break

            if (isSet == False and not node == self.model.getSWINGNode()):
                self.pvNodeIds.append(self.nodeNumberMap[node])
                print "[MAPPING] Treating bus " + str(self.nodeNumberMap[node]) + " as a PV Bus"
