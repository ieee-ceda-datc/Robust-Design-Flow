# This script was written and developed by ABKGroup students at UCSD. However, the underlying commands and reports are copyrighted by Cadence. 
# We thank Cadence for granting permission to share our research to help promote and foster the next generation of innovators.

set netlist_dir "../../../../swerv_wrapper"

set design swerv_wrapper
set DESIGN $design
set top_design swerv_wrapper
 
set netlist "${netlist_dir}/syn/1_synth.v"
set sdc "${netlist_dir}/syn/1_synth.sdc"
set def "${netlist_dir}/def/fplan.def"
