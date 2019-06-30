'''
------------------------------------------------------------
Name: bt_fracture.py
(copyright 2014 Brent Tyler, all rights reserved)
Author: Brent Tyler (tylerART)
Email: brent@tylerart.com
Web: http://tylerart.com

Description:
Creates fractured geometry.

History:
    09.11.2013    0.01    Script Creation
    09.13.2013    0.06    Switch to plane cutting
    10.21.2013    0.12    OOP Design
    12.07.2013    0.19    Created UI, Script Functional
    12.07.2013    0.21    Clean up script
    12.07.2013    0.22    Added Crack Type Fracture
    04.27.2014    0.23    Conversion to API 2.0 Started
    05.09.2014    0.24    Disable Unconnected Tools

Misc Ideas:
    Break Around Current Edges

    Boolean Crack Fractures, then recombine negative crack width
    pieces, bool from original to get just fractured edge pieces.


    Solve Boolean Problems
------------------------------------------------------------
'''

# Maya
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

# General
import sys
import time
import random
import math

# PySide
from PySide import QtCore
from PySide import QtGui
from shiboken import wrapInstance


class Vector():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '(%s, %s, %s)' % (self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        if isinstance(other, float):
            return Vector(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, Vector):
            return Vector(self.x - other, self.y - other, self.z - other)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def dot(self, vector):
        return (self.x * vector.x) + (self.y * vector.y) + (self.z * vector.z)

    def cross(self, other):
        return Vector((self.y * other.z - self.z * other.y), (self.z * other.x - self.x * other.z),
                      (self.x * other.y - self.y * other.x))

    def scalar(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def normalize(self):
        return Vector(self.x / self.length(), self.y / self.length(), self.z / self.length())

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vector(self.x * other, self.y * other, self.z * other)

    def __div__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    def length(self):
        return math.sqrt(self.dot(self))

    def angleBetween(self, other, deg=True):
        if deg:
            return math.degrees(math.acos((self.dot(other) / (self.length() * other.length()))))
        else:
            return math.acos((self.dot(other) / (self.length() * other.length())))


class ProgressBar(QtGui.QDialog):
    def __init__(self, name, steps):
        # Variables
        self.stop = 0

        # UI
        parent = wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget)

        QtGui.QDialog.__init__(self, parent)

        self.name = name
        self.steps = steps
        self.setWindowTitle(self.name)
        self.setFixedSize(420, 30)

        self.barWidget = QtGui.QProgressBar(self)
        self.barWidget.setGeometry(0, 0, 350, 30)
        self.barWidget.setMaximum(steps + 1)

        self.cancelButton = QtGui.QPushButton('Cancel', self)
        self.cancelButton.setGeometry(350, 0, 70, 30)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)

        self.stepCount = 0
        self.step()
        self.show()

    def step(self):
        self.barWidget.setValue(self.stepCount)
        self.stepCount += 1

    def reset(self):
        self.barWidget.reset()

    def close(self):
        self.hide()

    def cancel(self):
        self.stop = 1


class Point(Vector):
    def __init__(self, x, y, z):
        Vector.__init__(self, x, y, z)

    def __str__(self):
        return '<<%s, %s, %s>>' % (self.x, self.y, self.z)

    def insideMesh(self, mesh):
        om.MGlobal.clearSelectionList()
        om.MGlobal.selectByName(mesh.name)
        selected = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selected)

        item = om.MDagPath()
        selected.getDagPath(0, item)
        item.extendToShape()

        fnMesh = om.MFnMesh(item)

        raySource = om.MFloatPoint(self.x, self.y, self.z, 1.0)
        rayDir = om.MFloatVector(1, 0, 0)
        hitstartingPoss = om.MFloatPointArray()
        hitRayParams = om.MFloatArray()
        hitFaces = om.MIntArray()

        fnMesh.allIntersections(raySource, rayDir, None, None, False, om.MSpace.kWorld, 999999, False, None, True,
                                hitstartingPoss, hitRayParams, hitFaces, None, None, None, 0.0001)
        om.MGlobal.clearSelectionList()

        return int(math.fmod(len(hitFaces), 2))

    def raycast(self, vector, mesh):
        om.MGlobal.clearSelectionList()
        om.MGlobal.selectByName(mesh.name)
        selected = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selected)

        item = om.MDagPath()
        selected.getDagPath(0, item)
        item.extendToShape()

        fnMesh = om.MFnMesh(item)

        raySource = om.MFloatPoint(self.x, self.y, self.z, 1.0)
        rayDir = om.MFloatVector(vector.x, vector.y, vector.z)
        hitstartingPoss = om.MFloatPointArray()
        hitRayParams = om.MFloatArray()
        hitFaces = om.MIntArray()

        hit = fnMesh.allIntersections(raySource, rayDir, None, None, False, om.MSpace.kWorld, 999999, True, None, True,
                                      hitstartingPoss, hitRayParams, hitFaces, None, None, None, 0.0001)
        om.MGlobal.clearSelectionList()

        return hit


class Mesh(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def woodScale(self, axis, inverse=0):
        if inverse:
            if axis == 'x': cmds.xform(self.name, ws=1, r=1, s=[10, 1, 1])
            if axis == 'y': cmds.xform(self.name, ws=1, r=1, s=[1, 10, 1])
            if axis == 'z': cmds.xform(self.name, ws=1, r=1, s=[1, 1, 10])
        else:
            if axis == 'x': cmds.xform(self.name, ws=1, r=1, s=[0.1, 1, 1])
            if axis == 'y': cmds.xform(self.name, ws=1, r=1, s=[1, 0.1, 1])
            if axis == 'z': cmds.xform(self.name, ws=1, r=1, s=[1, 1, 0.1])

    def getBounds(self):
        bbox = cmds.xform(self.name, q=1, ws=1, bb=1)
        lowerBounds = Vector(bbox[0], bbox[1], bbox[2])
        upperBounds = Vector(bbox[3], bbox[4], bbox[5])
        return lowerBounds, upperBounds

    def duplicate(self, name):
        return Mesh(cmds.duplicate(self.name, n=name)[0])

    def rename(self, name):
        cmds.rename(self.name, name)
        self.name = name

    def boolean(self, boolMesh, name, copy=1):
        if copy:
            sourceMesh = Mesh(self.duplicate(self.name + '_fracturing'))
        else:
            sourceMesh = self

        if cmds.about(version=1) > 2013:
            try:
                # New Booleans
                newMesh = Mesh(cmds.polyCBoolOp(boolMesh.name, sourceMesh.name, op=3, ch=0, n=name)[0])
            except:
                # Old Booleans
                newMesh = Mesh(cmds.polyBoolOp(boolMesh.name, sourceMesh.name, op=3, ch=0, n=name)[0])

        cmds.xform(newMesh.name, cp=1)
        return newMesh

    def trimFaces(self, pointA, pointB, crackWidth, cutFaces):
        vectorAB = pointB - pointA
        distance = math.sqrt((vectorAB.z ** 2) + (vectorAB.x ** 2))
        rotateX = math.degrees(math.atan(vectorAB.y / distance))
        rotateY = 90 - math.degrees(math.atan(vectorAB.z / vectorAB.x))
        if vectorAB.x > 0: rotateY += 180
        midpoint = ((pointB + pointA) / 2) + ((pointB - pointA).normalize() * crackWidth * -1)

        # Cut Faces
        if cutFaces:
            cmds.polyCut(self.name, df=1, pc=[midpoint.x, midpoint.y, midpoint.z], ro=[rotateX, rotateY, 0], ch=0)
            cmds.select(cl=1)
            cmds.polyCloseBorder(self.name, ch=0)
            cmds.select(cl=1)
            return self

        # Boolean
        else:
            pass

    def createBoundingCube(self, buf=1.01):
        lowerBounds, upperBounds = self.getBounds()
        center = (lowerBounds + upperBounds) / 2
        dimentions = (upperBounds - lowerBounds) * buf
        cube = cmds.polyCube(ch=0, h=dimentions.y, w=dimentions.x, d=dimentions.z, n=self.name + '_boundingCube')[0]
        cmds.xform(cube, ws=1, a=1, t=[center.x, center.y, center.z])
        pivot = cmds.xform(self.name, q=1, ws=1, sp=1)
        cmds.xform(cube, ws=1, a=1, sp=pivot)
        return Mesh(cube)

    def offsetUV(self, uv):
        cmds.polyEditUV(self.name + '.f[*]', u=uv[0] - 1, v=uv[1] - 1)

    def hide(self):
        cmds.hide(self.name)

    def wireframe(self, switch):
        if switch:
            cmds.setAttr(self.name + '.overrideEnabled', 1)
            cmds.setAttr(self.name + '.overrideDisplayType', 1)

        else:
            cmds.setAttr(self.name + '.overrideEnabled', 0)
            cmds.setAttr(self.name + '.overrideDisplayType', 0)

    def deleteShape(self):
        cmds.delete(cmds.listRelatives(self.name, s=1)[0])

    def pointsUniform(self, count, falloffDistance, falloffSharpness, seed=0, loc=0):
        # Variables
        breakCount = 0
        lowerBounds, upperBounds = self.getBounds()
        pivot = cmds.xform(self.name, q=1, rp=1, ws=1)
        points = []
        i = 0
        if seed: random.seed(1)

        # Create Progress Bar
        progress = ProgressBar('Creating Points', count)

        # Generate Points
        while i < count:
            if falloffDistance == 0:
                x = random.uniform(lowerBounds.x, upperBounds.x)
                y = random.uniform(lowerBounds.y, upperBounds.y)
                z = random.uniform(lowerBounds.z, upperBounds.z)
            if falloffDistance > 0 and i < count / falloffSharpness:
                x = random.uniform(lowerBounds.x, upperBounds.x)
                y = random.uniform(lowerBounds.y, upperBounds.y)
                z = random.uniform(lowerBounds.z, upperBounds.z)
            if falloffDistance > 0 and i >= count / falloffSharpness:
                x = random.gauss(pivot[0], falloffDistance)
                y = random.gauss(pivot[1], falloffDistance)
                z = random.gauss(pivot[2], falloffDistance)

            point = Point(x, y, z)

            # Check Point Inside Mesh
            if point.insideMesh(self):
                points.append(point)
                progress.step()
                i += 1
                if loc: cmds.xform(cmds.spaceLocator(), ws=1, a=1, t=[x, y, z])

            if breakCount > 100000: break
            breakCount += 1

        progress.close()
        return points

    def pointsIrregular(self, count, falloffDistance, initialPointCount, falloffSharpness, seed=0, loc=0):
        # Variables
        breakCount = 0
        lowerBounds, upperBounds = self.getBounds()
        initialPoints = []
        points = []
        if seed:
            random.seed(1)
        else:
            random.seed(random.uniform(0, 10000000))

        # Create Progress Bar
        progress = ProgressBar('Creating Points', count)

        # Generate Initial Points
        i = 0
        while i < initialPointCount:
            x = random.uniform(lowerBounds.x, upperBounds.x)
            y = random.uniform(lowerBounds.y, upperBounds.y)
            z = random.uniform(lowerBounds.z, upperBounds.z)

            if Point(x, y, z).insideMesh(self):
                initialPoints.append(Point(x, y, z))
                i += 1

            if breakCount > 100000: break
            breakCount += 1

        # Generate Points
        i = 0
        while i < count:
            if falloffDistance > 0 and i < count / falloffSharpness:
                x = random.uniform(lowerBounds.x, upperBounds.x)
                y = random.uniform(lowerBounds.y, upperBounds.y)
                z = random.uniform(lowerBounds.z, upperBounds.z)
            if falloffDistance > 0 and i >= count / falloffSharpness:
                rand = int(random.uniform(0, initialPointCount))
                x = random.gauss(initialPoints[rand].x, falloffDistance)
                y = random.gauss(initialPoints[rand].y, falloffDistance)
                z = random.gauss(initialPoints[rand].z, falloffDistance)

            point = Point(x, y, z)

            # Check Point Inside Mesh
            if point.insideMesh(self):
                points.append(point)
                progress.step()
                i += 1
                if loc: cmds.xform(cmds.spaceLocator(), ws=1, a=1, t=[x, y, z])

            if breakCount > 100000: break
            breakCount += 1

        progress.close()
        return points

    def pointsCracks(self, countPerEdge, falloffDistance, uv, seed=0, loc=0):
        # Variables
        breakCount = 0
        points = []
        uvPoints = []
        if seed: random.seed(1)
        print countPerEdge, falloffDistance, uv
        # Create Progress Bar
        progress = ProgressBar('Creating Points', countPerEdge)

        # Loop Through UVs
        for i in range(cmds.polyEvaluate(self, uv=1)):
            uvc = self.name + '.map[' + str(i) + ']'
            currentUV = cmds.polyEditUV(uvc, q=1, u=1, v=1)
            if int(currentUV[0]) == uv[0] - 1 and int(currentUV[1]) == uv[1] - 1:
                uvPoints.append(uvc)

        vertices = cmds.ls(cmds.polyListComponentConversion(tv=1), fl=1)
        for vertex in vertices:
            i = 0
            while i < countPerEdge:
                pos = cmds.xform(vertex, q=1, ws=1, t=1)
                x = random.gauss(pos[0], falloffDistance)
                y = random.gauss(pos[1], falloffDistance)
                z = random.gauss(pos[2], falloffDistance)

                point = Point(x, y, z)
                # Check Point Inside Mesh
                if point.insideMesh(self):
                    points.append(point)
                    progress.step()
                    i += 1
                    if loc: cmds.xform(cmds.spaceLocator(), ws=1, a=1, t=[x, y, z])

                if breakCount > 100000: break
                breakCount += 1

        progress.close()
        return points
        '''
        edges = cmds.ls(cmds.polyListComponentConversion(te=1), fl=1)
        edge = edges[0]
        for edge in edges:
            verts = cmds.ls(cmds.polyListComponentConversion(edge, tv=1), fl=1)
            A = cmds.xform(verts[0], q=1, ws=1, t=1)
            B = cmds.xform(verts[1], q=1, ws=1, t=1)
            pointA = Vector(A[0], A[1], A[2])
            pointB = Vector(B[0], B[1], B[2])
            for i in range(countPerEdge):
                newPoint = pointA + (pointA-pointB/(countPerEdge+1.0)*i)
                cmds.xform(cmds.spaceLocator(), ws=1, a=1, t=[newPoint.x, newPoint.y, newPoint.z])

        '''

        return uvPoints

    def pointsCurve(self, count, curveShape, falloffDistance, seed=0, loc=0):
        # Variables
        breakCount = 0
        distances = []
        points = []

        # Create Progress Bar
        progress = ProgressBar('Creating Points', count)

        for i in range(100):
            distance = cmds.getAttr(curveShape + '.spans') / 100.0
            position = cmds.pointOnCurve(curveShape, pr=distance * i)
            point = Point(position[0], position[1], position[2])
            if point.insideMesh(self):
                distances.append(distance * i)

        startDistance = distances[0]
        endDistance = distances[-1]

        while i < count:
            position = cmds.pointOnCurve(curveShape, pr=startDistance + i * (endDistance - startDistance) / count)
            x = random.uniform(-falloffDistance, falloffDistance)
            y = random.uniform(-falloffDistance, falloffDistance)
            z = random.uniform(-falloffDistance, falloffDistance)

            point = Point(position.x + x, position.y + y, position.z + z)

            # Check Point Inside Mesh
            if point.insideMesh(self):
                points.append(point)
                progress.step()
                i += 1
                if loc: cmds.xform(cmds.spaceLocator(), ws=1, a=1, t=[x, y, z])

            if breakCount > 100000: break
            breakCount += 1

        progress.close()
        return points

    def meshHoneycomb(self, radius=2, crackWidth=0.001, uv=[2, 1], axis='y'):
        # Variables
        lowerBounds, upperBounds = self.getBounds()
        lowerBounds.z += radius * 0.5
        center = (lowerBounds + upperBounds) * 0.5
        height = upperBounds.y - lowerBounds.y + 0.1
        fractureMeshes = []
        x = lowerBounds.x
        i = 0

        while x < upperBounds.x + radius:
            z = lowerBounds.z
            if i % 2 != 0:
                z += -radius + (radius * 0.134)

            while z < upperBounds.z + radius:
                cylinder = cmds.polyCylinder(r=radius - (crackWidth * 0.5774), h=height, ch=0, sx=6)[0]
                cmds.xform(cylinder, ws=1, a=1, t=[x, center.y, z])
                fractureMeshes.append(Mesh(cylinder))
                z += radius * 0.866 * 2
            x += radius * 1.5
            i += 1

        # Offset UVs
        for fractureMesh in fractureMeshes:
            fractureMesh.offsetUV(uv)

        return fractureMeshes

    def meshBrick(self, brickWidth=4, brickHeight=2, mortarThickness=0.1, crackWidth=0.001, uv=[2, 1], buf=0.1,
                  axis='y'):
        # Variables
        lowerBounds, upperBounds = self.getBounds()
        center = (lowerBounds + upperBounds) * 0.5
        brickDepth = upperBounds.y - lowerBounds.y + buf * 2
        lowerBounds -= buf
        upperBounds += buf
        fractureMeshes = []
        x = lowerBounds.x
        y = lowerBounds.y

        i = 0
        while y < upperBounds.y:
            x = lowerBounds.x
            j = 0

            if i % 2 == 0:
                if (i / 2) % 2 != 0:
                    x -= brickWidth / 2.0

                while x < upperBounds.x:
                    # Create Brick
                    if j % 2 == 0:
                        cube = cmds.polyCube(h=brickHeight, w=brickWidth, d=brickDepth, ch=0)[0]
                        cmds.xform(cube, ws=1, a=1, t=[x + brickWidth * 0.5, y + brickHeight * 0.5, center.z])
                        x += brickWidth + crackWidth

                    # Create Mortar
                    else:
                        cube = cmds.polyCube(h=brickHeight, w=mortarThickness, d=brickDepth, ch=0)[0]
                        cmds.xform(cube, ws=1, a=1, t=[x + mortarThickness * 0.5, y + brickHeight * 0.5, center.z])
                        x += brickWidth + crackWidth

                fractureMeshes.append(Mesh(cube))
                y += brickHeight + crackWidth
                j += 1

            # Vertical Mortar
            else:
                cube = cmds.polyCube(h=mortarThickness, w=upperBounds.x - lowerBounds.x + buf * 2, d=brickDepth, ch=0)[
                    0]
                cmds.xform(cube, ws=1, a=1, t=[center.x, y + mortarThickness * 0.5, center.z])
                fractureMeshes.append(Mesh(cube))
                y += mortarThickness + crackWidth
            i += 1

        # Offset UVs
        for fractureMesh in fractureMeshes:
            fractureMesh.offsetUV(uv)

        return fractureMeshes


class MeshAPI(object):

    def __init__(self, name):
        self.name = name
        self.dag = self.getDag()
        self.mobj = self.getMObject()

    def __repr__(self):
        return self.name

    def getDag(self):
        meshList = om.MSelectionList()
        meshList.add(self.name)
        item = meshList.getDagPath(0)
        return om.MFnMesh(item.child(0))

    def getMObject(self):
        meshList = om.MSelectionList()
        meshList.add(self.name)
        item = meshList.getDagPath(0)
        return om.MObject(item.child(0))

    def getBoundingBox(self):
        ''' Return as 2 Vectors '''
        bbox = self.dag.boundingBox
        return Vector(bbox.min.x, bbox.min.y, bbox.min.z), Vector(bbox.max.x, bbox.max.y, bbox.max.z)

    def createBoundingCube(self, buf=1.01):
        ''' Create Cube Around Mesh and Return Cube as Mesh '''

        lowerBounds, upperBounds = self.getBoundingBox()
        position = (lowerBounds + upperBounds) / 2.0
        dimentions = (upperBounds - lowerBounds) * buf

        # Create Point Coordinates
        points = om.MFloatPointArray()
        points.append(om.MFloatPoint(position.x - dimentions.x * 0.5, position.y - dimentions.y * 0.5,
                                     position.z + dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x + dimentions.x * 0.5, position.y - dimentions.y * 0.5,
                                     position.z + dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x - dimentions.x * 0.5, position.y + dimentions.y * 0.5,
                                     position.z + dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x + dimentions.x * 0.5, position.y + dimentions.y * 0.5,
                                     position.z + dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x - dimentions.x * 0.5, position.y + dimentions.y * 0.5,
                                     position.z - dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x + dimentions.x * 0.5, position.y + dimentions.y * 0.5,
                                     position.z - dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x - dimentions.x * 0.5, position.y - dimentions.y * 0.5,
                                     position.z - dimentions.z * 0.5))
        points.append(om.MFloatPoint(position.x + dimentions.x * 0.5, position.y - dimentions.y * 0.5,
                                     position.z - dimentions.z * 0.5))

        # Create Face Counts
        faceConnects = om.MIntArray()
        faceConnectsArray = [0, 1, 7, 6, 0, 1, 3, 2, 3, 5, 4, 2, 5, 7, 6, 4, 0, 2, 4, 6, 7, 5, 3, 1]
        for x in faceConnectsArray:
            faceConnects.append(x)

        # Create Face Counts
        faceCounts = om.MIntArray()
        for x in range(0, 6):
            faceCounts.append(4)

        # Create Output Mesh
        outputMesh = om.MObject()
        meshFS = om.MFnMesh()
        newMesh = meshFS.create(8, 6, points, faceCounts, faceConnects, outputMesh)
        meshFS.updateSurface()
        nodeName = meshFS.name()


class UI(QtGui.QDialog):
    def __init__(self):
        self.parent = wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget)
        QtGui.QDialog.__init__(self, self.parent)

        self.createUI()
        self.createConnections()
        self.show()

    def createUI(self):

        # Window
        self.setWindowTitle('Fracture Tools')
        self.setFixedSize(275, 350)
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowMinMaxButtonsHint)

        # Fracture Type
        fractureTypes = ['Uniform', 'Wood', 'Irregular', 'Brick', 'Honeycomb']
        fractureTypeText = QtGui.QLabel('Fracture Type ')
        fractureTypeText.setAlignment(QtCore.Qt.AlignRight)
        fractureTypeText.setMargin(3)
        fractureTypeText.setFixedWidth(100)
        self.fractureTypeUI = QtGui.QComboBox()
        self.fractureTypeUI.addItems(fractureTypes)
        self.fractureTypeUI.setFixedWidth(150)

        self.fractureTypeLayout = QtGui.QHBoxLayout()
        self.fractureTypeLayout.addWidget(fractureTypeText)
        self.fractureTypeLayout.addWidget(self.fractureTypeUI)

        # Axis
        axisText = QtGui.QLabel('Axis ')
        axisText.setAlignment(QtCore.Qt.AlignRight)
        axisText.setMargin(3)
        axisText.setFixedWidth(100)

        self.axisXUI = QtGui.QRadioButton('X')
        self.axisYUI = QtGui.QRadioButton('Y')
        self.axisZUI = QtGui.QRadioButton('Z')
        self.axisXUI.setChecked(1)
        self.axisXUI.setFixedWidth(50)
        self.axisYUI.setFixedWidth(50)
        self.axisZUI.setFixedWidth(50)

        axisLayout = QtGui.QHBoxLayout()
        axisLayout.addWidget(axisText)
        axisLayout.addWidget(self.axisXUI)
        axisLayout.addWidget(self.axisYUI)
        axisLayout.addWidget(self.axisZUI)

        # Fractures
        fracturesText = QtGui.QLabel('Fractures ')
        fracturesText.setAlignment(QtCore.Qt.AlignRight)
        fracturesText.setMargin(3)
        fracturesText.setFixedWidth(100)
        self.fracturesCountUI = QtGui.QSpinBox()
        self.fracturesCountUI.setFixedWidth(150)
        self.fracturesCountUI.setMaximum(1000)
        self.fracturesCountUI.setValue(50)

        fracturesLayout = QtGui.QHBoxLayout()
        fracturesLayout.addWidget(fracturesText)
        fracturesLayout.addWidget(self.fracturesCountUI)

        # Crack Width
        crackWidthText = QtGui.QLabel('Crack Width ')
        crackWidthText.setAlignment(QtCore.Qt.AlignRight)
        crackWidthText.setMargin(3)
        crackWidthText.setFixedWidth(100)
        self.crackWidthUI = QtGui.QDoubleSpinBox()
        self.crackWidthUI.setFixedWidth(150)
        self.crackWidthUI.setMaximum(100000000)
        self.crackWidthUI.setMinimum(-10)
        self.crackWidthUI.setDecimals(4)
        self.crackWidthUI.setValue(0.0010)

        crackWidthLayout = QtGui.QHBoxLayout()
        crackWidthLayout.addWidget(crackWidthText)
        crackWidthLayout.addWidget(self.crackWidthUI)

        # Initial Point Count
        initialPointCountText = QtGui.QLabel('Initial Point Count ')
        initialPointCountText.setAlignment(QtCore.Qt.AlignRight)
        initialPointCountText.setMargin(3)
        initialPointCountText.setFixedWidth(100)
        self.initialPointCountUI = QtGui.QSpinBox()
        self.initialPointCountUI.setFixedWidth(150)
        self.initialPointCountUI.setMaximum(1000)
        self.initialPointCountUI.setValue(3)

        initialPointCountLayout = QtGui.QHBoxLayout()
        initialPointCountLayout.addWidget(initialPointCountText)
        initialPointCountLayout.addWidget(self.initialPointCountUI)

        # Falloff Distance
        falloffDistanceText = QtGui.QLabel('Falloff Distance ')
        falloffDistanceText.setAlignment(QtCore.Qt.AlignRight)
        falloffDistanceText.setMargin(3)
        falloffDistanceText.setFixedWidth(100)
        self.falloffDistanceUI = QtGui.QDoubleSpinBox()
        self.falloffDistanceUI.setFixedWidth(150)
        self.falloffDistanceUI.setMaximum(100000000)
        self.falloffDistanceUI.setDecimals(4)

        falloffDistanceLayout = QtGui.QHBoxLayout()
        falloffDistanceLayout.addWidget(falloffDistanceText)
        falloffDistanceLayout.addWidget(self.falloffDistanceUI)

        # Falloff Sharpness
        falloffSharpnessText = QtGui.QLabel('Falloff Sharpness ')
        falloffSharpnessText.setAlignment(QtCore.Qt.AlignRight)
        falloffSharpnessText.setMargin(3)
        falloffSharpnessText.setFixedWidth(100)
        self.falloffSharpnessUI = QtGui.QSpinBox()
        self.falloffSharpnessUI.setFixedWidth(150)
        self.falloffSharpnessUI.setMaximum(100)
        self.falloffSharpnessUI.setValue(4)

        falloffSharpnessLayout = QtGui.QHBoxLayout()
        falloffSharpnessLayout.addWidget(falloffSharpnessText)
        falloffSharpnessLayout.addWidget(self.falloffSharpnessUI)

        # Radius
        radiusText = QtGui.QLabel('Radius ')
        radiusText.setAlignment(QtCore.Qt.AlignRight)
        radiusText.setMargin(3)
        radiusText.setFixedWidth(100)
        self.radiusUI = QtGui.QDoubleSpinBox()
        self.radiusUI.setFixedWidth(150)
        self.radiusUI.setMaximum(100000000)
        self.radiusUI.setDecimals(4)
        self.radiusUI.setValue(2)

        radiusLayout = QtGui.QHBoxLayout()
        radiusLayout.addWidget(radiusText)
        radiusLayout.addWidget(self.radiusUI)

        # Brick Dimensions
        brickDimensionsText = QtGui.QLabel('Brick Width / Height ')
        brickDimensionsText.setAlignment(QtCore.Qt.AlignRight)
        brickDimensionsText.setMargin(3)
        brickDimensionsText.setFixedWidth(100)
        self.brickWidthUI = QtGui.QDoubleSpinBox()
        self.brickHeightUI = QtGui.QDoubleSpinBox()
        self.brickWidthUI.setMaximum(100000000)
        self.brickHeightUI.setMaximum(100000000)
        self.brickWidthUI.setDecimals(4)
        self.brickHeightUI.setDecimals(4)
        self.brickWidthUI.setFixedWidth(74)
        self.brickHeightUI.setFixedWidth(75)
        self.brickWidthUI.setValue(4)
        self.brickHeightUI.setValue(2)

        brickLayout = QtGui.QHBoxLayout()
        brickLayout.addWidget(brickDimensionsText)
        brickLayout.addWidget(self.brickWidthUI)
        brickLayout.addWidget(self.brickHeightUI)

        # Mortar Thickness
        mortarThicknessText = QtGui.QLabel('Mortar Thickness ')
        mortarThicknessText.setAlignment(QtCore.Qt.AlignRight)
        mortarThicknessText.setMargin(3)
        mortarThicknessText.setFixedWidth(100)
        self.mortarThicknessUI = QtGui.QDoubleSpinBox()
        self.mortarThicknessUI.setFixedWidth(150)
        self.mortarThicknessUI.setMaximum(100000000)
        self.mortarThicknessUI.setDecimals(4)
        self.mortarThicknessUI.setValue(0.1)

        mortarThicknessLayout = QtGui.QHBoxLayout()
        mortarThicknessLayout.addWidget(mortarThicknessText)
        mortarThicknessLayout.addWidget(self.mortarThicknessUI)

        # UV Position
        uvPositionText = QtGui.QLabel('UV Position ')
        uvPositionText.setAlignment(QtCore.Qt.AlignRight)
        uvPositionText.setMargin(3)
        uvPositionText.setFixedWidth(100)
        self.uUI = QtGui.QSpinBox()
        self.vUI = QtGui.QSpinBox()
        self.uUI.setFixedWidth(73)
        self.vUI.setFixedWidth(74)
        self.uUI.setValue(2)
        self.vUI.setValue(1)

        uvPositionLayout = QtGui.QHBoxLayout()
        uvPositionLayout.addWidget(uvPositionText)
        uvPositionLayout.addWidget(self.uUI)
        uvPositionLayout.addWidget(self.vUI)

        # Mesh Occlusion
        meshOcclusionButton = QtGui.QPushButton('Mesh Occlusion')
        meshOcclusionButton.setFixedWidth(100)
        self.meshOcclusionUI = QtGui.QLineEdit()
        self.meshOcclusionUI.setFixedWidth(150)

        meshOcclusionLayout = QtGui.QHBoxLayout()
        meshOcclusionLayout.addWidget(meshOcclusionButton)
        meshOcclusionLayout.addWidget(self.meshOcclusionUI)

        # Divider
        hLine = QtGui.QFrame()
        hLine.setFrameShape(QtGui.QFrame.HLine)
        hLine.setFrameShadow(QtGui.QFrame.Sunken)

        # Assign Shader
        shaderList = ['None', 'surfaceShader', 'lambert', 'mia_x_passes', 'VRay_Mtl', 'aiStandard', 'aiUtility']
        assignShaderText = QtGui.QLabel('Assign Shader ')
        assignShaderText.setAlignment(QtCore.Qt.AlignRight)
        assignShaderText.setMargin(3)
        assignShaderText.setFixedWidth(100)
        self.assignShaderUI = QtGui.QComboBox()
        self.assignShaderUI.addItems(shaderList)
        self.assignShaderUI.setFixedWidth(150)

        assignShaderLayout = QtGui.QHBoxLayout()
        assignShaderLayout.addWidget(assignShaderText)
        assignShaderLayout.addWidget(self.assignShaderUI)

        # Spacer
        spacerUI = QtGui.QSpacerItem(0, 15)

        # Fracture Button
        self.fractureButton = QtGui.QPushButton('Fracture')

        # Info Bar
        self.infoBarUI = QtGui.QLabel('')
        self.infoBarUI.setAutoFillBackground(1)
        self.infoBarUI.setStyleSheet('QLabel { background-color: rgba(20,20,20);}')
        self.infoBarUI.setAlignment(QtCore.Qt.AlignCenter)

        # Main Layout
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(3)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.mainLayout.addLayout(self.fractureTypeLayout)
        self.mainLayout.addLayout(axisLayout)
        self.mainLayout.addLayout(fracturesLayout)
        self.mainLayout.addLayout(crackWidthLayout)
        self.mainLayout.addLayout(initialPointCountLayout)
        self.mainLayout.addLayout(falloffDistanceLayout)
        self.mainLayout.addLayout(falloffSharpnessLayout)
        self.mainLayout.addLayout(radiusLayout)
        self.mainLayout.addLayout(brickLayout)
        self.mainLayout.addLayout(mortarThicknessLayout)
        self.mainLayout.addLayout(meshOcclusionLayout)

        self.mainLayout.addWidget(hLine)
        self.mainLayout.addLayout(uvPositionLayout)
        self.mainLayout.addLayout(assignShaderLayout)

        self.mainLayout.addSpacerItem(spacerUI)
        self.mainLayout.addWidget(self.fractureButton)
        self.mainLayout.addWidget(self.infoBarUI)
        self.setLayout(self.mainLayout)

    def createConnections(self):
        self.fractureButton.clicked.connect(self.execute)

    def initVars(self):
        # General Variables
        self.fractureMeshes = []
        self.fractureType = self.fractureTypeUI.currentText()
        self.fracturesCount = self.fracturesCountUI.value()
        self.crackWidth = self.crackWidthUI.value()
        self.initialPointCount = self.initialPointCountUI.value()
        self.falloffDistance = self.falloffDistanceUI.value()
        self.falloffSharpness = self.falloffSharpnessUI.value() + 1
        self.fracturesPerEdge = 3
        self.uv = [self.uUI.value(), self.vUI.value()]
        if self.axisXUI.isChecked(): self.axis = 'x'
        if self.axisYUI.isChecked(): self.axis = 'y'
        if self.axisZUI.isChecked(): self.axis = 'z'

        # Mesh Based Variables
        self.radius = self.radiusUI.value()
        self.brickWidth = self.brickWidthUI.value()
        self.brickHeight = self.brickHeightUI.value()
        self.mortarThickness = self.mortarThicknessUI.value()

        # Troubleshooting Variables
        self.loc = False
        self.seed = True
        self.cutFaces = True
        self.refresh = 1

    def execute(self):
        # Initialize
        self.selection = cmds.ls(sl=1)
        if not self.checkSelection(): return 0
        self.timer(1)
        cmds.undoInfo(state=0)
        self.initVars()

        for mesh in self.meshes:
            # Wireframe
            mesh.wireframe(1)

            # Group
            self.group = mesh.duplicate(mesh.name + '_Fractures')
            self.group.wireframe(0)
            self.group.deleteShape()

            # Point Based
            if self.fractureType == 'Uniform' or self.fractureType == 'Wood' or self.fractureType == 'Irregular' or self.fractureType == 'Curve' or self.fractureType == 'Texture' or self.fractureType == 'Particles':
                self.pointBased(mesh)

            # Mesh Based
            if self.fractureType == 'Honeycomb' or self.fractureType == 'Brick':
                self.meshBased(mesh)

        self.cleanup(mesh)

    def pointBased(self, mesh, points=0):

        if points == 0:
            # Create Points
            if self.fractureType == 'Uniform':
                points = mesh.pointsUniform(self.fracturesCount, self.falloffDistance, self.falloffSharpness,
                                            seed=self.seed, loc=self.loc)

            if self.fractureType == 'Wood':
                mesh.woodScale(self.axis)
                points = mesh.pointsUniform(self.fracturesCount, self.falloffDistance, self.falloffSharpness,
                                            seed=self.seed, loc=self.loc)
                mesh.woodScale(self.axis, inverse=1)

            if self.fractureType == 'Irregular':
                points = mesh.pointsIrregular(self.fracturesCount, self.falloffDistance, self.initialPointCount,
                                              self.falloffSharpness, seed=self.seed, loc=self.loc)

            if self.fractureType == 'Cracks':
                points = mesh.pointsCracks(self.fracturesPerEdge, self.falloffDistance, self.uv, seed=0, loc=0)

            if self.fractureType == 'Curve':
                points = mesh.pointsCurve(self.fracturesCount, self.curveShape, self.falloffDistance, loc=1)

        # Loop Through Points
        count = 1
        self.progress = ProgressBar('Fracturing', self.fracturesCount)
        for pointA in points:
            # Cancel Button
            if self.progress.stop == 1:
                self.cleanup(mesh)
                return 0

            # Create Bounding Cube
            boundingCube = mesh.createBoundingCube()
            boundingCube.offsetUV(self.uv)
            if self.fractureType == 'Wood': boundingCube.woodScale(self.axis)

            # Loop Through Points
            for pointB in points:
                if pointA != pointB:
                    boundingCube.trimFaces(pointA, pointB, self.crackWidth, self.cutFaces)

            if self.fractureType == 'Wood': boundingCube.woodScale(self.axis, inverse=1)

            # Fracture
            fracture = mesh.boolean(boundingCube, mesh.name + '_f_' + str(count))
            cmds.parent(fracture.name, self.group.name)
            if self.refresh: cmds.refresh()
            self.progress.step()
            count += 1

    def meshBased(self, mesh):
        # Honeycomb
        if self.fractureType == 'Honeycomb':
            fractureMeshes = mesh.meshHoneycomb(radius=self.radius,
                                                crackWidth=self.crackWidth,
                                                uv=self.uv,
                                                axis=self.axis)

        # Brick
        if self.fractureType == 'Brick':
            fractureMeshes = mesh.meshBrick(brickWidth=self.brickWidth,
                                            brickHeight=self.brickHeight,
                                            mortarThickness=self.mortarThickness,
                                            crackWidth=self.crackWidth,
                                            uv=self.uv,
                                            axis=self.axis)

        # Progress Bar
        self.progress = ProgressBar('Fracturing', len(fractureMeshes))

        # Fracture
        for fractureMesh in fractureMeshes:

            # Cancel Button
            if self.progress.stop == 1:
                self.cleanup(mesh)
                return 0

            fracture = mesh.boolean(fractureMesh, mesh.name)
            cmds.parent(fracture.name, self.group.name)
            if self.refresh: cmds.refresh()
            self.progress.step()

    def checkSelection(self):
        # No Selection
        if len(self.selection) == 0:
            sys.stderr.write('Must select object(s) to fracture')
            return 0

        # Curve Check
        if self.fractureTypeUI.currentText() == 'Curve':
            if cmds.nodeType(cmds.listRelatives(self.selection[-1], s=1)[0]) != 'nurbsCurve':
                sys.stderr.write('Last selection must be a curve')
                return 0
            else:
                self.curveShape = cmds.listRelatives(self.selection[-1], s=1)[0]
                self.selection.pop()

        # Mesh Check
        for select in self.selection:
            if cmds.nodeType(cmds.listRelatives(select)[0]) != 'mesh':
                sys.stderr.write('Selection must be a mesh')
                return 0

        # Convert to Meshes
        self.meshes = []
        for mesh in self.selection:
            self.meshes.append(Mesh(mesh))
        return 1

    def timer(self, function):
        if function:
            self.startTime = time.clock()
        else:
            self.endTime = time.clock()
            self.elapsedTime = str(round(abs(self.startTime - self.endTime), 2))

    def cleanup(self, mesh):
        self.progress.close()
        mesh.wireframe(0)
        mesh.hide()
        cmds.select(self.group.name, r=1)
        cmds.undoInfo(state=1)
        self.timer(0)
        self.infoBarUI.setText('Time: %s secs' % self.elapsedTime)


def main():
    ui = UI()


if __name__ == '__main__':
    main()