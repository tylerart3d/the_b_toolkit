import pymel.core as pm
from pymel.all import factories

# Virtual Classes
from core.mesh import TMesh

# Logger
from core import log_tools


def initialize():

    # Setup logger
    logger = log_tools.logger('t_toolkit')

    # Setup virtual classes
    factories.registerVirtualClass(TMesh, nameRequired=False)
    logger.info("Registered virtual classes")

    # Setup command port
    if not pm.commandPort(':4434', q=True):
        pm.commandPort(n=':4434')


initialize()
