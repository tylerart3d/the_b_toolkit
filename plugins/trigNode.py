import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import math, sys

# Variables:
pluginName = 'trigNode'
version = '1.1'
creator = 'tylerART (Brent Tyler)'
mayaVersion = 'Any'
sineNodeId = om.MTypeId(0x87157)

class TrigNode(mpx.MPxNode):

    # Attributes
    input = om.MObject()
    output = om.MObject()
    type = om.MObject()
    function = om.MObject()

    def __init__(self):
        mpx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == self.output:
            inputFloat = dataBlock.inputValue(self.input).asFloat()
            functionString = dataBlock.inputValue(self.function).asShort()
            typeString = dataBlock.inputValue(self.type).asShort()
            result = 0

            if functionString == 0: result = math.sin(inputFloat)
            if functionString == 1: result = math.cos(inputFloat)
            if functionString == 2: result = math.tan(inputFloat)
            if functionString == 3: result = math.asin(inputFloat)
            if functionString == 4: result = math.acos(inputFloat)
            if functionString == 5: result = math.atan(inputFloat)
            if typeString == 0: result = math.degrees(result)

            outputHandle = dataBlock.outputValue(self.output)
            outputHandle.setFloat(result)
            dataBlock.setClean(plug)

# Initialization

def nodeCreator():
    return mpx.asMPxPtr(TrigNode())

def nodeInitializer():
    #Radians / Degree
    eAttr = om.MFnEnumAttribute()
    TrigNode.type = eAttr.create('type', 't', 1)
    eAttr.addField('Degrees', 0)
    eAttr.addField('Radians', 1)
    eAttr.setDefault(0)
    eAttr.setStorable(1)
    eAttr.setKeyable(1)

    # Function
    TrigNode.function = eAttr.create('function', 'f', 1)
    eAttr.addField('Sin', 0)
    eAttr.addField('Cos', 1)
    eAttr.addField('Tan', 2)
    eAttr.addField('aSin', 3)
    eAttr.addField('aCos', 4)
    eAttr.addField('aTan', 5)
    eAttr.setDefault(0)
    eAttr.setStorable(1)
    eAttr.setKeyable(1)

    # Input
    nAttr = om.MFnNumericAttribute()
    TrigNode.input = nAttr.create('input', 'in', om.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)

    # Output
    nAttr = om.MFnNumericAttribute()
    TrigNode.output = nAttr.create('output', 'out', om.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    # Add Attributes
    TrigNode.addAttribute(TrigNode.type)
    TrigNode.addAttribute(TrigNode.function)
    TrigNode.addAttribute(TrigNode.input)
    TrigNode.addAttribute(TrigNode.output)
    TrigNode.attributeAffects(TrigNode.input, TrigNode.output)
    TrigNode.attributeAffects(TrigNode.type, TrigNode.output)
    TrigNode.attributeAffects(TrigNode.function, TrigNode.output)

def initializePlugin(obj):
    plugin = mpx.MFnPlugin(obj, creator, version, mayaVersion)
    try:
        plugin.registerNode(pluginName, sineNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to register plugin: ' + pluginName)

def uninitializePlugin(obj):
    plugin = mpx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(sineNodeId)
    except:
        sys.stderr.write('Failed to deregister plugin: ' + pluginName)
    
