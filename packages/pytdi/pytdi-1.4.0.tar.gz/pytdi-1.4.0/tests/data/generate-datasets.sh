#!/bin/sh
#
# BSD 3-Clause License
#
# Copyright (c) 2022, California Institute of Technology and
# Max Planck Institute for Gravitational Physics (Albert Einstein Institute)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# This software may be subject to U.S. export control laws. By accepting this
# software, the user agrees to comply with all applicable U.S. export laws and
# regulations. User has the responsibility to obtain export licenses, or other
# export authority as may be required before exporting such information to
# foreign countries or providing access to foreign persons.
#
#
# Dataset created from LISANode (e8f1faa64276cd38344f188b5a1a780a08fc6756).
#
# 1. Please checkout the correct version before executing this file.
#   git checkout e8f1faa64276cd38344f188b5a1a780a08fc6756
#
# 2. In 'config.py', set
#         LISA_MEASUREMENT_FS = 3.2
#         LISA_LOCKING_SCHEME = None
#
# 3. In 'config.py', set LISA_ORBIT_TYPE = 'polynomial_tt', and execute
# lisanode run --build -O2 lisanode:LISA && mv LISA LISA-static && rm LISA.cpp
#
# 4. In 'config.py', set LISA_ORBIT_TYPE = 'keplerian', and execute
# lisanode run --build -O2 lisanode:LISA && mv LISA LISA-keplerian && rm LISA.cpp
#
# 5. In 'config.py', set LISA_ORBIT_TYPE = 'keplerian', LISA_SIMULATE_DOPPLER = True, and execute
# lisanode run --build -O2 lisanode:LISA && mv LISA LISA-keplerian-doppler && rm LISA.cpp
#
# 6. Execute this file


# Parameters

SIM_DURATION=4E5

# Run 3 free-running lasers, only laser noise, static orbits

./LISA-static -d $SIM_DURATION --accelnoise-on-off=0 --readoutnoise-on-off=0 --obpathlengthnoise-on-off=0 --backlinknoise-on-off=0 --usonoise-on-off=0 --rangingnoise-on-off=0 --modulationnoise-on-off=0 --telescopenoise-on-off=0 --polynomial-tt-order=0 --laser-seed1=1 --laser-seed1-p=1 --laser-seed2=2 --laser-seed2-p=2 --laser-seed3=3 --laser-seed3-p=3 --print-time=0 -o "lisa-threelasers-lasernoise-staticorbits.h5"
python trimmer.py lisa-threelasers-lasernoise-staticorbits.h5 lisa-threelasers-lasernoise-staticorbits-trimmed.h5
mv lisa-threelasers-lasernoise-staticorbits-trimmed.h5 lisa-threelasers-lasernoise-staticorbits.h5

# Run 6 free-running lasers, only laser noise, static orbits

./LISA-static -d $SIM_DURATION --accelnoise-on-off=0 --readoutnoise-on-off=0 --obpathlengthnoise-on-off=0 --backlinknoise-on-off=0 --usonoise-on-off=0 --rangingnoise-on-off=0 --modulationnoise-on-off=0 --telescopenoise-on-off=0 --polynomial-tt-order=0 --laser-seed1=1 --laser-seed1-p=4 --laser-seed2=2 --laser-seed2-p=5 --laser-seed3=3 --laser-seed3-p=6 --print-time=0 -o "lisa-sixlasers-lasernoise-staticorbits.h5"
python trimmer.py lisa-sixlasers-lasernoise-staticorbits.h5 lisa-sixlasers-lasernoise-staticorbits-trimmed.h5
mv lisa-sixlasers-lasernoise-staticorbits-trimmed.h5 lisa-sixlasers-lasernoise-staticorbits.h5

# Run 6 free-running lasers, only laser noise, Keplerian orbits

./LISA-keplerian -d $SIM_DURATION --accelnoise-on-off=0 --readoutnoise-on-off=0 --obpathlengthnoise-on-off=0 --backlinknoise-on-off=0 --usonoise-on-off=0 --rangingnoise-on-off=0 --modulationnoise-on-off=0 --telescopenoise-on-off=0 --laser-seed1=1 --laser-seed1-p=4 --laser-seed2=2 --laser-seed2-p=5 --laser-seed3=3 --laser-seed3-p=6 --print-time=0 -o "lisa-sixlasers-lasernoise-keplerianorbits.h5"
python trimmer.py lisa-sixlasers-lasernoise-keplerianorbits.h5 lisa-sixlasers-lasernoise-keplerianorbits-trimmed.h5
mv lisa-sixlasers-lasernoise-keplerianorbits-trimmed.h5 lisa-sixlasers-lasernoise-keplerianorbits.h5

# Run 6 free-running lasers, only laser noise, Keplerian orbits, Doppler shifts

./LISA-keplerian-doppler -d $SIM_DURATION --accelnoise-on-off=0 --readoutnoise-on-off=0 --obpathlengthnoise-on-off=0 --backlinknoise-on-off=0 --usonoise-on-off=0 --rangingnoise-on-off=0 --modulationnoise-on-off=0 --telescopenoise-on-off=0 --laser-seed1=1 --laser-seed1-p=4 --laser-seed2=2 --laser-seed2-p=5 --laser-seed3=3 --laser-seed3-p=6 --print-time=0 -o "lisa-sixlasers-lasernoise-keplerianorbits-doppler.h5"
python trimmer.py lisa-sixlasers-lasernoise-keplerianorbits-doppler.h5 lisa-sixlasers-lasernoise-keplerianorbits-doppler-trimmed.h5
mv lisa-sixlasers-lasernoise-keplerianorbits-doppler-trimmed.h5 lisa-sixlasers-lasernoise-keplerianorbits-doppler.h5
