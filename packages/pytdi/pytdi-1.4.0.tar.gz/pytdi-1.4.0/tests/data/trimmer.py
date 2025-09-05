#
# Copyright 2021, by the Max Planck Institute for Gravitational Physics
# (Albert Einstein Institute). ALL RIGHTS RESERVED.
#
"""
Trimmer dor LISANode data.

This script takes HDF5 data produced by LISANode and removes unnecessary datasets.
"""

import sys

import h5py

KEEP_KEYS = [
    "ranging1",
    "ranging1_p",
    "ranging2",
    "ranging2_p",
    "ranging3",
    "ranging3_p",
    "s_c_fluctuations1",
    "s_c_fluctuations1_p",
    "s_c_fluctuations2",
    "s_c_fluctuations2_p",
    "s_c_fluctuations3",
    "s_c_fluctuations3_p",
    "tm_c_fluctuations1",
    "tm_c_fluctuations1_p",
    "tm_c_fluctuations2",
    "tm_c_fluctuations2_p",
    "tm_c_fluctuations3",
    "tm_c_fluctuations3_p",
    "ref_c_fluctuations1",
    "ref_c_fluctuations1_p",
    "ref_c_fluctuations2",
    "ref_c_fluctuations2_p",
    "ref_c_fluctuations3",
    "ref_c_fluctuations3_p",
]
LENGTH = 400000


if __name__ == "__main__":
    path_in = str(sys.argv[1])
    path_out = str(sys.argv[2])
    with h5py.File(path_in, "r") as hdf5_in, h5py.File(path_out, "w") as hdf5_out:
        for key in hdf5_in:
            if key in KEEP_KEYS:
                hdf5_out.create_dataset(key, data=hdf5_in[key][-LENGTH:])
