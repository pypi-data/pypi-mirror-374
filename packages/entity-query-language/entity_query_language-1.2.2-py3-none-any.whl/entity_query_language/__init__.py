__version__ = "1.2.2"

import logging

logger = logging.Logger("eql")
logger.setLevel(logging.INFO)

from .entity import (entity, an, let, the, set_of,
                     and_, or_, not_, contains, in_,
                     symbolic_mode, symbol, predicate,
                     alternative, refinement)
from .failures import MultipleSolutionFound

