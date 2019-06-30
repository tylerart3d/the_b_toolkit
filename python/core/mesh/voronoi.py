import maya.OpenMaya as om
from core import log_tools
from random import uniform, seed
import pymel.core as pm
import raycast

logger = log_tools.logger(__name__)


class Voronoi(object, raycast.Raycast):


    def voronoi_fracture(self, type='uniform'):
        pass

    def generate_points_uniform(self, count, seed=0):
        bounding_box = pm.selected()[0].boundingBox()
        points = [[uniform(bounding_box[0][i], bounding_box[1][i]) for i in range(3)] for j in range(count)]
        logger.info(points)




'''
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
    return points'''