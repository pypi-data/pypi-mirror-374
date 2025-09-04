#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 09:01:11 2025
@author: Žiga Štancar

Script for parsing TGLF DUMP data files for all JETTO radial grid points and
extracting information on the transport parameter space, and plotting it. This
is useful when using TGLFNN, in orderto compare the parameter space of our
simulations versus the TGLFNN model domain.

Input: list of jetto run folders with TGLF DUMP files, and list of output
TGLF quantities (designed to match the TGLFNN model domain shown in
https://git.ccfe.ac.uk/tran/tglfnn-jet/-/tree/master/MultiMachineHyper_1Aug25)

Output: Dictionary of TGLF parameter values for all specified JETTO runs and
all JETTO grid points + summary graph showing dependence of individual TGLF
parameters on the JETTO grid points.
"""

import numpy as np
from os import listdir
from collections import defaultdict
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 11})

####################
# DUMP FILE READ FUNCTION
def read(files, search):
    parameter = []
    value = []

    with open(files) as file:
        lines = file.readlines()
        for line in lines:
            if any([phrase for phrase in search if phrase in line]):
                print(line)
                line = line.split(sep='=')
                parameter.append(str(line[0])[1:])
                value.append(float(line[1]))
    return parameter, value
####################
# PARSING TGLF DUMP FILE

TGLFNN_quantities = ['RLNS_1', 'RLTS_1', 'RLTS_2', 'TAUS_2', 'RMIN_LOC',
                     'DRMAJDX_LOC', 'Q_LOC', 'Q_PRIME_LOC', 'XNUE', 'KAPPA_LOC',
                     'DELTA_LOC', 'ZEFF', 'VEXB_SHEAR'] # List of relevant quantity names
jetto_list = ['/common/cmg/zstancar/jetto/runs/run_jet/96482/96482_tglf_Zeff_BgB04_V08/'] # List of JETTO-TGLF runs with dump files

# Extracting information from TGLF dump files
localdumpfiles = defaultdict(lambda: defaultdict(dict))
TGLF_DUMP = defaultdict(lambda: defaultdict(dict))
for file in jetto_list:
    localdumpfiles[file] = [f for f in listdir(file) if f[13:] == 'localdump']
    for dumpfile in localdumpfiles[file]:
        TGLF_DUMP[file]['parameters'][int(dumpfile[:3])], TGLF_DUMP[file]['values'][int(dumpfile[:3])] = read(file+dumpfile, TGLFNN_quantities)

# Calculating S_HAT via extracted quantities
for file in jetto_list:
    localdumpfiles[file] = [f for f in listdir(file) if f[13:] == 'localdump']
    for dumpfile in localdumpfiles[file]:
        TGLF_DUMP[file]['parameters'][int(dumpfile[:3])].append('SHAT')
        TGLF_DUMP[file]['values'][int(dumpfile[:3])].append(
                TGLF_DUMP[file]['values'][int(dumpfile[:3])][TGLF_DUMP[file]['parameters'][1].index('Q_PRIME_LOC')] / \
                (TGLF_DUMP[file]['values'][int(dumpfile[:3])][TGLF_DUMP[file]['parameters'][1].index('Q_LOC')] / \
                 TGLF_DUMP[file]['values'][int(dumpfile[:3])][TGLF_DUMP[file]['parameters'][1].index('RMIN_LOC')])**2)
        
#################
# PLOTTING PARAMETER SPACE for each JETTO-TGLF run

TGLFNN_plot = ['RLNS_1', 'RLTS_1', 'RLTS_2', 'TAUS_2', 'RMIN_LOC',
                     'DRMAJDX_LOC', 'Q_LOC', 'SHAT', 'XNUE', 'KAPPA_LOC',
                     'DELTA_LOC', 'ZEFF', 'VEXB_SHEAR'] # List of relevant quantity names for plotting

ncol = 3
nrow = int(np.ceil(len(TGLFNN_plot)/ncol))
position = range(1,len(TGLFNN_plot) + 1)

for file in jetto_list:
    fig = plt.figure(1)
    for k in range(len(TGLFNN_plot)):
        ax = fig.add_subplot(nrow,ncol,position[k])
        for i in range(len(localdumpfiles[file])):
            ax.scatter(i+1, TGLF_DUMP[file]['values'][i+1][TGLF_DUMP[file]['parameters'][1].index(TGLFNN_plot[k])], color = 'k')
        ax.set_title(TGLFNN_plot[k]+' (JETTO grid)')
    fig.set_size_inches(10.5, 10.5)
    fig.subplots_adjust(hspace=0.5, wspace=0.3)
    fig.suptitle('TGLF parameter space for JETTO run' + '\n' + file)
plt.show()
