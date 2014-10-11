import CIM15


class CIMModel():

    swingNodeID = ""

    def __init__(self, model):
        self.model = model
        self.swingNodeID = self.getTopologicalNodes()[0].mRID

        print "[IMPORTER] Slack Bus was set to " + self.swingNodeID

    def add(self, mRID, object):
        self.model[mRID] = object

    def getObjectWithMRID(self, mRID):
        return self.model[mRID]

    def getAllObjects(self):
        return self.model.itervalues()

    def getAllObjectsWithClass(self, objectclass):
        objects = []
        for item in self.model.itervalues():
            if(item.__class__ == objectclass):
                objects.append(item)

        return objects

    def getTopologicalNodes(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Topology.TopologicalNode)

    def getConnectivityNodes(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Core.ConnectivityNode)

    def getLines(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Wires.ACLineSegment)

    def getLoads(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Wires.EnergyConsumer)

    def getSources(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Wires.EnergySource)

    def getTransformers(self):
        return self.getAllObjectsWithClass(CIM15.IEC61970.Wires.PowerTransformer)

    def getSWINGNode(self):
        return self.model[self.swingNodeID]

    def setSWINGNode(self, mRID):
        self.swingNodeID == mRID
