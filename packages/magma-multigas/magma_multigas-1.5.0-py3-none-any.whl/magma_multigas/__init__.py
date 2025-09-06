#!/usr/bin/env python
# -*- coding: utf-8 -*-

from magma_multigas.multigas import MultiGas
from magma_multigas.multigas_data import MultiGasData
from magma_multigas.diagnose import Diagnose
from magma_multigas.diagnose import Query
from magma_multigas.resources import columns_description
from magma_multigas.plot_availability import PlotAvailability
from magma_multigas.plot_wind_direction import PlotWindDirection
from magma_multigas.plot_var import PlotWithMagma
from magma_multigas.validator import STATUSES

from pkg_resources import get_distribution

__version__ = get_distribution("magma-multigas").version
__author__ = "Martanto"
__author_email__ = "martanto@LIVE.COM"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024, Martanto"
__url__ = "https://github.com/martanto/magma-multigas"

__all__ = [
    "MultiGas",
    "MultiGasData",
    "Diagnose",
    "Query",
    "columns_description",
    "STATUSES",
    "PlotAvailability",
    "PlotWindDirection",
    "PlotWithMagma",
]
