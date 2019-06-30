"""Simple utility that spherizes mesh

"""
import pymel.core as pm
import math


class Spherize(object):

    def spherize(self, radius=10):

        offset = pm.xform(self.getParent(), q=1, rp=1, ws=1)
        for i in range(pm.polyEvaluate(self, v=1)):
            pos = pm.xform('{0}.vtx[{1}]'.format(self.name(), i), q=1, ws=1, t=1)
            pos = [pos[0] - offset[0], pos[1] - offset[1], pos[2] - offset[2]]
            mult = radius / math.sqrt(sum(j ** 2 for j in pos))
            new_pos = [pos[0] * mult, pos[1] * mult, pos[2] * mult]
            new_pos = [new_pos[0] + offset[0], new_pos[1] + offset[1], new_pos[2] + offset[2]]
            pm.xform('{0}.vtx[{1}]'.format(self.name(), i), ws=1, t=new_pos)
