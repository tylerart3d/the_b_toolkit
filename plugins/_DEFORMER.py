# Deformer Plugin Base File

import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import sys

# Variables:
pluginName = 'baseDeformer'
version = '1.0'
creator = 'tylerART (Brent Tyler)'
mayaVersion = 'Any'
nodeId = om.MTypeId(0x87158)

class Deformer(mpx.MPxDeformerNode):

    # Node Attributes

    def __init__(self):
        mpx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, iterator, matrix, multiIndex):

        # Envelope
        envelopeAttr = mpx.cvar.MPxDeformerNode_envelope
        envelope = dataBlock.inputValue(envelopeAttr).asFloat()
        
        # Loop Through Points
        while not iterator.isDone():
            position = iterator.position()
            position.x += envelope
            position.y += envelope
            position.z += envelope
            iterator.setPosition(position)
            iterator.next()

def nodeCreator():
    return mpx.asMPxPtr(Deformer())

def nodeInitializer():
    pass
    

def initializePlugin(MObject):
    plugin = mpx.MFnPlugin(MObject, creator, version, mayaVersion)
    try:
        plugin.registerNode(pluginName, nodeId, nodeCreator, nodeInitializer, mpx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write('Failed to register plugin: ' + pluginName)

def uninitializePlugin(MObject):
    plugin = mpx.MFnPlugin(MObject)
    try:
        plugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Failed to deregister plugin: ' + pluginName)
