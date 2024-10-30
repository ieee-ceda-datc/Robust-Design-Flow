# This script was written and developed by ABKGroup students at UCSD. However, the underlying commands and reports are copyrighted by Cadence. 
# We thank Cadence for granting permission to share our research to help promote and foster the next generation of innovators.
# lib and lef, RC setup

set lefdir "../../../../nangate45/lef"
set libdir "../../../../nangate45/lib"


set lefs "
    ${lefdir}/NangateOpenCellLibrary.tech.lef \
    ${lefdir}/NangateOpenCellLibrary.macro.lef \
    ${lefdir}/fakeram45_256x34.lef \
    ${lefdir}/fakeram45_64x21.lef \
    ${lefdir}/fakeram45_2048x39.lef \
    "

set libworst "
    ${libdir}/NangateOpenCellLibrary_typical.lib \
    ${libdir}/fakeram45_256x34.lib \
    ${libdir}/fakeram45_64x21.lib \
    ${libdir}/fakeram45_2048x39.lib \
    "

