"""
Time Profiler
=============

The tm_profiler module for time profiling of functions

+---------------+--------------------------------------------+
| GitHub        | https://github.com/NorchaHack/tm_profiler  |
+---------------+--------------------------------------------+
| Pypi          | https://pypi.org/project/tm_profiler       |
+---------------+--------------------------------------------+


Installation
============

Releases of :py:mod:`tm_profiler` can be installed
using pip

.. code:: bash

    pip install tm_profiler

Time Profiler Basic Usage
=========================

............

"""

# __submodules__ = [
#     'tm_profiler',
#     'ipython_extension',
# ]
#
# __autogen__ = """
# mkinit ./tm_profiler/__init__.py --relative
# mkinit ./tm_profiler/__init__.py --relative -w
# """

from .tm_profiler import (profile, print_stat, print_table, print_last,
                          set_output_dec, set_output_name_format,
                          FuncNameFormat, log_time_enabled)


__all__ = [
    "profile",
    # "sum_by_pairs_to_file",
    # "sum_file_total",
    # "read_numbers_from_text_file",
    # "set_parse_float",
    # "set_max_number",
    # "set_min_number",
    # "reset_to_default",
]

__author__ = "Normunds Pureklis <norchahack@gmail.com>"
__status__ = "development"
__version__ = "0.0.2"
__date__ = "05 Sep 2025"
