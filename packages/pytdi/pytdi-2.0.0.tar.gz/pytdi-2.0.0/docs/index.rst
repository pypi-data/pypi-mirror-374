.. PyTDI documentation master file, created by
   sphinx-quickstart on Tue Dec 21 16:59:29 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyTDI
=====

PyTDI is a Python package that provides a toolset to perform symbolical and numerical
time-delay interferometry (TDI) calculations. It can be used to define arbitrary linear combination
of time-shifted signals (i.e., combinations), symbolically handle these combinations, and numerically
evaluate these combinations against data.

PyTDI also provides ready-to-use standard TDI combinations for the LISA mission.

Refer to the following sections to get started.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   quickstart
   lisa-conventions

.. toctree::
   :maxdepth: 2
   :caption: Reference

   standard-combinations
   tdi-combination
   clock-noise-correction
   interface
   dsp

.. toctree::
   :maxdepth: 1
   :caption: Others

   Gitlab project page <https://gitlab.in2p3.fr/LISA/LDPG/wg6_inrep/pytdi>
   legal
