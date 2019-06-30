import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import math, sys

# Variables:
pluginName = 'raycastNode'
version = '1.1'
creator = 'tylerART (Brent Tyler)'
mayaVersion = 'Any'
nodeId = om.MTypeId(0x87157)

class Node(mpx.MPxNode):

    # Node Attributes
    origin = om.MObject()
    direction = om.MObject()
    target = om.MObject()
    output = om.MObject()

    def __init__(self):
        mpx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == self.output:
            originX = dataBlock.inputValue(
            originY = 

def nodeCreator():
    return mpx.asMPxPtr(Node())

def nodeInitializer():

    # Origin Attribute
    nAttr = om.MFnNumericAttribute()
    Node.originX = nAttr.create('originX', 'oX', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    Node.originY = nAttr.create('originY', 'oY', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    Node.originZ = nAttr.create('originZ', 'oZ', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    cAttr = om.MFnCompoundAttribute()
    Node.origin = cAttr.create('origin', 'o')
    cAttr.setChild(Node.originX)
    cAttr.setChild(Node.originY)
    cAttr.setChild(Node.originZ)

    # Direction Attribute
    nAttr = om.MFnNumericAttribute()
    Node.directionX = nAttr.create('directionX', 'dX', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    Node.directionY = nAttr.create('directionY', 'dY', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    Node.directionZ = nAttr.create('directionZ', 'dZ', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    cAttr = om.MFnCompoundAttribute()
    Node.direction = cAttr.create('direction', 'd')
    cAttr.setChild(Node.directionX)
    cAttr.setChild(Node.directionY)
    cAttr.setChild(Node.directionZ)

    # Target Attribute
    gAttr = om.GenericAttribute()
    Node.target = gAttr.create('target', 't')
    gAttr.addDataAccept(om.MfnData.kMesh)
    gAttr.setArray(1)

    # Output Attributes
    nAttr = om.MFnNumericAttribute()
    Node.outputX =nAttr.create('outputX', 'outX', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    Node.outputY =nAttr.create('outputY', 'outY', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    Node.outputZ =nAttr.create('outputZ', 'outZ', om.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cAttr.om.MFnCompoundAttribute()
    Node.output = cAttr.create('output', 'out')
    cAttr.setChild(Node.outputX)
    cAttr.setChild(Node.outputY)
    cAttr.setChild(Node.outputZ)

    # Add Attributes
    Node.addAttribute(Node.origin)
    Node.addAttribute(Node.direction)
    Node.addAttribute(Node.target)
    Node.addAttribute(Node.output)

    # Attribute Affects
    Node.attributeAffects(Node.origin, Node.output)
    Node.attributeAffects(Node.direction, Node.output)
    Node.attributeAffects(Node.targe, Node.output)

    
def initializePlugin(obj):
    plugin = mpx.MFnPlugin(obj, creator, version, mayaVersion)
    try:
        plugin.registerNode(pluginName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to register plugin: ' + pluginName)

def uninitializePlugin(obj):
    plugin = mpx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Failed to deregister plugin: ' + pluginName)
    
