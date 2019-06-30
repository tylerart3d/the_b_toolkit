from pymel.all import factories
from core.mesh import TMesh
import pymel.core as pm

factories.registerVirtualClass(TMesh, nameRequired=False)
