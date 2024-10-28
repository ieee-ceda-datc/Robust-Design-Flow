#!/bin/bash
# This script was written and developed by ABKGroup students at UCSD. However,
# the underlying commands and reports are copyrighted by Cadence. 
# We thank Cadence for granting permission to share our research to help promote
# and foster the next generation of innovators.

module unload genus
module load genus/21.1
module unload innovus
module load innovus/21.1

## Grep the project directory
export project_dir=`pwd | grep -o '/\S*ProxyEnablement'`

# To run the Physical Synthesis (iSpatial) flow - flow2
export PHY_SYNTH=0
export clock_period=$1
export utility=$2
export lib_directory=$3
export Cscale=$4
export Rscale=$5

mkdir log -p
genus -overwrite -log log/genus.log -no_gui -files run_genus_hybrid.tcl
innovus -64 -overwrite -log log/innovus.log -files run_invs.tcl
