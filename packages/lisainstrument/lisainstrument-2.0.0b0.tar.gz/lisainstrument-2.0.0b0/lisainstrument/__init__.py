# -*- coding: utf-8 -*-
"""LISA Instrument module."""

import importlib

from .glitches import glitch_file
from .gwsource import gw_file
from .instru import SimResultFile
from .instrument import Instrument
from .orbiting import MosaID, SatID, orbit_file
from .streams import SchedulerConfigParallel, SchedulerConfigSerial

# Automatically set by `poetry dynamic-versioning`
__version__ = "2.0.0-beta"


try:
    metadata = importlib.metadata.metadata("lisainstrument").json
    __author__ = metadata["author"]
    __email__ = metadata["author_email"]
except importlib.metadata.PackageNotFoundError:
    pass
